import os  # ← ADD THIS IMPORT
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    if os.environ.get('DATABASE_URL'):  # ← This line needs 'os' imported
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///knowledge_base.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # ✅ CORS Configuration
    CORS(app, resources={
        r"/*": {
            "origins": [
                "http://localhost:5173",
                "http://127.0.0.1:5173", 
                "https://knowledge-base-backend-hg1e.onrender.com"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
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