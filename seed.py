# seed.py (REPLACE your current seed.py with this EXACT code)
import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set database URI before importing Flask app
os.environ['DATABASE_URL'] = 'sqlite:///knowledge_base.db'

# Now import Flask and SQLAlchemy directly
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

# Create a minimal Flask app just for seeding
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///knowledge_base.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define models directly in this file (copy from your models.py but simplified)
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    firebase_uid = db.Column(db.String(128), unique=True, nullable=True)
    role = db.Column(db.String(20), default="employee")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))

class Article(db.Model):
    __tablename__ = "articles"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)

class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ArticleTag(db.Model):
    __tablename__ = "article_tags"
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Feedback(db.Model):
    __tablename__ = "feedback"
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    helpfulness_score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def seed_database():
    with app.app_context():
        # ⚠️ Drop + recreate = nukes all data (only for dev/test)
        print("🔄 Creating database tables...")
        db.drop_all()
        db.create_all()

        # --- Users ---
        print("👥 Creating users...")
        user1 = User(
            username="alice_dev", 
            email="alice@company.com", 
            password_hash=generate_password_hash("password123"),
            role="admin"
        )
        user2 = User(
            username="bob_engineer", 
            email="bob@company.com", 
            password_hash=generate_password_hash("password123"),
            role="editor"
        )
        user3 = User(
            username="charlie_hr", 
            email="charlie@company.com", 
            password_hash=generate_password_hash("password123"),
            role="employee"
        )
        user4 = User(
            username="diana_marketing", 
            email="diana@company.com", 
            password_hash=generate_password_hash("password123"),
            role="employee"
        )

        # --- Categories ---
        print("📂 Creating categories...")
        cat1 = Category(name="Engineering", description="Technical documentation and development guides")
        cat2 = Category(name="Product", description="Product specifications and roadmaps")
        cat3 = Category(name="Marketing", description="Marketing strategies and campaigns")
        cat4 = Category(name="Sales", description="Sales processes and customer guides")
        cat5 = Category(name="HR", description="HR policies and employee resources")
        cat6 = Category(name="All Documents", description="Complete company knowledge base")

        # Add users and categories
        db.session.add_all([user1, user2, user3, user4, cat1, cat2, cat3, cat4, cat5, cat6])
        db.session.commit()

        # --- Articles ---
        print("📝 Creating articles...")
        
        # Engineering
        eng1 = Article(
            title="Getting Started with Our Tech Stack",
            content="Learn about our technology stack including React, Flask, and PostgreSQL. This guide covers everything you need to know to start developing with our stack.",
            author_id=user1.id,
            category_id=cat1.id
        )

        eng2 = Article(
            title="API Documentation v2.1",
            content="Complete REST API documentation with authentication and endpoints. Learn how to integrate with our API services.",
            author_id=user2.id,
            category_id=cat1.id
        )

        eng3 = Article(
            title="Database Schema Guide",
            content="Database schema documentation and relationships between tables. Understand our data structure and relationships.",
            author_id=user1.id,
            category_id=cat1.id
        )

        # Product
        prod1 = Article(
            title="Product Roadmap Q1 2024",
            content="Quarterly product roadmap with features and timelines. See what's coming next in our product development.",
            author_id=user2.id,
            category_id=cat2.id
        )

        prod2 = Article(
            title="Feature Specification: Smart Search",
            content="AI-powered search feature specification and requirements. Learn about our new intelligent search capabilities.",
            author_id=user1.id,
            category_id=cat2.id
        )

        # Marketing
        marketing1 = Article(
            title="Brand Guidelines v3.0",
            content="Company brand guidelines including colors, fonts, and voice. Maintain consistent branding across all materials.",
            author_id=user4.id,
            category_id=cat3.id
        )

        marketing2 = Article(
            title="Q1 Marketing Campaign Plan",
            content="Marketing campaign plan with goals, channels, and budget. Execute successful marketing campaigns with this guide.",
            author_id=user4.id,
            category_id=cat3.id
        )

        # Sales
        sales1 = Article(
            title="Sales Playbook: Enterprise Accounts",
            content="Enterprise sales playbook with processes and value propositions. Close more enterprise deals with proven strategies.",
            author_id=user3.id,
            category_id=cat4.id
        )

        # HR
        hr1 = Article(
            title="Employee Onboarding Checklist",
            content="Complete onboarding checklist for new employees. Ensure smooth onboarding experiences for all new hires.",
            author_id=user3.id,
            category_id=cat5.id
        )

        hr2 = Article(
            title="Remote Work Policy",
            content="Company remote work policy and guidelines. Understand our remote work expectations and best practices.",
            author_id=user1.id,
            category_id=cat5.id
        )

        # Add all articles
        all_articles = [eng1, eng2, eng3, prod1, prod2, marketing1, marketing2, sales1, hr1, hr2]
        db.session.add_all(all_articles)
        db.session.commit()

        # --- Tags ---
        print("🏷️ Creating tags...")
        tags_data = [
            "getting-started", "api", "documentation", "database", 
            "roadmap", "feature", "brand", "campaign", "sales", "onboarding",
            "remote-work", "policy", "technical", "guide", "best-practices"
        ]
        
        tags = []
        for tag_name in tags_data:
            tag = Tag(name=tag_name)
            tags.append(tag)
        
        db.session.add_all(tags)
        db.session.commit()

        # --- Article-Tag Relationships ---
        print("🔗 Creating article-tag relationships...")
        relationships = [
            # Engineering articles
            ArticleTag(article_id=eng1.id, tag_id=1),  # getting-started
            ArticleTag(article_id=eng1.id, tag_id=13), # technical
            ArticleTag(article_id=eng1.id, tag_id=14), # guide
            
            ArticleTag(article_id=eng2.id, tag_id=2),  # api
            ArticleTag(article_id=eng2.id, tag_id=3),  # documentation
            ArticleTag(article_id=eng2.id, tag_id=13), # technical
            
            ArticleTag(article_id=eng3.id, tag_id=4),  # database
            ArticleTag(article_id=eng3.id, tag_id=3),  # documentation
            ArticleTag(article_id=eng3.id, tag_id=14), # guide
            
            # Product articles
            ArticleTag(article_id=prod1.id, tag_id=5), # roadmap
            ArticleTag(article_id=prod2.id, tag_id=6), # feature
            
            # Marketing articles  
            ArticleTag(article_id=marketing1.id, tag_id=7), # brand
            ArticleTag(article_id=marketing1.id, tag_id=3), # documentation
            ArticleTag(article_id=marketing2.id, tag_id=8), # campaign
            
            # Sales articles
            ArticleTag(article_id=sales1.id, tag_id=9), # sales
            ArticleTag(article_id=sales1.id, tag_id=14), # guide
            
            # HR articles
            ArticleTag(article_id=hr1.id, tag_id=10), # onboarding
            ArticleTag(article_id=hr1.id, tag_id=14), # guide
            ArticleTag(article_id=hr2.id, tag_id=11), # remote-work
            ArticleTag(article_id=hr2.id, tag_id=12), # policy
        ]

        # --- Feedback ---
        print("💬 Creating feedback...")
        feedback_entries = [
            Feedback(
                article_id=1,
                user_id=3,
                helpfulness_score=5,
                comment="Very helpful for new developers!"
            ),
            Feedback(
                article_id=9,
                user_id=4,
                helpfulness_score=4,
                comment="Great onboarding checklist."
            )
        ]

        db.session.add_all(relationships)
        db.session.add_all(feedback_entries)
        db.session.commit()

        print("✅ Database seeded successfully!")
        print(f"📊 Created: 4 users, 6 categories, {len(all_articles)} articles, {len(tags)} tags")
        
        # Display sample data verification
        print("\n📝 Articles by Category:")
        categories = Category.query.all()
        for category in categories:
            article_count = Article.query.filter_by(category_id=category.id).count()
            print(f"- {category.name}: {article_count} articles")
        
        print("\n🏷️ Sample Tags:")
        for tag in tags[:5]:
            article_count = Article.query.join(ArticleTag).filter(ArticleTag.tag_id == tag.id).count()
            print(f"- #{tag.name} ({article_count} articles)")

if __name__ == "__main__":
    seed_database()