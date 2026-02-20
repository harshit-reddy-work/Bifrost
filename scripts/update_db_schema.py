"""
Script to update database schema to add is_admin column.
Run this if you get errors about missing is_admin column.
"""
from app import create_app
from models import db

app = create_app()

with app.app_context():
    print("Updating database schema...")
    
    try:
        # This will create all tables including the new is_admin column
        db.create_all()
        print("[SUCCESS] Database schema updated successfully!")
        print("   The is_admin column has been added to the user table.")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        print("\nIf you're using SQLite, you may need to:")
        print("1. Backup your database")
        print("2. Delete instances/cloudroom.db")
        print("3. Run the app again to recreate tables")
