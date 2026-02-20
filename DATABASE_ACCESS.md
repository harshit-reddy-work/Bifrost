# Database Access Guide for CloudRoom

The CloudRoom application uses **SQLite** as its database. The database file is located at:
```
instances/cloudroom.db
```

## Quick Access via Web Browser (Easiest!)

You can view database data directly in your browser using these URLs:

### View All Users:
```
http://localhost:5000/users
```
This page displays all users in the database with their details.

### Export Users to CSV:
```
http://localhost:5000/export_users
```
Downloads a CSV file with all user data.

### Leaderboard:
```
http://localhost:5000/leaderboard
```
Shows user rankings based on coding platform scores.

### Other Database-Related Pages:
- **Projects**: `http://localhost:5000/projects` - View all projects
- **Events**: `http://localhost:5000/events` - View all events
- **Teams**: `http://localhost:5000/teamup` - View all teams
- **Clubs**: `http://localhost:5000/clubs` - View all clubs
- **Chapters**: `http://localhost:5000/chapters` - View all student chapters

## Methods to Access the Database

### Method 1: Flask Shell (Recommended for Python queries)

The easiest way to interact with the database using Python/SQLAlchemy:

```powershell
cd CLOUDROOMf
.\venv\Scripts\python.exe -m flask shell
```

Or use the custom database shell script:
```powershell
.\venv\Scripts\python.exe db_shell.py
```

**Example queries in Flask shell:**
```python
# Get all users
users = User.query.all()

# Find a specific user
user = User.query.filter_by(email='user@example.com').first()

# Get all projects
projects = Project.query.all()

# Count records
user_count = User.query.count()

# Create a new user
new_user = User(name='John Doe', email='john@example.com', username='johndoe')
new_user.password_hash = generate_password_hash('password123')
db.session.add(new_user)
db.session.commit()

# Update a user
user = User.query.filter_by(username='johndoe').first()
user.name = 'Jane Doe'
db.session.commit()

# Delete a record
user = User.query.filter_by(username='johndoe').first()
db.session.delete(user)
db.session.commit()
```

### Method 2: Quick Database Viewer

View a summary of all data:
```powershell
.\venv\Scripts\python.exe view_db.py
```

This will show:
- Total counts for each table
- Sample records from each table
- Database file location

### Method 3: SQLite Command Line Tool

Access the database directly using SQLite:

```powershell
sqlite3 instances\cloudroom.db
```

**Example SQL queries:**
```sql
-- List all tables
.tables

-- View schema of a table
.schema user

-- Select all users
SELECT * FROM user;

-- Select specific columns
SELECT id, username, email, name FROM user;

-- Count records
SELECT COUNT(*) FROM user;

-- Join query (users and their projects)
SELECT u.username, u.name, p.title 
FROM user u 
LEFT JOIN project p ON p.owner_id = u.id;

-- Exit SQLite
.exit
```

### Method 4: GUI Database Browser (Recommended for visual inspection)

**DB Browser for SQLite** (Free, cross-platform):
1. Download from: https://sqlitebrowser.org/
2. Install and open the application
3. Click "Open Database"
4. Navigate to: `CLOUDROOMf\instances\cloudroom.db`
5. Browse tables, run queries, and edit data visually

**Other GUI tools:**
- **DBeaver** (Free, supports many databases): https://dbeaver.io/
- **SQLiteStudio** (Free): https://sqlitestudio.pl/
- **VS Code Extension**: Install "SQLite Viewer" extension

### Method 5: Python Script (Custom queries)

Create your own script:

```python
from app import create_app
from models import db, User, Project

app = create_app()

with app.app_context():
    # Your custom queries here
    users = User.query.all()
    for user in users:
        print(f"{user.username}: {user.email}")
```

Run it:
```powershell
.\venv\Scripts\python.exe your_script.py
```

## Database Schema

### Main Tables:

1. **user** - User accounts and profiles
   - id, username, email, name, password_hash
   - mobile, roll_number, codechef, hackerrank, leetcode
   - college, branch, year, skills
   - resume_filename, certificates_filename
   - created_at

2. **project** - User projects
   - id, title, description, github
   - owner_id (FK to user)
   - created_at

3. **events** - Events/competitions
   - id, title, description, date, location
   - created_at

4. **team** - Teams for collaboration
   - id, name, description
   - leader_id (FK to user)
   - size_limit

5. **team_members** - Many-to-many relationship (users ↔ teams)
   - user_id, team_id

6. **club** - Clubs information
   - id, name, description, contact, faculty_incharge, website

7. **student_chapter** - Student chapters
   - id, name, associated_club, description, contact, student_lead

8. **registrations** - Event registrations
   - id, user_id, event_id, created_at

9. **team_join_request** - Team join requests
   - id, team_id, sender_id, status

10. **team_invite** - Team invitations
    - id, team_id, user_id, sender_id, created_at

## Common Database Operations

### Backup the database:
```powershell
Copy-Item instances\cloudroom.db instances\cloudroom_backup.db
```

### Reset the database (⚠️ WARNING: Deletes all data):
```python
from app import create_app
from models import db

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
    print("Database reset complete!")
```

### Export data to CSV:
The app already has an export route: `/export_users` (exports users to CSV)

## Troubleshooting

**Database locked error:**
- Make sure the Flask app is not running
- Close any database viewers/GUI tools
- Try again

**Database file not found:**
- The database is created automatically when you first run the app
- Check if `instances/cloudroom.db` exists
- If not, run the app once to create it

**Permission errors:**
- Make sure you have read/write permissions to the `instances` folder
- Run your terminal/IDE as administrator if needed
