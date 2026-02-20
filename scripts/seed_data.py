# seed_data.py (safe, non-destructive)
from app import create_app
from models import db, User, Project, Event, Team
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    # Create tables if they don't exist
    db.create_all()

    # If users already exist, skip seeding
    if User.query.count() > 0:
        print("✅ Database already has users — skipping seeding.")
    else:
        print("🌱 Seeding demo data...")

        # Example demo users
        u1 = User(
            name="Alice",
            email="alice@university.edu",
            username="alice",
            password_hash=generate_password_hash("Passw0rd!")
        )
        u2 = User(
            name="Bob",
            email="bob@college.edu",
            username="bob",
            password_hash=generate_password_hash("Passw0rd!")
        )
        db.session.add_all([u1, u2])
        db.session.commit()

        # Example demo projects
        p1 = Project(
            title="Campus Map App",
            description="Find study groups and events easily on campus.",
            github="https://github.com/example/campus-map",
            owner=u1
        )
        p2 = Project(
            title="Hackathon Helper",
            description="Team formation and event tracker for students.",
            owner=u2
        )
        db.session.add_all([p1, p2])

        # Example demo events
        e1 = Event(
            title="Winter Hackathon",
            description="A 24-hour innovation challenge!",
            date=datetime.utcnow() + timedelta(days=10),
            location="Innovation Lab"
        )
        e2 = Event(
            title="AI Study Circle",
            description="Weekly machine learning discussions.",
            date=datetime.utcnow() + timedelta(days=3),
            location="Room 210"
        )
        db.session.add_all([e1, e2])

        db.session.commit()
        print("🌟 Seeding complete.")
