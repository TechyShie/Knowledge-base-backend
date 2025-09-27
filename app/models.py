from datetime import datetime
from . import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="viewer")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    articles = db.relationship(
        "Article",
        back_populates="author",
        cascade="all, delete-orphan"
    )
    # New relationship for feedback (if user is logged in)
    feedback_entries = db.relationship("Feedback", back_populates="user")

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))
    articles = db.relationship(
        "Article",
        back_populates="category",
        cascade="all, delete-orphan"
    )

class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Article(db.Model):
    __tablename__ = "articles"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)

    author = db.relationship("User", back_populates="articles")
    category = db.relationship("Category", back_populates="articles")
    
    # New relationships for secondary tables
    tags = db.relationship(
        "Tag", 
        secondary="article_tags", 
        back_populates="articles",
        cascade="all, delete"
    )
    feedback_entries = db.relationship(
        "Feedback", 
        back_populates="article",
        cascade="all, delete-orphan"
    )

# Join table for many-to-many relationship between Articles and Tags
# In models.py - cleaner ArticleTag model
class ArticleTag(db.Model):
    __tablename__ = "article_tags"
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Remove these relationships - they're redundant with the many-to-many
    # article = db.relationship("Article", backref="article_tag_associations")
    # tag = db.relationship("Tag", backref="article_tag_associations")
    
    __table_args__ = (db.UniqueConstraint('article_id', 'tag_id', name='unique_article_tag'),)

    
class Feedback(db.Model):
    __tablename__ = "feedback"
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)  # nullable for anonymous feedback
    helpfulness_score = db.Column(db.Integer, nullable=False)  # 1-5 scale or 0/1 for like/dislike
    comment = db.Column(db.Text)  # Optional comment field
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    article = db.relationship("Article", back_populates="feedback_entries")
    user = db.relationship("User", back_populates="feedback_entries")

# Add back-populates to Tag model
Tag.articles = db.relationship(
    "Article", 
    secondary="article_tags", 
    back_populates="tags"
)