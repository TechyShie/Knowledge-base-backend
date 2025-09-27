from flask import Blueprint, jsonify
from app.models import Category

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/categories', methods=['GET'])
def get_categories():
    try:
        categories = Category.query.all()
        
        categories_data = []
        for category in categories:
            categories_data.append({
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'article_count': len(category.articles)
            })
        
        return jsonify(categories_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500