import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager  # NEW
from datetime import timedelta  # NEW

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()  # NEW

def create_app():
    app = Flask(__name__)
    
    # Configuration
    if os.environ.get('DATABASE_URL'):
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///knowledge_base.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-super-secret-jwt-key-change-in-production')  # NEW
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)  # NEW
    
    # ✅ CORS Configuration
    CORS(app, resources={
        r"/*": {
            "origins": [
                "http://localhost:5173",
                "http://127.0.0.1:5173", 
                "https://knowledge-base-backend-hg1e.onrender.com",
                "http://localhost:3000",
                "http://127.0.0.1:3000"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)  # NEW
    
    # Register blueprints
    from app.routes.articles import articles_bp
    from app.routes.categories import categories_bp
    from app.routes.tags import tags_bp
    from app.routes.users import users_bp
    from app.routes.feedback import feedback_bp
    from app.routes.main import main_bp
    
    app.register_blueprint(articles_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(tags_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(main_bp)
    
    return app