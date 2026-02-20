# Admin System Setup Guide

## Overview

The CloudRoom application now includes a comprehensive admin system with:
- ✅ Admin login authentication
- ✅ Protected database access routes
- ✅ Admin dashboard
- ✅ User management (delete, modify, kick)
- ✅ Admin-only access to sensitive data

## Quick Setup

### Step 1: Update Database Schema

First, update the database to add the `is_admin` column:

```powershell
cd CLOUDROOMf
.\venv\Scripts\python.exe update_db_schema.py
```

### Step 2: Create an Admin User

Create your first admin user:

```powershell
.\venv\Scripts\python.exe create_admin.py
```

Choose option 1 to create a new admin user, or option 2 to promote an existing user.

### Step 3: Access Admin Panel

1. Go to: `http://localhost:5000/admin/login`
2. Login with your admin credentials
3. You'll be redirected to the admin dashboard

## Admin Features

### Admin Dashboard (`/admin`)
- View statistics (users, projects, events, teams, clubs, chapters)
- Quick access to user management
- View recent users

### User Management (`/admin/users`)
- View all users
- Edit user details
- Delete users
- Change user passwords
- Grant/revoke admin privileges

### Protected Routes

The following routes now require admin access:
- `/users` - View all users
- `/export_users` - Export users to CSV
- `/admin` - Admin dashboard
- `/admin/users` - User management
- `/admin/user/<id>/edit` - Edit user
- `/admin/user/<id>/delete` - Delete user

### Admin Powers

1. **Delete Users**: Remove users from the system (with cleanup of related data)
2. **Modify Users**: Edit any user's profile, password, and admin status
3. **Kick Users**: Remove users from teams (visible in team view pages)

## Security Features

- ✅ Admin-only routes protected with `@admin_required` decorator
- ✅ Regular users cannot access `/users` or `/export_users`
- ✅ Admin status checked on every protected route
- ✅ Self-protection: Admins cannot delete themselves or remove their own admin status

## Admin Login

**URL**: `http://localhost:5000/admin/login`

This is a separate login page specifically for administrators. Regular users should use `/login`.

## Creating Additional Admins

To create more admin users:

1. **Via Script** (Recommended):
   ```powershell
   .\venv\Scripts\python.exe create_admin.py
   ```

2. **Via Admin Panel**:
   - Login as admin
   - Go to `/admin/users`
   - Click "Edit" on any user
   - Check "Admin Privileges" checkbox
   - Save

## Database Schema Update

If you're upgrading an existing database, the `is_admin` column will be added automatically when you run `update_db_schema.py`. All existing users will have `is_admin = False` by default.

## Troubleshooting

### "Access denied. Admin privileges required"
- Make sure you've created an admin user
- Verify you're logged in as an admin
- Check that the user's `is_admin` field is `True` in the database

### "is_admin column doesn't exist"
- Run `update_db_schema.py` to update the database schema
- Or delete `instances/cloudroom.db` and restart the app (⚠️ This will delete all data)

### Can't access admin routes
- Make sure you're logged in
- Verify your user has `is_admin = True`
- Try logging out and logging back in

## Admin Routes Summary

| Route | Method | Description |
|-------|--------|-------------|
| `/admin/login` | GET/POST | Admin login page |
| `/admin` | GET | Admin dashboard |
| `/admin/users` | GET | List all users |
| `/admin/user/<id>/edit` | GET/POST | Edit user |
| `/admin/user/<id>/delete` | POST | Delete user |
| `/admin/team/<team_id>/kick/<user_id>` | POST | Kick user from team |
| `/users` | GET | View all users (admin only) |
| `/export_users` | GET | Export users CSV (admin only) |

## Notes

- Admin users see an "Admin Panel" link in the navigation menu
- Admin users can kick members from teams (except team leaders)
- Admins cannot delete themselves or remove their own admin status
- All admin actions are logged via flash messages
