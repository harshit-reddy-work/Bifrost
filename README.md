# 🌐 CloudRoom — Bifrost

> A full-featured college community platform built with **Flask** and **SQLite**, deployed via **Vercel**.  
> Students, coordinators, staff, and admins each get tailored access to manage events, projects, teams, clubs, a forum, and more.

---

## 📑 Table of Contents

1. [Project Overview](#-project-overview)
2. [Tech Stack](#-tech-stack)
3. [Privilege / Admin Levels](#-privilege--admin-levels)
4. [Feature Breakdown by Role](#-feature-breakdown-by-role)
5. [All Application Routes](#-all-application-routes)
6. [Setup & Running Locally](#-setup--running-locally)
7. [Database Access](#-database-access)
8. [Utility Scripts](#-utility-scripts)
9. [Deployment (Vercel)](#-deployment-vercel)
10. [Project Structure](#-project-structure)
11. [Troubleshooting](#-troubleshooting)

---

## 📌 Project Overview

CloudRoom is a college campus hub where students can:
- Register and maintain their academic profile (coding handles, resume, skills)
- Form teams and collaborate on projects
- Browse and register for events
- View and join clubs & student chapters
- Participate in a Reddit-style forum
- View an interactive academic calendar
- Climb a leaderboard based on coding scores (CodeChef, HackerRank, LeetCode)

---

## 🛠 Tech Stack

| Layer      | Technology                             |
|------------|----------------------------------------|
| Backend    | Python 3.8+ · Flask 2.3.3              |
| ORM        | Flask-SQLAlchemy 3.0.3                 |
| Auth       | Flask-Login 0.6.3                      |
| Database   | SQLite (local) · PostgreSQL (Vercel)   |
| Migrations | Flask-Migrate 4.0.4                    |
| Server     | Gunicorn 21.2.0 (production)           |
| Frontend   | Jinja2 templates · HTML/CSS/JS         |
| Calendar   | FullCalendar.js                        |
| Deployment | Vercel                                 |

---

## 🔐 Privilege / Admin Levels

CloudRoom uses a **4-level privilege system**. Every new user starts at **Level 4**.

| Level | Role            | Description                                      |
|-------|-----------------|--------------------------------------------------|
| **1** | **Admin**       | Full access — user management, moderation, all features |
| **2** | **Staff**       | Forum announcements + calendar event management  |
| **3** | **Coordinator** | Create events (Events tab) + most forum posts    |
| **4** | **Student**     | Default — view content, post in Q&A/study only   |

### Level 1 — Admin
- Access the **Admin Panel** (`/admin`)
- Full **User Management**: create, edit, delete users; change passwords; grant/revoke admin
- **Forum Moderation**: ban/silence users, lock/pin posts, post in all categories including Announcements
- **Calendar Management**: create, edit, delete calendar events
- **Create Events** in both the Events tab and Calendar
- Export users to CSV
- Kick members from teams
- View all users (`/users`)

### Level 2 — Staff
- Post in **all forum categories** including Announcements
- **Create and manage Calendar events** via `/admin/calendar`
- Cannot access Admin Panel or manage users

### Level 3 — Coordinator
- **Create events** in the Events tab (`/events/create`)
- Post in most forum categories (except Announcements)
- Cannot manage calendar or access admin panel

### Level 4 — Student (Default)
- View all content freely
- Post in forum only in: **Questions**, **Study**, **Doubts** categories
- Cannot create events
- Cannot access Announcements forum category

### Privilege Sync Rule
- Setting a user to **Level 1** automatically sets `is_admin = True`
- Setting a user to **Level 2–4** removes admin status if applicable
- Admins cannot change their own privilege level away from Level 1

---

## 🧩 Feature Breakdown by Role

### Feature Access Matrix

| Feature                        | Student (L4) | Coordinator (L3) | Staff (L2) | Admin (L1) |
|-------------------------------|:---:|:---:|:---:|:---:|
| View forum                    | ✅  | ✅  | ✅  | ✅  |
| Post in Doubts/Study/Questions| ✅  | ✅  | ✅  | ✅  |
| Post in other categories      | ❌  | ✅  | ✅  | ✅  |
| Post Announcements            | ❌  | ❌  | ✅  | ✅  |
| Create Event (Events tab)     | ❌  | ✅  | ❌  | ✅  |
| Create Calendar Event         | ❌  | ❌  | ✅  | ✅  |
| Manage Calendar               | ❌  | ❌  | ✅  | ✅  |
| Access Admin Panel            | ❌  | ❌  | ❌  | ✅  |
| User Management               | ❌  | ❌  | ❌  | ✅  |
| Forum Moderation              | ❌  | ❌  | ❌  | ✅  |
| Export Users CSV              | ❌  | ❌  | ❌  | ✅  |
| Kick team members             | ❌  | ❌  | ❌  | ✅  |

### Forum Features (All Users)
- Create posts with title, content, and category
- Threaded comments (reply to comments, unlimited nesting)
- Reddit-style upvote/downvote on posts and comments
- Score = upvotes − downvotes
- Search posts by title or content

### Admin Forum Moderation
- **Ban Users**: permanently remove from forum posting
- **Silence Users**: temporarily or permanently prevent posting (enter days; 0 = permanent)
- **Lock Posts**: prevent new comments
- **Pin Posts**: display at top of forum

### Calendar Features
- Students: interactive month-view calendar (FullCalendar.js), click events for details
- Staff/Admin: create, edit, delete events
- Event types: General, Exam, Holiday, Deadline, Workshop, Competition
- Supports multi-day events, color coding, and location fields

### Teams
- Create teams with a size limit
- Send/accept/decline join requests
- Send/accept/decline invitations
- Admin can kick members from any team

### Projects
- Create and showcase projects with GitHub links
- Each user can list multiple projects

### Clubs & Chapters
- Browse clubs and student chapters
- Each club has contact, faculty in-charge, and website info

### Leaderboard
- Rankings based on coding scores from CodeChef, HackerRank, and LeetCode handles

### User Profiles
- Upload resume and certificates
- List skills, branch, year, roll number
- Link coding platform handles

---

## 🗺 All Application Routes

### Auth Routes
| Route             | Method   | Access       | Description           |
|-------------------|----------|--------------|-----------------------|
| `/register`       | GET/POST | Public       | Register new account  |
| `/login`          | GET/POST | Public       | Student login         |
| `/logout`         | GET      | Logged in    | Logout                |

### User / Profile Routes
| Route                      | Method   | Access       | Description              |
|---------------------------|----------|--------------|--------------------------|
| `/profile`                | GET/POST | Logged in    | View/edit own profile    |
| `/user/<username>`        | GET      | Logged in    | View user profile        |
| `/users`                  | GET      | Admin only   | View all users           |
| `/export_users`           | GET      | Admin only   | Export all users as CSV  |

### Events Routes
| Route             | Method   | Access            | Description            |
|-------------------|----------|-------------------|------------------------|
| `/events`         | GET      | Logged in         | Browse all events      |
| `/events/create`  | GET/POST | Coordinator+ (L3) | Create a new event     |
| `/events/<id>`    | GET      | Logged in         | View event details     |
| `/events/<id>/register` | POST | Logged in    | Register for event     |

### Teams Routes
| Route                               | Method   | Access    | Description              |
|------------------------------------|----------|-----------|--------------------------|
| `/teamup`                          | GET      | Logged in | Browse teams             |
| `/teams/create`                    | GET/POST | Logged in | Create a team            |
| `/teams/<id>`                      | GET      | Logged in | View team page           |
| `/teams/<id>/join`                 | POST     | Logged in | Request to join team     |
| `/teams/<id>/invite/<user_id>`     | POST     | Logged in | Invite a user to team    |

### Projects Routes
| Route               | Method   | Access    | Description         |
|--------------------|----------|-----------|---------------------|
| `/projects`        | GET      | Logged in | Browse all projects |
| `/projects/create` | GET/POST | Logged in | Create a project    |
| `/projects/<id>`   | GET      | Logged in | View project        |

### Community (Clubs & Chapters)
| Route           | Method | Access    | Description            |
|----------------|--------|-----------|------------------------|
| `/clubs`       | GET    | Logged in | Browse clubs           |
| `/chapters`    | GET    | Logged in | Browse student chapters|

### Leaderboard
| Route          | Method | Access    | Description           |
|---------------|--------|-----------|-----------------------|
| `/leaderboard` | GET   | Logged in | View score rankings   |

### Forum Routes
| Route                             | Method   | Access    | Description                    |
|----------------------------------|----------|-----------|--------------------------------|
| `/forum`                         | GET      | Logged in | Main forum page                |
| `/forum/post/<id>`               | GET/POST | Logged in | View post + add comment        |
| `/forum/create`                  | GET/POST | Logged in | Create post (with restrictions)|
| `/forum/vote/<type>/<id>`        | POST     | Logged in | Vote on post or comment        |

### Calendar Routes
| Route                                  | Method   | Access       | Description              |
|---------------------------------------|----------|--------------|--------------------------|
| `/calendar`                           | GET      | Logged in    | Student calendar view    |
| `/admin/calendar`                     | GET      | Staff+ (L2)  | Manage calendar events   |
| `/admin/calendar/event/create`        | GET/POST | Staff+ (L2)  | Create calendar event    |
| `/admin/calendar/event/<id>/edit`     | GET/POST | Staff+ (L2)  | Edit calendar event      |
| `/admin/calendar/event/<id>/delete`   | POST     | Staff+ (L2)  | Delete calendar event    |

### Admin Routes
| Route                                   | Method   | Access    | Description                  |
|----------------------------------------|----------|-----------|------------------------------|
| `/admin/login`                         | GET/POST | Public    | Admin-specific login page    |
| `/admin`                               | GET      | Admin (L1)| Admin dashboard              |
| `/admin/users`                         | GET      | Admin (L1)| List and manage all users    |
| `/admin/user/<id>/edit`                | GET/POST | Admin (L1)| Edit any user's details      |
| `/admin/user/<id>/delete`              | POST     | Admin (L1)| Delete user and related data |
| `/admin/team/<team_id>/kick/<user_id>` | POST     | Admin (L1)| Kick user from any team      |
| `/admin/forum/users`                   | GET      | Admin (L1)| Manage forum users           |
| `/admin/forum/post/<id>/lock`          | POST     | Admin (L1)| Lock/unlock a post           |
| `/admin/forum/post/<id>/pin`           | POST     | Admin (L1)| Pin/unpin a post             |

---

## 🚀 Setup & Running Locally

### Prerequisites
- **Python 3.8+** — [Download here](https://www.python.org/downloads/)  
  *(Make sure to check "Add Python to PATH" during installation)*

### Quick Start

**Option 1 — PowerShell script (Recommended):**
```powershell
.\run.ps1
```

**Option 2 — Command Prompt batch file:**
```cmd
run.bat
```

**Option 3 — Manual:**
```powershell
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

The app runs at: **http://localhost:5000**

### First-Time Database Setup

After starting the app for the first time, the SQLite database is created automatically at `instances/cloudroom.db`.

#### Initialize Database Tables
```powershell
.\venv\Scripts\python.exe scripts\create_db.py
```

#### Add Forum Categories
```powershell
.\venv\Scripts\python.exe scripts\create_forum_categories.py
```

#### (Optional) Import Clubs & Chapters Data
```powershell
.\venv\Scripts\python.exe scripts\import_clubs_chapters.py
```

### Creating the First Admin User

```powershell
.\venv\Scripts\python.exe scripts\create_first_admin.py
```

OR promote an existing user:
```powershell
.\venv\Scripts\python.exe scripts\create_admin.py
```

Then log in at: **http://localhost:5000/admin/login**

---

## 🗄 Database Access

The app uses **SQLite** locally. Database file: `instances/cloudroom.db`

### Web Routes (Easiest)
| What                  | URL                                |
|----------------------|------------------------------------|
| All Users            | http://localhost:5000/users        |
| Export Users to CSV  | http://localhost:5000/export_users |
| Leaderboard          | http://localhost:5000/leaderboard  |
| Projects             | http://localhost:5000/projects     |
| Events               | http://localhost:5000/events       |
| Teams                | http://localhost:5000/teamup       |
| Clubs                | http://localhost:5000/clubs        |
| Chapters             | http://localhost:5000/chapters     |

### Via Script
```powershell
.\venv\Scripts\python.exe scripts\view_db.py       # Summary of all tables
.\venv\Scripts\python.exe scripts\db_shell.py      # Interactive Python shell
```

### Via Flask Shell
```powershell
.\venv\Scripts\python.exe -m flask shell
```
```python
# Example queries
User.query.all()
User.query.filter_by(email='user@vnrvjiet.in').first()
Project.query.count()
```

### Via SQLite CLI
```powershell
sqlite3 instances\cloudroom.db
```
```sql
.tables
SELECT id, username, email FROM user;
.exit
```

### Backup & Restore
```powershell
# Backup
Copy-Item instances\cloudroom.db instances\cloudroom_backup.db

# Reset (⚠️ DELETES ALL DATA)
Remove-Item instances\cloudroom.db
python app.py   # Recreates schema on next run
```

---

## 🔧 Utility Scripts

All scripts are in the `scripts/` folder.

| Script                       | Purpose                                           |
|-----------------------------|---------------------------------------------------|
| `create_db.py`              | Initialize database tables                        |
| `create_first_admin.py`     | Create the very first admin interactively         |
| `create_admin.py`           | Create or promote a user to admin                 |
| `create_forum_categories.py`| Seed default forum categories                     |
| `create_tables.py`          | Alias to create all DB tables                     |
| `import_clubs_chapters.py`  | Import clubs and chapters data                    |
| `seed_data.py`              | Seed sample data into the database                |
| `view_db.py`                | Print a summary of all database tables            |
| `db_shell.py`               | Interactive Python/SQLAlchemy shell               |
| `update_db_schema.py`       | Add `is_admin` column (for upgrades)              |
| `migrate_add_admin.py`      | Migration: add admin fields                       |
| `migrate_event_poster.py`   | Migration: add event poster field                 |
| `migrate_forum_calendar.py` | Migration: add forum and calendar tables          |
| `migrate_privilege_level.py`| Migration: add `privilege_level` column           |
| `verify_admin.py`           | Check if a user has admin status                  |

---

## ☁️ Deployment (Vercel)

This project is deployed on **Vercel** as a serverless Python app.

### Key Files
- `vercel.json` — Vercel routing configuration
- `api/index.py` — Vercel entry point
- `.vercelignore` — Files excluded from deployment
- `requirements.txt` — Python dependencies (includes `gunicorn`, `psycopg2-binary`)

### Deploy
```bash
vercel --prod
```

> **Note:** On Vercel, SQLite is replaced by **PostgreSQL**. Set the `DATABASE_URL` environment variable in your Vercel project settings.

---

## 📁 Project Structure

```
Bifrost/
├── app.py                      # Main Flask application (all routes)
├── models.py                   # SQLAlchemy database models
├── config.py                   # App configuration
├── forms.py                    # WTForms definitions
├── requirements.txt            # Python dependencies
├── vercel.json                 # Vercel deployment config
├── .vercelignore               # Vercel ignore rules
├── run.ps1                     # Windows PowerShell run script
├── run.bat                     # Windows CMD run script
│
├── api/
│   └── index.py                # Vercel serverless entry point
│
├── scripts/                    # Database management utilities
│   ├── create_db.py
│   ├── create_admin.py
│   ├── create_first_admin.py
│   ├── create_forum_categories.py
│   ├── create_tables.py
│   ├── import_clubs_chapters.py
│   ├── seed_data.py
│   ├── view_db.py
│   ├── db_shell.py
│   ├── verify_admin.py
│   ├── update_db_schema.py
│   ├── migrate_add_admin.py
│   ├── migrate_event_poster.py
│   ├── migrate_forum_calendar.py
│   └── migrate_privilege_level.py
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── admin/
│   ├── auth/
│   ├── community/
│   ├── events/
│   ├── forum/
│   ├── leaderboard/
│   ├── messaging/
│   ├── projects/
│   ├── teams/
│   └── user/
│
├── static/                     # Static assets
│   ├── css/
│   ├── js/
│   ├── images/
│   └── icons/
│
└── data/                       # Seed/import data files
```

---

## ❓ Troubleshooting

### Can't log in as admin
1. Ensure an admin user exists — run `scripts/create_first_admin.py`
2. Use the admin login page: `/admin/login` (not `/login`)
3. Check `privilege_level = 1` and `is_admin = True` in the DB

### "is_admin column doesn't exist"
```powershell
.\venv\Scripts\python.exe scripts\update_db_schema.py
```

### "privilege_level column doesn't exist"
```powershell
.\venv\Scripts\python.exe scripts\migrate_privilege_level.py
```

### Forum not showing posts
```powershell
.\venv\Scripts\python.exe scripts\create_forum_categories.py
```

### User cannot post in forum
- Level 4 users can only post in: Questions, Study, Doubts
- Check if the user is banned (`is_banned = True`) or silenced

### User cannot create events
- Events tab: requires Level 3 (Coordinator) or higher
- Calendar events: requires Level 2 (Staff) or higher

### Python not found
- Install Python 3.8+ from https://www.python.org/downloads/
- Check "Add Python to PATH" during install
- Restart terminal after installation

### Database locked
- Stop the Flask app before running scripts
- Close any SQLite GUI tools (DB Browser, etc.)

---

## 📧 Email Domain Restriction

> Registration is restricted to **VNR VJIET email addresses** (`@vnrvjiet.in`).  
> If you need to change this, update the email validation logic in `forms.py` and `app.py`.

---

*CloudRoom — Built for VNR VJIET. Deployed on Vercel.*
