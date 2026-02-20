# Forum & Calendar Features Documentation

## Overview

Two major features have been added to CloudRoom:
1. **Reddit-style Forum** - A community discussion platform
2. **Admin Calendar** - Event management system

## Forum Features

### User Features

- **Create Posts**: Users can create posts with titles, content, and categories
- **Comment System**: Threaded comments (reply to comments)
- **Voting System**: Upvote/downvote posts and comments (Reddit-style)
- **Categories**: Posts can be organized into categories
- **Search**: Search posts by title or content
- **View Posts**: Browse posts sorted by score and date

### Admin Moderation Features

- **Ban Users**: Permanently ban users from the forum
- **Silence Users**: Temporarily or permanently silence users (prevent posting/commenting)
- **Lock Posts**: Lock posts to prevent new comments
- **Pin Posts**: Pin important posts to the top
- **User Management**: View all users and their forum status

### Forum URLs

- `/forum` - Main forum page
- `/forum/post/<id>` - View a specific post
- `/forum/create` - Create a new post
- `/admin/forum/users` - Admin: Manage forum users
- `/admin/forum/post/<id>/lock` - Admin: Lock/unlock post
- `/admin/forum/post/<id>/pin` - Admin: Pin/unpin post

### User Restrictions

- **Banned Users**: Cannot create posts or comments
- **Silenced Users**: Cannot create posts or comments (temporary or permanent)
- **Locked Posts**: No new comments allowed

## Calendar Features

### Student Features

- **View Calendar**: Interactive calendar view with FullCalendar
- **View Events**: See all upcoming events
- **Event Details**: Click events to see details

### Admin Features

- **Create Events**: Add new events to the calendar
- **Edit Events**: Modify existing events
- **Delete Events**: Remove events from calendar
- **Event Types**: Categorize events (general, exam, holiday, deadline, workshop, competition)
- **Colors**: Assign colors to events for visual distinction
- **Multi-day Events**: Support for events spanning multiple days

### Calendar URLs

- `/calendar` - Student calendar view
- `/admin/calendar` - Admin calendar management
- `/admin/calendar/event/create` - Create new event
- `/admin/calendar/event/<id>/edit` - Edit event
- `/admin/calendar/event/<id>/delete` - Delete event

## Database Schema

### New Tables

1. **forum_categories** - Forum categories
2. **forum_posts** - Forum posts
3. **forum_comments** - Forum comments (with parent_id for threading)
4. **forum_votes** - User votes on posts/comments

### Enhanced Tables

1. **user** - Added columns:
   - `is_banned` - Boolean flag for banned users
   - `is_silenced` - Boolean flag for silenced users
   - `silence_until` - DateTime for temporary silence expiration

2. **events** - Added columns:
   - `end_date` - End date for multi-day events
   - `event_type` - Event category
   - `color` - Calendar color
   - `created_by` - Admin who created the event

## Setup Instructions

### 1. Run Migration

The database migration has been completed. If you need to run it again:

```powershell
.\venv\Scripts\python.exe migrate_forum_calendar.py
```

### 2. Create Forum Categories

Default categories have been created. To add more:

```powershell
.\venv\Scripts\python.exe create_forum_categories.py
```

### 3. Access Features

- **Forum**: Navigate to `/forum` in your browser
- **Calendar**: Navigate to `/calendar` in your browser
- **Admin Calendar**: Navigate to `/admin/calendar` (admin only)

## Admin Moderation Guide

### Banning a User

1. Go to `/admin/forum/users`
2. Find the user
3. Click "Ban" button
4. User will be permanently banned from forum

### Silencing a User

1. Go to `/admin/forum/users`
2. Find the user
3. Click "Silence" button
4. Enter number of days (0 for permanent)
5. User cannot post or comment during silence period

### Managing Posts

- **Lock Post**: Prevents new comments
- **Pin Post**: Shows post at top of forum
- **Unlock/Unpin**: Remove restrictions

## Event Management Guide

### Creating an Event

1. Go to `/admin/calendar`
2. Click "Create Event"
3. Fill in:
   - Title (required)
   - Description
   - Start Date (required)
   - End Date (optional, for multi-day events)
   - Location
   - Event Type
   - Color
4. Click "Create Event"

### Event Types

- **General** - General events
- **Exam** - Examinations
- **Holiday** - Holidays
- **Deadline** - Important deadlines
- **Workshop** - Workshops
- **Competition** - Competitions

## Navigation

New menu items have been added:
- **Forum** - Access the forum
- **Calendar** - View the calendar
- **Admin Panel** - Admin dashboard (admin only)

## Technical Details

### Forum Voting System

- Each user can vote once per post/comment
- Clicking the same vote removes it
- Clicking opposite vote changes it
- Score = upvotes - downvotes

### Comment Threading

- Comments can have parent comments
- Replies are nested under parent comments
- Unlimited nesting depth

### Calendar Integration

- Uses FullCalendar.js library
- Events displayed in month view
- Click events to see details
- Color-coded by event type

## Troubleshooting

### Forum not showing posts
- Check if categories exist: Run `create_forum_categories.py`
- Verify database migration completed

### Calendar not loading
- Check FullCalendar CDN is accessible
- Verify events exist in database

### Admin features not working
- Ensure user has `is_admin = True`
- Check admin routes are protected

## Future Enhancements

Potential improvements:
- Post editing/deletion
- Comment editing/deletion
- User profiles with forum stats
- Notifications for replies
- Advanced search filters
- Calendar export (iCal)
- Recurring events
