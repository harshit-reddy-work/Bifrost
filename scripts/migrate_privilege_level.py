"""
Migration script to add privilege_level column to user table.
Default privilege level is 4 (Student).
"""
from app import create_app
from models import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("=" * 60)
    print("Privilege Level Migration")
    print("=" * 60)
    
    try:
        # Check if privilege_level column exists
        result = db.session.execute(text("PRAGMA table_info(user)"))
        columns = [row[1] for row in result]
        
        if 'privilege_level' not in columns:
            db.session.execute(text("ALTER TABLE user ADD COLUMN privilege_level INTEGER DEFAULT 4 NOT NULL"))
            print("[SUCCESS] Added privilege_level column")
            
            # Set existing admins to level 1
            db.session.execute(text("UPDATE user SET privilege_level = 1 WHERE is_admin = 1"))
            print("[SUCCESS] Set existing admins to privilege level 1")
        else:
            print("[INFO] privilege_level column already exists")
        
        db.session.commit()
        print("\n[SUCCESS] Migration completed successfully!")
        print("\nPrivilege Levels:")
        print("  Level 1: Admin (All Functions)")
        print("  Level 2: Staff (Forum Announcements, Calendar Events)")
        print("  Level 3: Coordinator (Create Events)")
        print("  Level 4: Student (Doubts/Study Posts Only)")
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        db.session.rollback()
        import traceback
        traceback.print_exc()
    
    print("=" * 60)
