"""
Create default forum categories
"""
from app import create_app
from models import db, ForumCategory

app = create_app()

with app.app_context():
    print("Creating default forum categories...")
    
    categories = [
        ("General", "General discussions"),
        ("Questions", "Ask questions and get help"),
        ("Projects", "Share your projects"),
        ("Events", "Discuss events and competitions"),
        ("Announcements", "Important announcements"),
        ("Tech", "Technology discussions"),
        ("Study", "Study groups and resources"),
        ("Hackathons", "Hackathon discussions"),
    ]
    
    created = 0
    for name, description in categories:
        existing = ForumCategory.query.filter_by(name=name).first()
        if not existing:
            cat = ForumCategory(name=name, description=description)
            db.session.add(cat)
            created += 1
            print(f"Created category: {name}")
        else:
            print(f"Category already exists: {name}")
    
    db.session.commit()
    print(f"\n[SUCCESS] Created {created} new categories!")
