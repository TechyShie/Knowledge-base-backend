from flask import Blueprint, jsonify, request
from app.models import Feedback, Article, User
from app import db
from datetime import datetime

feedback_bp = Blueprint('feedback', __name__)

# GET all feedback for an article (admin/moderator view)
@feedback_bp.route('/articles/<int:article_id>/feedback', methods=['GET'])
def get_article_feedback(article_id):
    try:
        # Verify article exists
        article = Article.query.get_or_404(article_id)
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        feedback_query = Feedback.query.filter_by(article_id=article_id)
        
        # Filter by helpfulness score if provided
        min_score = request.args.get('min_score', type=int)
        if min_score is not None:
            feedback_query = feedback_query.filter(Feedback.helpfulness_score >= min_score)
        
        feedback = feedback_query.order_by(Feedback.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        feedback_data = []
        for entry in feedback.items:
            feedback_entry = {
                'id': entry.id,
                'helpfulness_score': entry.helpfulness_score,
                'comment': entry.comment,
                'created_at': entry.created_at.isoformat(),
                'is_anonymous': entry.user_id is None
            }
            
            # Include username if not anonymous
            if entry.user_id:
                feedback_entry['user'] = {
                    'id': entry.user.id,
                    'username': entry.user.username
                }
            
            feedback_data.append(feedback_entry)
        
        # Calculate article feedback statistics
        total_feedback = Feedback.query.filter_by(article_id=article_id).count()
        avg_score = db.session.query(db.func.avg(Feedback.helpfulness_score))\
                            .filter_by(article_id=article_id)\
                            .scalar() or 0
        
        return jsonify({
            'article': {
                'id': article.id,
                'title': article.title
            },
            'feedback': feedback_data,
            'statistics': {
                'total_feedback': total_feedback,
                'average_score': round(float(avg_score), 2),
                'positive_feedback': Feedback.query.filter(
                    Feedback.article_id == article_id,
                    Feedback.helpfulness_score >= 4
                ).count()
            },
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': feedback.total,
                'pages': feedback.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# POST submit feedback for an article
@feedback_bp.route('/articles/<int:article_id>/feedback', methods=['POST'])
def submit_feedback(article_id):
    try:
        # Verify article exists
        article = Article.query.get_or_404(article_id)
        
        data = request.get_json()
        
        # Validation
        if not data or data.get('helpfulness_score') is None:
            return jsonify({'error': 'Helpfulness score is required'}), 400
        
        score = data['helpfulness_score']
        if not isinstance(score, int) or score < 1 or score > 5:
            return jsonify({'error': 'Helpfulness score must be between 1 and 5'}), 400
        
        # Check if user has already submitted feedback for this article
        user_id = data.get('user_id')  # Can be None for anonymous feedback
        
        if user_id:
            existing_feedback = Feedback.query.filter_by(
                article_id=article_id, 
                user_id=user_id
            ).first()
            
            if existing_feedback:
                return jsonify({
                    'error': 'You have already submitted feedback for this article',
                    'existing_feedback_id': existing_feedback.id
                }), 400
        
        # Create new feedback
        new_feedback = Feedback(
            article_id=article_id,
            user_id=user_id,  # None for anonymous
            helpfulness_score=score,
            comment=data.get('comment', '').strip()
        )
        
        db.session.add(new_feedback)
        db.session.commit()
        
        response_data = {
            'message': 'Feedback submitted successfully',
            'feedback_id': new_feedback.id,
            'article_id': article_id,
            'helpfulness_score': score,
            'is_anonymous': user_id is None
        }
        
        if user_id:
            response_data['user_id'] = user_id
        
        return jsonify(response_data), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# GET feedback summary for an article (public view)
@feedback_bp.route('/articles/<int:article_id>/feedback/summary', methods=['GET'])
def get_feedback_summary(article_id):
    try:
        # Verify article exists
        article = Article.query.get_or_404(article_id)
        
        # Calculate statistics
        total_feedback = Feedback.query.filter_by(article_id=article_id).count()
        
        if total_feedback == 0:
            return jsonify({
                'article_id': article_id,
                'total_feedback': 0,
                'average_score': 0,
                'score_breakdown': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                'message': 'No feedback yet'
            }), 200
        
        avg_score = db.session.query(db.func.avg(Feedback.helpfulness_score))\
                            .filter_by(article_id=article_id)\
                            .scalar()
        
        # Get score breakdown
        score_breakdown = {}
        for score in range(1, 6):
            count = Feedback.query.filter_by(
                article_id=article_id, 
                helpfulness_score=score
            ).count()
            score_breakdown[score] = count
        
        return jsonify({
            'article_id': article_id,
            'article_title': article.title,
            'total_feedback': total_feedback,
            'average_score': round(float(avg_score), 2),
            'score_breakdown': score_breakdown,
            'positive_percentage': round(
                (score_breakdown[4] + score_breakdown[5]) / total_feedback * 100, 
                2
            )
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# GET user's feedback history (requires authentication later)
@feedback_bp.route('/users/<int:user_id>/feedback', methods=['GET'])
def get_user_feedback(user_id):
    try:
        user = User.query.get_or_404(user_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        feedback = Feedback.query.filter_by(user_id=user_id)\
                               .order_by(Feedback.created_at.desc())\
                               .paginate(page=page, per_page=per_page, error_out=False)
        
        feedback_data = []
        for entry in feedback.items:
            feedback_data.append({
                'id': entry.id,
                'article': {
                    'id': entry.article.id,
                    'title': entry.article.title,
                    'category': entry.article.category.name
                },
                'helpfulness_score': entry.helpfulness_score,
                'comment': entry.comment,
                'created_at': entry.created_at.isoformat()
            })
        
        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username
            },
            'feedback': feedback_data,
            'total_feedback': feedback.total,
            'page': page,
            'per_page': per_page,
            'pages': feedback.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# DELETE feedback (admin/moderator function)
@feedback_bp.route('/feedback/<int:feedback_id>', methods=['DELETE'])
def delete_feedback(feedback_id):
    try:
        feedback = Feedback.query.get_or_404(feedback_id)
        
        db.session.delete(feedback)
        db.session.commit()
        
        return jsonify({
            'message': 'Feedback deleted successfully',
            'deleted_feedback_id': feedback_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500