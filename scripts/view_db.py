"""
Quick Database Viewer
Shows a summary of all data in the database.
"""
from app import create_app
from models import (
    db, User, Project, Event, Team, Club, 
    StudentChapter, Registration, TeamJoinRequest, TeamInvite
)

app = create_app()

with app.app_context():
    print("=" * 70)
    print("CLOUDROOM DATABASE SUMMARY")
    print("=" * 70)
    
    # Users
    user_count = User.query.count()
    print(f"\n[USERS]: {user_count}")
    if user_count > 0:
        users = User.query.limit(5).all()
        for u in users:
            print(f"  - {u.username} ({u.email}) - {u.name}")
        if user_count > 5:
            print(f"  ... and {user_count - 5} more")
    
    # Projects
    project_count = Project.query.count()
    print(f"\n[PROJECTS]: {project_count}")
    if project_count > 0:
        projects = Project.query.limit(5).all()
        for p in projects:
            owner_name = p.owner.name if p.owner else "Unknown"
            print(f"  - {p.title} (by {owner_name})")
        if project_count > 5:
            print(f"  ... and {project_count - 5} more")
    
    # Events
    event_count = Event.query.count()
    print(f"\n[EVENTS]: {event_count}")
    if event_count > 0:
        events = Event.query.limit(5).all()
        for e in events:
            date_str = e.date.strftime("%Y-%m-%d") if e.date else "No date"
            print(f"  - {e.title} ({date_str})")
        if event_count > 5:
            print(f"  ... and {event_count - 5} more")
    
    # Teams
    team_count = Team.query.count()
    print(f"\n[TEAMS]: {team_count}")
    if team_count > 0:
        teams = Team.query.limit(5).all()
        for t in teams:
            member_count = len(t.members)
            leader_name = t.leader.name if t.leader else "Unknown"
            print(f"  - {t.name} (Leader: {leader_name}, Members: {member_count}/{t.size_limit})")
        if team_count > 5:
            print(f"  ... and {team_count - 5} more")
    
    # Clubs
    club_count = Club.query.count()
    print(f"\n[CLUBS]: {club_count}")
    if club_count > 0:
        clubs = Club.query.limit(5).all()
        for c in clubs:
            print(f"  - {c.name}")
        if club_count > 5:
            print(f"  ... and {club_count - 5} more")
    
    # Student Chapters
    chapter_count = StudentChapter.query.count()
    print(f"\n[STUDENT CHAPTERS]: {chapter_count}")
    if chapter_count > 0:
        chapters = StudentChapter.query.limit(5).all()
        for ch in chapters:
            print(f"  - {ch.name}")
        if chapter_count > 5:
            print(f"  ... and {chapter_count - 5} more")
    
    # Registrations
    reg_count = Registration.query.count()
    print(f"\n[REGISTRATIONS]: {reg_count}")
    
    # Team Join Requests
    join_req_count = TeamJoinRequest.query.filter_by(status='pending').count()
    print(f"\n[PENDING TEAM JOIN REQUESTS]: {join_req_count}")
    
    # Team Invites
    invite_count = TeamInvite.query.count()
    print(f"\n[TEAM INVITES]: {invite_count}")
    
    print("\n" + "=" * 70)
    print(f"Database file: instances/cloudroom.db")
    print("=" * 70)
