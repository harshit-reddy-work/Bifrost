"""
Create the first admin user with username 'admin' and password 'admin'
"""
from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    print("=" * 60)
    print("Creating First Admin User")
    print("=" * 60)
    
    # Check if admin user already exists
    existing_admin = User.query.filter_by(username='admin').first()
    if existing_admin:
        if existing_admin.is_admin:
            print("[INFO] Admin user already exists and is an admin.")
            print(f"      Username: admin")
            print(f"      Email: {existing_admin.email}")
        else:
            # Promote existing user to admin
            existing_admin.is_admin = True
            existing_admin.password_hash = generate_password_hash('admin')
            db.session.commit()
            print("[SUCCESS] Existing user 'admin' promoted to admin!")
    else:
        # Check if email admin@admin.com exists
        existing_email = User.query.filter_by(email='admin@admin.com').first()
        if existing_email:
            print("[INFO] User with email admin@admin.com exists. Promoting to admin...")
            existing_email.is_admin = True
            existing_email.password_hash = generate_password_hash('admin')
            if not existing_email.username == 'admin':
                existing_email.username = 'admin'
            db.session.commit()
            print("[SUCCESS] User promoted to admin!")
        else:
            # Create new admin user
            admin_user = User(
                name='Administrator',
                username='admin',
                email='admin@admin.com',
                password_hash=generate_password_hash('admin'),
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("[SUCCESS] Admin user created successfully!")
            print("      Username: admin")
            print("      Password: admin")
            print("      Email: admin@admin.com")
    
    # Verify
    admin = User.query.filter_by(username='admin', is_admin=True).first()
    if admin:
        print("\n[VERIFIED] Admin user is ready!")
        print(f"      Login at: http://localhost:5000/admin/login")
    else:
        print("\n[ERROR] Failed to create admin user!")
    
    print("=" * 60)
