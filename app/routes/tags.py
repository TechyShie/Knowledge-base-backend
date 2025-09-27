from flask import Blueprint, jsonify
from app.models import Tag

tags_bp = Blueprint('tags', __name__)

@tags_bp.route('/tags', methods=['GET'])
def get_tags():
    try:
        tags = Tag.query.all()
        
        tags_data = []
        for tag in tags:
            tags_data.append({
                'id': tag.id,
                'name': tag.name,
                'article_count': len(tag.articles)
            })
        
        return jsonify(tags_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500