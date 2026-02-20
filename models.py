from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# association table for users <-> teams (many-to-many)
team_members = db.Table(
    'team_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # basic account/profile
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    # contact & IDs
    mobile = db.Column(db.String(20))
    roll_number = db.Column(db.String(100))
    codechef = db.Column(db.String(100))
    hackerrank = db.Column(db.String(100))
    leetcode = db.Column(db.String(100))

    # profile fields
    bio = db.Column(db.Text)
    skills = db.Column(db.String(500))
    college = db.Column(db.String(200))
    branch = db.Column(db.String(200))
    year = db.Column(db.String(50))

    # uploads (store filenames)
    resume_filename = db.Column(db.String(300))
    certificates_filename = db.Column(db.String(300))

    # relationships & metadata
    projects = db.relationship('Project', backref='owner', lazy=True)
    teams = db.relationship('Team', secondary=team_members, back_populates='members')

    # admin flag
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    # privilege system (1=Admin, 2=Staff, 3=Coordinator, 4=Student/Default)
    privilege_level = db.Column(db.Integer, default=4, nullable=False)
    
    # forum moderation
    is_banned = db.Column(db.Boolean, default=False, nullable=False)
    is_silenced = db.Column(db.Boolean, default=False, nullable=False)
    silence_until = db.Column(db.DateTime, nullable=True)  # None = permanent silence

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Hashes and stores a password securely."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies a password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    github = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Project {self.title}>'

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)  # For multi-day events
    location = db.Column(db.String(200))
    poster = db.Column(db.String(300), nullable=True)  # Filename for event poster/image
    register_url = db.Column(db.String(500), nullable=True)  # Registration URL
    event_type = db.Column(db.String(50), default='general')  # general, exam, holiday, deadline, etc.
    color = db.Column(db.String(20), default='#007bff')  # Calendar color
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Admin who created it
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    creator = db.relationship('User', foreign_keys=[created_by])

    def __repr__(self):
        return f'<Event {self.title}>'

class Registration(db.Model):
    __tablename__ = 'registrations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('registrations', lazy='dynamic'))
    event = db.relationship('Event', backref=db.backref('registrations', lazy='dynamic'))

    def __repr__(self):
        return f'<Registration user={self.user_id} event={self.event_id}>'

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    # ✅ TEAM LEADER
    leader_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    leader = db.relationship('User', backref='leading_teams')

    # ✅ TEAM SIZE LIMIT
    size_limit = db.Column(db.Integer, default=4)

    # ✅ ASSOCIATED EVENT (nullable = "Others")
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=True)
    event = db.relationship('Event', backref='teams')

    # Members
    members = db.relationship('User', secondary=team_members, back_populates='teams')

    def __repr__(self):
        return f'<Team {self.name}>'


# ✅ JOIN REQUEST SYSTEM
class TeamJoinRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))   # person requesting
    status = db.Column(db.String(20), default="pending")

    team = db.relationship('Team', backref='join_requests')
    sender = db.relationship('User')


class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False, unique=True)
    description = db.Column(db.Text)
    contact = db.Column(db.String(200))      # phone or email
    faculty_incharge = db.Column(db.String(200))
    website = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Club {self.name}>'

class StudentChapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False, unique=True)
    associated_club = db.Column(db.String(250))  # optional string reference
    description = db.Column(db.Text)
    contact = db.Column(db.String(200))
    student_lead = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<StudentChapter {self.name}>'

class TeamInvite(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    team = db.relationship('Team', foreign_keys=[team_id])
    user = db.relationship('User', foreign_keys=[user_id])
    sender = db.relationship('User', foreign_keys=[sender_id])

    def __repr__(self):
        return f'<Invite team={self.team_id} user={self.user_id}>'


# -------------------------
# Forum Models (Reddit-style)
# -------------------------
class ForumCategory(db.Model):
    __tablename__ = 'forum_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    posts = db.relationship('ForumPost', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<ForumCategory {self.name}>'


class ForumPost(db.Model):
    __tablename__ = 'forum_posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('forum_categories.id'), nullable=True)
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)
    score = db.Column(db.Integer, default=0)  # upvotes - downvotes
    is_locked = db.Column(db.Boolean, default=False)
    is_pinned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    author = db.relationship('User', backref='forum_posts')
    comments = db.relationship('ForumComment', backref='post', lazy=True, cascade='all, delete-orphan')
    votes = db.relationship('ForumVote', backref='post', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ForumPost {self.title}>'


class ForumComment(db.Model):
    __tablename__ = 'forum_comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_posts.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('forum_comments.id'), nullable=True)  # For nested comments
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)
    score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    author = db.relationship('User', backref='forum_comments')
    parent = db.relationship('ForumComment', remote_side=[id], backref='replies')
    votes = db.relationship('ForumVote', backref='comment', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ForumComment {self.id}>'


class ForumVote(db.Model):
    __tablename__ = 'forum_votes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_posts.id'), nullable=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('forum_comments.id'), nullable=True)
    vote_type = db.Column(db.String(10), nullable=False)  # 'upvote' or 'downvote'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='forum_votes')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_post_vote'),
                      db.UniqueConstraint('user_id', 'comment_id', name='unique_comment_vote'))
    
    def __repr__(self):
        return f'<ForumVote {self.vote_type}>'


# -------------------------
# Direct Messages
# -------------------------
class DirectMessage(db.Model):
    __tablename__ = 'direct_messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

    def __repr__(self):
        return f'<DirectMessage {self.sender_id} -> {self.receiver_id}>'


# -------------------------
# Team Group Chat Messages
# -------------------------
class TeamMessage(db.Model):
    __tablename__ = 'team_messages'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    team = db.relationship('Team', backref=db.backref('messages', lazy='dynamic', order_by='TeamMessage.created_at'))
    sender = db.relationship('User', backref='team_messages')

    def __repr__(self):
        return f'<TeamMessage team={self.team_id} sender={self.sender_id}>'
