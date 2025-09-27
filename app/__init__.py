from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS  # Make sure this is imported

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    if os.environ.get('DATABASE_URL'):
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///knowledge_base.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # ✅ FIX: Configure CORS properly
    CORS(app, resources={
        r"/*": {
            "origins": [
                "http://localhost:5173",  # Vite dev server
                "http://127.0.0.1:5173",   # Alternative localhost
                "https://knowledge-base-backend-hg1e.onrender.com"  # Your own domain
            ],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # ... rest of your code