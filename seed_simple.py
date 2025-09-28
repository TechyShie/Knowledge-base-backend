# seed_simple.py
from app import create_app, db
from app.models import User, Category, Article, Tag, ArticleTag, Feedback
from datetime import datetime
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # ⚠️ Drop + recreate = nukes all data (only for dev/test)
    db.drop_all()
    db.create_all()

    # --- Users ---
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
    cat1 = Category(name="Engineering", description="Technical documentation and development guides")
    cat2 = Category(name="Product", description="Product specifications and roadmaps")
    cat3 = Category(name="Marketing", description="Marketing strategies and campaigns")
    cat4 = Category(name="Sales", description="Sales processes and customer guides")
    cat5 = Category(name="HR", description="HR policies and employee resources")
    cat6 = Category(name="All Documents", description="Complete company knowledge base")

    # Add users and categories
    db.session.add_all([user1, user2, user3, user4, cat1, cat2, cat3, cat4, cat5, cat6])
    db.session.commit()

    # --- Articles --- (Simplified content)
    
    # Engineering
    eng1 = Article(
        title="Getting Started with Our Tech Stack",
        content="Learn about our technology stack including React, Flask, and PostgreSQL.",
        author_id=user1.id,
        category_id=cat1.id
    )

    eng2 = Article(
        title="API Documentation v2.1",
        content="Complete REST API documentation with authentication and endpoints.",
        author_id=user2.id,
        category_id=cat1.id
    )

    eng3 = Article(
        title="Database Schema Guide",
        content="Database schema documentation and relationships between tables.",
        author_id=user1.id,
        category_id=cat1.id
    )

    # Product
    prod1 = Article(
        title="Product Roadmap Q1 2024",
        content="Quarterly product roadmap with features and timelines.",
        author_id=user2.id,
        category_id=cat2.id
    )

    prod2 = Article(
        title="Feature Specification: Smart Search",
        content="AI-powered search feature specification and requirements.",
        author_id=user1.id,
        category_id=cat2.id
    )

    # Marketing
    marketing1 = Article(
        title="Brand Guidelines v3.0",
        content="Company brand guidelines including colors, fonts, and voice.",
        author_id=user4.id,
        category_id=cat3.id
    )

    marketing2 = Article(
        title="Q1 Marketing Campaign Plan",
        content="Marketing campaign plan with goals, channels, and budget.",
        author_id=user4.id,
        category_id=cat3.id
    )

    # Sales
    sales1 = Article(
        title="Sales Playbook: Enterprise Accounts",
        content="Enterprise sales playbook with processes and value propositions.",
        author_id=user3.id,
        category_id=cat4.id
    )

    # HR
    hr1 = Article(
        title="Employee Onboarding Checklist",
        content="Complete onboarding checklist for new employees.",
        author_id=user3.id,
        category_id=cat5.id
    )

    hr2 = Article(
        title="Remote Work Policy",
        content="Company remote work policy and guidelines.",
        author_id=user1.id,
        category_id=cat5.id
    )

    # Add all articles
    all_articles = [eng1, eng2, eng3, prod1, prod2, marketing1, marketing2, sales1, hr1, hr2]
    db.session.add_all(all_articles)
    db.session.commit()

    # --- Tags ---
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
    relationships = [
        # Engineering articles
        ArticleTag(article_id=eng1.id, tag_id=tags[0].id),
        ArticleTag(article_id=eng1.id, tag_id=tags[12].id),
        ArticleTag(article_id=eng1.id, tag_id=tags[13].id),
        
        ArticleTag(article_id=eng2.id, tag_id=tags[1].id),
        ArticleTag(article_id=eng2.id, tag_id=tags[2].id),
        ArticleTag(article_id=eng2.id, tag_id=tags[12].id),
        
        ArticleTag(article_id=eng3.id, tag_id=tags[3].id),
        ArticleTag(article_id=eng3.id, tag_id=tags[2].id),
        ArticleTag(article_id=eng3.id, tag_id=tags[13].id),
        
        # Product articles
        ArticleTag(article_id=prod1.id, tag_id=tags[4].id),
        ArticleTag(article_id=prod2.id, tag_id=tags[5].id),
        
        # Marketing articles  
        ArticleTag(article_id=marketing1.id, tag_id=tags[6].id),
        ArticleTag(article_id=marketing1.id, tag_id=tags[2].id),
        ArticleTag(article_id=marketing2.id, tag_id=tags[7].id),
        
        # Sales articles
        ArticleTag(article_id=sales1.id, tag_id=tags[8].id),
        ArticleTag(article_id=sales1.id, tag_id=tags[13].id),
        
        # HR articles
        ArticleTag(article_id=hr1.id, tag_id=tags[9].id),
        ArticleTag(article_id=hr1.id, tag_id=tags[13].id),
        ArticleTag(article_id=hr2.id, tag_id=tags[10].id),
        ArticleTag(article_id=hr2.id, tag_id=tags[11].id),
    ]

    # --- Feedback ---
    feedback_entries = [
        Feedback(
            article_id=eng1.id,
            user_id=user3.id,
            helpfulness_score=5,
            comment="Very helpful for new developers!"
        ),
        Feedback(
            article_id=hr1.id,
            user_id=user4.id,
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
    
    print("\n🏷️ Tags with Article Counts:")
    for tag in tags[:5]:  # Show first 5 tags
        article_count = Article.query.join(ArticleTag).filter(ArticleTag.tag_id == tag.id).count()
        print(f"- #{tag.name} ({article_count} articles)")