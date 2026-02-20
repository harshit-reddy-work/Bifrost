"""
Interactive Database Shell for CloudRoom
Run this script to access the database interactively.
"""
from app import create_app
from models import db, User, Project, Event, Team, Club, StudentChapter, Registration, TeamJoinRequest, TeamInvite

app = create_app()

with app.app_context():
    print("=" * 60)
    print("CloudRoom Database Shell")
    print("=" * 60)
    print("\nAvailable models:")
    print("  - User")
    print("  - Project")
    print("  - Event")
    print("  - Team")
    print("  - Club")
    print("  - StudentChapter")
    print("  - Registration")
    print("  - TeamJoinRequest")
    print("  - TeamInvite")
    print("\nDatabase: db")
    print("=" * 60)
    print("\nExample queries:")
    print("  User.query.all()                    # Get all users")
    print("  User.query.filter_by(email='...').first()  # Find user by email")
    print("  Project.query.count()               # Count projects")
    print("  db.session.query(User).count()     # Count users")
    print("\nType 'exit()' to quit")
    print("=" * 60)
    print()
    
    # Start interactive shell
    import code
    code.interact(local=dict(globals(), **locals()))
