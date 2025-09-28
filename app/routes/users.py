from flask import Blueprint, jsonify, request
from app.models import User, Article
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity  # NEW

users_bp = Blueprint('users', __name__)

# NEW: Firebase sync endpoint
@users_bp.route('/firebase-sync', methods=['POST'])
def sync_firebase_user():
    try:
        data = request.get_json()
        
        # Required fields from Firebase
        firebase_uid = data.get('firebase_uid')
        email = data.get('email')
        username = data.get('username')
        
        if not firebase_uid or not email:
            return jsonify({'error': 'Firebase UID and email are required'}), 400
        
        # Check if user already exists by Firebase UID
        user = User.query.filter_by(firebase_uid=firebase_uid).first()
        
        if user:
            # User exists, return their data
            access_token = create_access_token(identity=user.id)
            return jsonify({
                'message': 'User synced successfully',
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role
                }
            }), 200
        
        # Check if user exists by email (for existing users)
        user = User.query.filter_by(email=email).first()
        if user:
            # Link Firebase UID to existing user
            user.firebase_uid = firebase_uid
            db.session.commit()
        else:
            # Create new user from Firebase data
            if not username:
                # Generate username from email
                username = email.split('@')[0]
            
            # Ensure username is unique
            base_username = username
            counter = 1
            while User.query.filter_by(username=username).first():
                username = f"{base_username}{counter}"
                counter += 1
            
            new_user = User(
                username=username,
                email=email,
                firebase_uid=firebase_uid,
                password_hash='firebase_auth',  # Dummy value
                role='employee'
            )
            db.session.add(new_user)
            db.session.commit()
            user = new_user
        
        # Create JWT token for your backend
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'User synced successfully',
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# NEW: Get user profile (protected)
@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'firebase_uid': user.firebase_uid
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# GET all users (admin only)
@users_bp.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'article_count': len(user.articles),
                'created_at': user.created_at.isoformat()
            })
        
        return jsonify(users_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# GET single user by ID
@users_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'created_at': user.created_at.isoformat(),
            'articles': [
                {
                    'id': article.id,
                    'title': article.title,
                    'category': article.category.name,
                    'created_at': article.created_at.isoformat()
                } for article in user.articles
            ]
        }
        
        return jsonify(user_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# POST register new user (keep for non-Firebase registration)
@users_bp.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        
        # Validation
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Username, email, and password are required'}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
            
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new user
        new_user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            role=data.get('role', 'employee')
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email,
                'role': new_user.role
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# POST login user (keep for non-Firebase login)
@users_bp.route('/login', methods=['POST'])
def login_user():
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not check_password_hash(user.password_hash, data['password']):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Create JWT token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# PUT update user profile
@users_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        if 'username' in data:
            existing_user = User.query.filter_by(username=data['username']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'error': 'Username already taken'}), 400
            user.username = data['username']
        
        if 'email' in data:
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'error': 'Email already taken'}), 400
            user.email = data['email']
        
        if 'password' in data:
            user.password_hash = generate_password_hash(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500