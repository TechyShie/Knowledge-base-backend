from flask import Blueprint, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return jsonify({
        'message': 'Knowledge Base API is running!',
        'endpoints': {
            'articles': {
                'GET_all': '/articles',
                'GET_single': '/articles/1',
                'POST_create': '/articles (POST)',
                'PUT_update': '/articles/1 (PUT)',
                'DELETE': '/articles/1 (DELETE)',
                'by_tag': '/articles/tag/python'
            },
            'categories': '/categories',
            'tags': '/tags',
            'users': {
                'GET_all': '/users',
                'GET_single': '/users/1',
                'register': '/register (POST)',
                'login': '/login (POST)'
            },
            'feedback': {
                'GET_article_feedback': '/articles/1/feedback',
                'POST_feedback': '/articles/1/feedback (POST)',
                'GET_summary': '/articles/1/feedback/summary'
            }
        },
        'version': '1.0'
    })

@main_bp.route('/setup-database', methods=['POST'])
def setup_database():
    """One-time database setup route"""
    try:
        from app import db
        from app.models import User
        
        # Create all tables
        db.create_all()
        
        # Seed data
        from seed import seed_database
        seed_database()
        
        return jsonify({
            'message': 'Database setup completed successfully',
            'tables_created': True,
            'data_seeded': True
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500