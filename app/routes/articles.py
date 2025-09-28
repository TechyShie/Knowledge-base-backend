from flask import Blueprint, jsonify, request
from app.models import Article, Category, User, Tag
from app import db

articles_bp = Blueprint('articles', __name__)

# GET all articles with pagination and filtering
@articles_bp.route('/articles', methods=['GET'])
def get_articles():
    try:
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Filtering parameters
        category_id = request.args.get('category_id', type=int)
        tag_id = request.args.get('tag_id', type=int)
        author_id = request.args.get('author_id', type=int)
        search = request.args.get('search', type=str)
        
        # Base query
        query = Article.query
        
        # Apply filters
        if category_id:
            query = query.filter(Article.category_id == category_id)
        if author_id:
            query = query.filter(Article.author_id == author_id)
        if tag_id:
            query = query.join(Article.tags).filter(Tag.id == tag_id)
        if search:
            query = query.filter(
                db.or_(
                    Article.title.ilike(f'%{search}%'),
                    Article.content.ilike(f'%{search}%')
                )
            )
        
        # Get paginated results
        articles = query.order_by(Article.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Build response - UPDATED to match frontend expectations
        articles_data = []
        for article in articles.items:
            article_data = {
                'id': article.id,
                'title': article.title,
                'excerpt': article.content[:150] + '...' if len(article.content) > 150 else article.content,
                'content': article.content,  # Include full content for detail view
                'author': {
                    'id': article.author.id,
                    'username': article.author.username,
                    'email': article.author.email
                },
                'category': {
                    'id': article.category.id,
                    'name': article.category.name,
                    'description': article.category.description
                },
                'tags': [{'id': tag.id, 'name': tag.name} for tag in article.tags],
                'created_at': article.created_at.isoformat(),
                'updated_at': article.updated_at.isoformat()
            }
            articles_data.append(article_data)
        
        return jsonify({
            'articles': articles_data,
            'total': articles.total,
            'page': page,
            'per_page': per_page,
            'pages': articles.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# GET single article by ID with full details
@articles_bp.route('/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    try:
        article = Article.query.get_or_404(article_id)
        
        article_data = {
            'id': article.id,
            'title': article.title,
            'content': article.content,
            'author': {
                'id': article.author.id,
                'username': article.author.username,
                'email': article.author.email  # Include email for detailed view
            },
            'category': {
                'id': article.category.id,
                'name': article.category.name,
                'description': article.category.description
            },
            'tags': [{'id': tag.id, 'name': tag.name} for tag in article.tags],
            'created_at': article.created_at.isoformat(),
            'updated_at': article.updated_at.isoformat()
        }
        
        return jsonify(article_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# POST create new article
@articles_bp.route('/articles', methods=['POST'])
def create_article():
    try:
        data = request.get_json()
        
        # Basic validation
        if not data or not data.get('title') or not data.get('content'):
            return jsonify({'error': 'Title and content are required'}), 400
        
        # Validate author and category exist
        author = User.query.get(data.get('author_id', 1))
        if not author:
            return jsonify({'error': 'Author not found'}), 404
            
        category = Category.query.get(data.get('category_id', 1))
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        # Create new article
        new_article = Article(
            title=data['title'],
            content=data['content'],
            author_id=data.get('author_id', 1),
            category_id=data.get('category_id', 1)
        )
        
        db.session.add(new_article)
        db.session.commit()
        
        # Handle tags if provided
        if 'tag_ids' in data:
            for tag_id in data['tag_ids']:
                tag = Tag.query.get(tag_id)
                if tag:
                    new_article.tags.append(tag)
            db.session.commit()
        
        return jsonify({
            'message': 'Article created successfully',
            'article': {
                'id': new_article.id,
                'title': new_article.title,
                'author_id': new_article.author_id,
                'category_id': new_article.category_id,
                'tags': [{'id': tag.id, 'name': tag.name} for tag in new_article.tags]
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# PUT update existing article
@articles_bp.route('/articles/<int:article_id>', methods=['PUT'])
def update_article(article_id):
    try:
        article = Article.query.get_or_404(article_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields if provided
        if 'title' in data:
            article.title = data['title']
        if 'content' in data:
            article.content = data['content']
        if 'category_id' in data:
            category = Category.query.get(data['category_id'])
            if not category:
                return jsonify({'error': 'Category not found'}), 404
            article.category_id = data['category_id']
        
        # Update tags if provided
        if 'tag_ids' in data:
            article.tags.clear()  # Remove existing tags
            for tag_id in data['tag_ids']:
                tag = Tag.query.get(tag_id)
                if tag:
                    article.tags.append(tag)
        
        article.updated_at = db.func.now()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Article updated successfully',
            'article': {
                'id': article.id,
                'title': article.title,
                'content': article.content,
                'category_id': article.category_id,
                'tags': [{'id': tag.id, 'name': tag.name} for tag in article.tags],
                'updated_at': article.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# DELETE article
@articles_bp.route('/articles/<int:article_id>', methods=['DELETE'])
def delete_article(article_id):
    try:
        article = Article.query.get_or_404(article_id)
        
        db.session.delete(article)
        db.session.commit()
        
        return jsonify({
            'message': 'Article deleted successfully',
            'deleted_article_id': article_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# GET articles by tag
@articles_bp.route('/articles/tag/<string:tag_name>', methods=['GET'])
def get_articles_by_tag(tag_name):
    try:
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            return jsonify({'error': 'Tag not found'}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        articles = Article.query.join(Article.tags).filter(Tag.id == tag.id)\
                               .order_by(Article.created_at.desc())\
                               .paginate(page=page, per_page=per_page, error_out=False)
        
        articles_data = []
        for article in articles.items:
            articles_data.append({
                'id': article.id,
                'title': article.title,
                'excerpt': article.content[:100] + '...' if len(article.content) > 100 else article.content,
                'author': article.author.username,
                'category': article.category.name,
                'created_at': article.created_at.isoformat()
            })
        
        return jsonify({
            'tag': tag_name,
            'articles': articles_data,
            'total': articles.total,
            'page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500