from app import create_app
from models import db, User

app = create_app()

with app.app_context():
    user = User.query.first()
    if user:
        print(f"User model has is_admin attribute: {hasattr(user, 'is_admin')}")
        if hasattr(user, 'is_admin'):
            print(f"Current user is_admin value: {user.is_admin}")
    else:
        print("No users in database")
    
    # Check admin users
    admins = User.query.filter_by(is_admin=True).all()
    print(f"\nAdmin users found: {len(admins)}")
    for admin in admins:
        print(f"  - {admin.username} ({admin.email})")
