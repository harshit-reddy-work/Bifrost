"""
Script to create an admin user or promote an existing user to admin.
Run this script to set up admin access.
"""
from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    print("=" * 60)
    print("Admin User Setup")
    print("=" * 60)
    
    # Check if is_admin column exists, if not, add it
    try:
        # Try to query is_admin to check if column exists
        User.query.first()
        print("[OK] Database schema is up to date")
    except Exception as e:
        print(f"[WARNING] Database schema needs update: {e}")
        print("Please run database migration or recreate tables.")
    
    print("\nOptions:")
    print("1. Create a new admin user")
    print("2. Promote an existing user to admin")
    print("3. List all admin users")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        print("\n--- Create New Admin User ---")
        name = input("Name: ").strip()
        username = input("Username: ").strip()
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        
        if User.query.filter_by(email=email).first():
            print("[ERROR] Email already exists!")
        elif User.query.filter_by(username=username).first():
            print("[ERROR] Username already taken!")
        else:
            admin_user = User(
                name=name,
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print(f"[SUCCESS] Admin user '{username}' created successfully!")
    
    elif choice == "2":
        print("\n--- Promote Existing User to Admin ---")
        identifier = input("Enter username or email: ").strip()
        
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()
        
        if not user:
            print("[ERROR] User not found!")
        else:
            user.is_admin = True
            db.session.commit()
            print(f"[SUCCESS] User '{user.username}' is now an admin!")
    
    elif choice == "3":
        print("\n--- Admin Users ---")
        admins = User.query.filter_by(is_admin=True).all()
        if admins:
            for admin in admins:
                print(f"  - {admin.username} ({admin.email})")
        else:
            print("  No admin users found.")
    
    else:
        print("Invalid choice!")
    
    print("\n" + "=" * 60)
