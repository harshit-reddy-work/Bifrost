"""
Migration script to add forum and calendar features to the database.
This will add:
1. Forum tables (forum_posts, forum_comments, forum_votes, forum_categories)
2. User ban/silence columns
3. Enhanced Event table columns
"""
from app import create_app
from models import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("=" * 60)
    print("Forum & Calendar Migration")
    print("=" * 60)
    
    try:
        # Check and add user ban/silence columns
        result = db.session.execute(text("PRAGMA table_info(user)"))
        columns = [row[1] for row in result]
        
        if 'is_banned' not in columns:
            db.session.execute(text("ALTER TABLE user ADD COLUMN is_banned BOOLEAN DEFAULT 0 NOT NULL"))
            print("[SUCCESS] Added is_banned column")
        else:
            print("[INFO] is_banned column already exists")
        
        if 'is_silenced' not in columns:
            db.session.execute(text("ALTER TABLE user ADD COLUMN is_silenced BOOLEAN DEFAULT 0 NOT NULL"))
            print("[SUCCESS] Added is_silenced column")
        else:
            print("[INFO] is_silenced column already exists")
        
        if 'silence_until' not in columns:
            db.session.execute(text("ALTER TABLE user ADD COLUMN silence_until DATETIME"))
            print("[SUCCESS] Added silence_until column")
        else:
            print("[INFO] silence_until column already exists")
        
        # Check and add Event table enhancements
        result = db.session.execute(text("PRAGMA table_info(events)"))
        event_columns = [row[1] for row in result]
        
        if 'end_date' not in event_columns:
            db.session.execute(text("ALTER TABLE events ADD COLUMN end_date DATETIME"))
            print("[SUCCESS] Added end_date column to events")
        else:
            print("[INFO] end_date column already exists in events")
        
        if 'event_type' not in event_columns:
            db.session.execute(text("ALTER TABLE events ADD COLUMN event_type VARCHAR(50) DEFAULT 'general'"))
            print("[SUCCESS] Added event_type column to events")
        else:
            print("[INFO] event_type column already exists in events")
        
        if 'color' not in event_columns:
            db.session.execute(text("ALTER TABLE events ADD COLUMN color VARCHAR(20) DEFAULT '#007bff'"))
            print("[SUCCESS] Added color column to events")
        else:
            print("[INFO] color column already exists in events")
        
        if 'created_by' not in event_columns:
            db.session.execute(text("ALTER TABLE events ADD COLUMN created_by INTEGER"))
            print("[SUCCESS] Added created_by column to events")
        else:
            print("[INFO] created_by column already exists in events")
        
        # Create forum tables
        db.create_all()
        print("[SUCCESS] Forum tables created/verified")
        
        db.session.commit()
        print("\n[SUCCESS] Migration completed successfully!")
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        db.session.rollback()
        import traceback
        traceback.print_exc()
    
    print("=" * 60)
