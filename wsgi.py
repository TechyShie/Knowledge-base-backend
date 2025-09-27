# wsgi.py
from app import create_app, db
from app.models import User

app = create_app()

# Auto-create tables on startup
with app.app_context():
    try:
        # Try to query to see if tables exist
        User.query.first()
        print("✅ Database tables already exist")
    except:
        print("🔄 Creating database tables...")
        db.create_all()
        print("✅ Database tables created")
        
        # Seed initial data
        try:
            from seed import seed_database
            seed_database()
            print("✅ Database seeded successfully")
        except Exception as e:
            print(f"⚠️  Seeding failed: {e}")