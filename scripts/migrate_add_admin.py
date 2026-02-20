"""
Migration script to add is_admin column to existing user table.
This script will ALTER the existing table to add the column.
"""
from app import create_app
from models import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("=" * 60)
    print("Adding is_admin column to user table...")
    print("=" * 60)
    
    try:
        # Check if column already exists
        result = db.session.execute(text("PRAGMA table_info(user)"))
        columns = [row[1] for row in result]
        
        if 'is_admin' in columns:
            print("[INFO] Column 'is_admin' already exists. No migration needed.")
        else:
            # Add the column
            db.session.execute(text("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0 NOT NULL"))
            db.session.commit()
            print("[SUCCESS] Column 'is_admin' added successfully!")
            print("   All existing users have been set to is_admin = False")
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        db.session.rollback()
    
    print("=" * 60)
