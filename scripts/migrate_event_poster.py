"""
Migration script to add poster and register_url columns to events table.
"""
from app import create_app
from models import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("=" * 60)
    print("Event Poster & Register URL Migration")
    print("=" * 60)
    
    try:
        # Check if columns exist
        result = db.session.execute(text("PRAGMA table_info(events)"))
        columns = [row[1] for row in result]
        
        if 'poster' not in columns:
            db.session.execute(text("ALTER TABLE events ADD COLUMN poster VARCHAR(300)"))
            print("[SUCCESS] Added poster column to events")
        else:
            print("[INFO] poster column already exists in events")
        
        if 'register_url' not in columns:
            db.session.execute(text("ALTER TABLE events ADD COLUMN register_url VARCHAR(500)"))
            print("[SUCCESS] Added register_url column to events")
        else:
            print("[INFO] register_url column already exists in events")
        
        db.session.commit()
        print("\n[SUCCESS] Migration completed successfully!")
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        db.session.rollback()
        import traceback
        traceback.print_exc()
    
    print("=" * 60)
