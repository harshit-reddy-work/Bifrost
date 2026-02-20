# Privilege System Documentation

## Overview

CloudRoom uses a 4-level privilege system to control user access and permissions across the platform.

## Privilege Levels

### Level 1: Admin
- **All Functions**: Complete access to all features
- **Access**: Admin panel, user management, forum moderation, calendar management
- **Forum**: Can post in all categories including Announcements
- **Events**: Can create events in both Events tab and Calendar
- **Moderation**: Can ban, silence, lock posts, pin posts

### Level 2: Staff
- **Forum Announcements**: Can post forum-wide announcements
- **Calendar Events**: Can create and manage calendar events
- **Access**: `/admin/calendar` for calendar management
- **Forum**: Can post in all categories except restricted ones
- **Events**: Can create events in Calendar (not Events tab)

### Level 3: Coordinator
- **Create Events**: Can create events in the Events tab (`/events/create`)
- **Forum**: Can post in most categories (except Announcements)
- **Access**: Event creation in Events page
- **Restrictions**: Cannot post announcements, cannot access calendar management

### Level 4: Student (Default)
- **Forum Restrictions**: Can only post in Questions, Study, or Doubts categories
- **Forum**: Limited to doubt/study posts only
- **Events**: Can only view events, cannot create
- **Default Level**: All new users start at Level 4

## Feature Access Matrix

| Feature | Level 4 (Student) | Level 3 (Coordinator) | Level 2 (Staff) | Level 1 (Admin) |
|---------|-------------------|----------------------|-----------------|-----------------|
| View Forum | ✅ | ✅ | ✅ | ✅ |
| Post Doubts/Study | ✅ | ✅ | ✅ | ✅ |
| Post Other Categories | ❌ | ✅ | ✅ | ✅ |
| Post Announcements | ❌ | ❌ | ✅ | ✅ |
| Create Event (Events Tab) | ❌ | ✅ | ❌ | ✅ |
| Create Calendar Event | ❌ | ❌ | ✅ | ✅ |
| Manage Calendar | ❌ | ❌ | ✅ | ✅ |
| Admin Panel | ❌ | ❌ | ❌ | ✅ |
| User Management | ❌ | ❌ | ❌ | ✅ |
| Forum Moderation | ❌ | ❌ | ❌ | ✅ |

## Admin Management

### Setting User Privilege Levels

1. **Via Admin Panel**:
   - Go to `/admin/users`
   - Click "Edit" on any user
   - Select privilege level from dropdown
   - Save changes

2. **Privilege Level Options**:
   - Level 1: Admin (All Functions)
   - Level 2: Staff (Forum Announcements, Calendar Events)
   - Level 3: Coordinator (Create Events)
   - Level 4: Student (Doubts/Study Posts Only)

### Automatic Sync

- Setting a user to Level 1 automatically sets `is_admin = True`
- Setting a user to Level 2-4 with `is_admin = False` removes admin status
- Admins cannot change their own privilege level from Level 1

## Forum Category Restrictions

### Level 4 (Students)
- **Allowed**: Questions, Study, Doubts
- **Restricted**: All other categories

### Level 3 (Coordinators)
- **Allowed**: All categories except Announcements
- **Restricted**: Announcements

### Level 2 (Staff)
- **Allowed**: All categories including Announcements
- **Special**: Can post forum-wide announcements

### Level 1 (Admin)
- **Allowed**: All categories
- **Special**: Full moderation powers

## Route Protection

### Decorators Used

- `@admin_required` - Level 1 only
- `@staff_required` - Level 2+ (Staff, Admin)
- `@coordinator_required` - Level 3+ (Coordinator, Staff, Admin)
- `@login_required` - All authenticated users

### Protected Routes

- `/admin/*` - Level 1 (Admin) only
- `/admin/calendar/*` - Level 2+ (Staff, Admin)
- `/events/create` - Level 3+ (Coordinator, Staff, Admin)
- `/forum/create` - All users (with category restrictions)

## Database Schema

### User Table
- `privilege_level` INTEGER DEFAULT 4 NOT NULL
- Values: 1 (Admin), 2 (Staff), 3 (Coordinator), 4 (Student)

### Migration
Run `migrate_privilege_level.py` to add the privilege_level column:
```powershell
.\venv\Scripts\python.exe migrate_privilege_level.py
```

## Usage Examples

### Promoting a User to Coordinator
1. Admin logs in
2. Go to `/admin/users`
3. Click "Edit" on user
4. Select "Level 3: Coordinator"
5. Save

### Promoting a User to Staff
1. Admin logs in
2. Go to `/admin/users`
3. Click "Edit" on user
4. Select "Level 2: Staff"
5. Save

### Creating an Admin
1. Admin logs in
2. Go to `/admin/users`
3. Click "Edit" on user
4. Select "Level 1: Admin"
5. Save (automatically sets is_admin = True)

## Best Practices

1. **Default Level**: All new users should start at Level 4 (Student)
2. **Coordinator Assignment**: Assign Level 3 to club/student chapter coordinators
3. **Staff Assignment**: Assign Level 2 to faculty/staff members
4. **Admin Assignment**: Only assign Level 1 to trusted administrators
5. **Regular Review**: Periodically review privilege levels to ensure they're appropriate

## Troubleshooting

### User Cannot Post in Forum
- Check privilege level (should be 4+)
- Check if user is banned or silenced
- Verify category restrictions for Level 4 users

### User Cannot Create Events
- Check privilege level (should be 3+ for Events tab, 2+ for Calendar)
- Verify user is logged in
- Check route protection decorators

### Admin Features Not Working
- Verify privilege_level = 1
- Check is_admin flag (should be True for Level 1)
- Ensure user is logged in
