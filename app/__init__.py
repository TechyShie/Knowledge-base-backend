import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # === DATABASE CONFIGURATION (Works both locally and on Render) ===
    
    # Check if we're in production (Render provides DATABASE_URL)
    if os.environ.get('DATABASE_URL'):
        # Production - Use PostgreSQL on Render
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')
        print("🚀 Production mode: Using PostgreSQL database")
    else:
        # Development - Use SQLite locally
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///knowledge_base.db'
        print("💻 Development mode: Using SQLite database")
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # === SECRET KEY (Important for production) ===
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # CORS configuration - more restrictive in production
    if os.environ.get('FLASK_ENV') == 'production':
        CORS(app, origins=[os.environ.get('FRONTEND_URL', 'https://your-frontend-domain.com')])
    else:
        CORS(app)  # Allow all in development
    
    # === REGISTER BLUEPRINTS ===
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
    
    # === HEALTH CHECK ROUTE (Good for production) ===
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'API is running'}
    
    return app