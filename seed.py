# seed.py
from app import create_app, db
from app.models import User, Category, Article, Tag, ArticleTag, Feedback
from datetime import datetime

app = create_app()

with app.app_context():
    # ⚠️ Drop + recreate = nukes all data (only for dev/test)
    db.drop_all()
    db.create_all()

    # --- Users ---
    user1 = User(username="alice", email="alice@example.com", password_hash="hashed_pw1", role="admin")
    user2 = User(username="bob", email="bob@example.com", password_hash="hashed_pw2", role="editor")
    user3 = User(username="charlie", email="charlie@example.com", password_hash="hashed_pw3", role="viewer")

    # --- Categories ---
    cat1 = Category(name="Python", description="All about Python programming")
    cat2 = Category(name="Flask", description="Guides and tutorials on Flask framework")
    cat3 = Category(name="Database", description="Database management and ORM")

    # Add users and categories first to get IDs
    db.session.add_all([user1, user2, user3, cat1, cat2, cat3])
    db.session.commit()

    # --- Articles ---
    art1 = Article(
        title="Getting Started with Python",
        content="Python is a versatile programming language...",
        author_id=user1.id,
        category_id=cat1.id
    )

    art2 = Article(
        title="Flask for Beginners",
        content="Flask is a lightweight WSGI web application framework...",
        author_id=user2.id,
        category_id=cat2.id
    )

    art3 = Article(
        title="SQLAlchemy Basics",
        content="SQLAlchemy is a powerful ORM for Python...",
        author_id=user1.id,
        category_id=cat3.id
    )

    db.session.add_all([art1, art2, art3])
    db.session.commit()

    # --- Tags ---
    tag1 = Tag(name="beginner")
    tag2 = Tag(name="advanced")
    tag3 = Tag(name="tutorial")
    tag4 = Tag(name="database")
    tag5 = Tag(name="web")
    tag6 = Tag(name="orm")

    db.session.add_all([tag1, tag2, tag3, tag4, tag5, tag6])
    db.session.commit()

    # --- Article-Tag Relationships (SIMPLIFIED approach) ---
    # Instead of using constructors, assign directly using IDs
    relationships = [
        ArticleTag(article_id=art1.id, tag_id=tag1.id),
        ArticleTag(article_id=art1.id, tag_id=tag3.id),
        ArticleTag(article_id=art2.id, tag_id=tag1.id),
        ArticleTag(article_id=art2.id, tag_id=tag3.id),
        ArticleTag(article_id=art2.id, tag_id=tag5.id),
        ArticleTag(article_id=art3.id, tag_id=tag4.id),
        ArticleTag(article_id=art3.id, tag_id=tag6.id),
        ArticleTag(article_id=art3.id, tag_id=tag2.id)
    ]

    # --- Feedback ---
    feedback_entries = [
        Feedback(
            article_id=art1.id,
            user_id=user3.id,
            helpfulness_score=5,
            comment="Very helpful for beginners!"
        ),
        Feedback(
            article_id=art1.id,
            user_id=None,  # Anonymous feedback
            helpfulness_score=4,
            comment="Good introduction"
        ),
        Feedback(
            article_id=art2.id,
            user_id=user3.id,
            helpfulness_score=3,
            comment="Could use more examples"
        )
    ]

    db.session.add_all(relationships)
    db.session.add_all(feedback_entries)
    db.session.commit()

    print("✅ Database seeded successfully!")
    print(f"📊 Created: 3 users, 3 categories, 3 articles, 6 tags, 8 tag relationships, 3 feedback entries")
    
    # Display sample data verification
    print("\n📝 Sample Article with Tags:")
    sample_article = Article.query.first()
    print(f"Article: {sample_article.title}")
    print(f"Tags: {[tag.name for tag in sample_article.tags]}")
    
    print("\n🏷️ All Tags:")
    tags = Tag.query.all()
    for tag in tags:
        article_count = Article.query.join(ArticleTag).filter(ArticleTag.tag_id == tag.id).count()
        print(f"- {tag.name} ({article_count} articles)")