import os
import re
import io
import csv
from datetime import datetime, timedelta

from flask import (
    Flask, render_template, redirect, url_for, request, flash,
    send_from_directory, make_response, current_app, abort
)
from sqlalchemy import text
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user
)
from functools import wraps

from config import Config
from models import (
    db, User, Project, Event, Team, Club, StudentChapter, Registration,
    TeamJoinRequest, TeamInvite,
    ForumPost, ForumComment, ForumVote, ForumCategory,
    DirectMessage, TeamMessage
)

# -------------------------
# Validation regexes
# -------------------------
EMAIL_RE = re.compile(r"^[^@]+@[^@]+\.[^@]+$")
PASSWORD_RE = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$')
MOBILE_RE = re.compile(r'^\d{10}$')


# -------------------------
# Privilege System
# Level 1: Admin (all functions)
# Level 2: Staff (forum announcements, calendar events)
# Level 3: Coordinator (create events in events tab)
# Level 4: Student/Default (doubts, study posts only in forum)
# -------------------------
def privilege_required(required_level):
    """Decorator to require a minimum privilege level"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please login to access this feature.', 'warning')
                return redirect(url_for('login'))
            if current_user.privilege_level > required_level:
                flash(f'Access denied. Privilege level {required_level} or higher required.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.privilege_level != 1:
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    """Level 2 or higher (Staff, Admin)"""
    return privilege_required(2)(f)

def coordinator_required(f):
    """Level 3 or higher (Coordinator, Staff, Admin)"""
    return privilege_required(3)(f)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # sensible defaults
    if not app.config.get("ALLOWED_EXTENSIONS"):
        app.config["ALLOWED_EXTENSIONS"] = {"pdf", "png", "jpg", "jpeg"}
    if not app.config.get("UPLOAD_FOLDER"):
        app.config["UPLOAD_FOLDER"] = os.path.join(app.instance_path, "uploads")
    try:
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    except OSError:
        pass  # Vercel has read-only filesystem — skip directory creation

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'


    # Tables already created on Neon PostgreSQL — do NOT call db.create_all() here
    # as it conflicts with PostgreSQL's built-in 'user' type.

    # -------------------------
    # Helpers
    # -------------------------
    def allowed_file(filename):
        return bool(filename) and '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/hackathons')
    def hackathons():
        """Render the hackathons page."""
        return render_template('events/hackathons.html')
    # -------------------------
    # Core pages
    # -------------------------
    @app.route('/')
    def index():
        projects = Project.query.order_by(Project.created_at.desc()).limit(6).all()
        events = Event.query.order_by(Event.date).limit(5).all()
        return render_template('index.html', projects=projects, events=events)

    @app.route('/projects')
    def projects():
        all_projects = Project.query.order_by(Project.created_at.desc()).all()
        return render_template('projects/projects.html', projects=all_projects)

    @app.route('/project/<int:project_id>')
    def view_project(project_id):
        p = Project.query.get_or_404(project_id)
        return render_template('projects/project_detail.html', p=p)

    # -------------------------
    # Profile
    # -------------------------
    @app.route('/profile')
    @app.route('/profile/<int:user_id>')
    def profile(user_id=None):
        if user_id is None:
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            user = current_user
        else:
            user = User.query.get_or_404(user_id)
        return render_template('user/profile.html', user=user)

    @app.route('/user/<int:user_id>')
    def view_user(user_id):
        user = User.query.get_or_404(user_id)
        return render_template('user/view_user.html', user=user)

    @app.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
    def edit_user(user_id):
        user = User.query.get_or_404(user_id)
        if request.method == 'POST':
            user.name = request.form.get('name')
            user.email = request.form.get('email')
            user.mobile = request.form.get('mobile')
            user.roll_number = request.form.get('roll_number')
            user.college = request.form.get('college')
            user.branch = request.form.get('branch')
            user.year = request.form.get('year')
            user.skills = request.form.get('skills')
            user.codechef = request.form.get('codechef')
            user.hackerrank = request.form.get('hackerrank')
            user.leetcode = request.form.get('leetcode')
            db.session.commit()
            flash('User details updated successfully!', 'success')
            return redirect(url_for('view_user', user_id=user.id))
        return render_template('user/edit_user.html', user=user)

    @app.route('/profile_setup', methods=['GET', 'POST'])
    @login_required
    def profile_setup():
        user = current_user
        upload_folder = current_app.config.get('UPLOAD_FOLDER')
        if upload_folder:
            os.makedirs(upload_folder, exist_ok=True)

        if request.method == 'POST':
            college = request.form.get('college', '').strip()
            branch = request.form.get('branch', '').strip()
            year = request.form.get('year', '').strip()
            skills = request.form.get('skills', '').strip()

            if not all([college, branch, year, skills]):
                flash('Please fill all profile fields.', 'danger')
                return redirect(url_for('profile_setup'))

            resume = request.files.get('resume')
            certs = request.files.get('certificates')

            if resume and resume.filename:
                if not allowed_file(resume.filename):
                    flash('Resume must be a PDF or image.', 'danger')
                    return redirect(url_for('profile_setup'))
                resume_fn = secure_filename(f"{user.id}_resume_{resume.filename}")
                resume.save(os.path.join(upload_folder, resume_fn))
                user.resume_filename = resume_fn

            if certs and certs.filename:
                if not allowed_file(certs.filename):
                    flash('Certificates must be pdf/images.', 'danger')
                    return redirect(url_for('profile_setup'))
                certs_fn = secure_filename(f"{user.id}_certs_{certs.filename}")
                certs.save(os.path.join(upload_folder, certs_fn))
                user.certificates_filename = certs_fn

            user.college = college
            user.branch = branch
            user.year = year
            user.skills = skills
            db.session.commit()
            flash('Profile setup complete! Welcome to CloudRoom 🎉', 'success')
            return redirect(url_for('profile'))

        return render_template('auth/profile_setup.html', user=user)

    # -------------------------
    # Events
    # -------------------------
    @app.route('/events')
    def events():
        upcoming = Event.query.order_by(Event.date).all()
        return render_template('events/events.html', events=upcoming)

    @app.route('/events/create', methods=['GET', 'POST'])
    @coordinator_required
    def create_event():
        """Level 3+ (Coordinators, Staff, Admin) can create events"""
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            date_str = request.form.get('date', '').strip()
            location = request.form.get('location', '').strip()
            register_url = request.form.get('register_url', '').strip()
            
            if not title or not date_str:
                flash('Title and date are required.', 'danger')
                return redirect(url_for('create_event'))
            
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format.', 'danger')
                return redirect(url_for('create_event'))
            
            # Handle image upload
            poster_filename = None
            if 'poster' in request.files:
                poster_file = request.files['poster']
                if poster_file and poster_file.filename:
                    if allowed_file(poster_file.filename):
                        poster_filename = secure_filename(f"event_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{poster_file.filename}")
                        images_folder = os.path.join(current_app.static_folder, 'images')
                        os.makedirs(images_folder, exist_ok=True)
                        poster_file.save(os.path.join(images_folder, poster_filename))
                    else:
                        flash('Invalid file type. Only images (png, jpg, jpeg) are allowed.', 'danger')
                        return redirect(url_for('create_event'))
            
            event = Event(
                title=title,
                description=description,
                date=date,
                location=location,
                poster=poster_filename,
                register_url=register_url if register_url else None,
                event_type='general',
                color='#007bff',
                created_by=current_user.id
            )
            db.session.add(event)
            db.session.commit()
            flash('Event created successfully!', 'success')
            return redirect(url_for('events'))
        
        return render_template('events/create_event.html')

    @app.route('/my_registrations')
    @login_required
    def my_registrations():
        try:
            regs = current_user.registrations.order_by(Registration.created_at.desc()).all()
        except Exception:
            regs = []
        return render_template('events/my_registrations.html', registrations=regs)

    @app.route('/register_event/<int:event_id>', methods=['POST'])
    @login_required
    def register_event(event_id):
        ev = Event.query.get_or_404(event_id)
        existing = Registration.query.filter_by(user_id=current_user.id, event_id=ev.id).first()
        if existing:
            flash('You have already registered for this event.', 'info')
            return redirect(url_for('my_registrations'))
        reg = Registration(user_id=current_user.id, event_id=ev.id)
        db.session.add(reg)
        db.session.commit()
        flash('Registration saved. Redirecting to event form...', 'success')
        if getattr(ev, 'register_url', None):
            return redirect(ev.register_url)
        return redirect(url_for('my_registrations'))

    @app.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
    @coordinator_required
    def edit_event(event_id):
        """Level 3+ can edit events. Level 3 only their own; Level 2+ any event."""
        event = Event.query.get_or_404(event_id)

        # Level 3 (Coordinator) can only edit their own events
        if current_user.privilege_level == 3 and event.created_by != current_user.id:
            flash('You can only edit events you created.', 'danger')
            return redirect(url_for('events'))

        if request.method == 'POST':
            event.title = request.form.get('title', event.title).strip()
            event.description = request.form.get('description', event.description or '').strip()
            date_str = request.form.get('date', '').strip()
            event.location = request.form.get('location', event.location or '').strip()
            event.register_url = request.form.get('register_url', event.register_url or '').strip() or None

            if date_str:
                try:
                    event.date = datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    flash('Invalid date format.', 'danger')
                    return redirect(url_for('edit_event', event_id=event_id))

            # Handle image upload
            if 'poster' in request.files:
                poster_file = request.files['poster']
                if poster_file and poster_file.filename:
                    if allowed_file(poster_file.filename):
                        poster_filename = secure_filename(f"event_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{poster_file.filename}")
                        images_folder = os.path.join(current_app.static_folder, 'images')
                        os.makedirs(images_folder, exist_ok=True)
                        poster_file.save(os.path.join(images_folder, poster_filename))
                        event.poster = poster_filename
                    else:
                        flash('Invalid file type. Only images (png, jpg, jpeg) are allowed.', 'danger')
                        return redirect(url_for('edit_event', event_id=event_id))

            db.session.commit()
            flash('Event updated successfully!', 'success')
            return redirect(url_for('events'))

        return render_template('events/edit_event.html', event=event)

    @app.route('/events/<int:event_id>/delete', methods=['POST'])
    @coordinator_required
    def delete_event(event_id):
        """Level 3+ can delete events. Level 3 only their own; Level 2+ any event."""
        event = Event.query.get_or_404(event_id)

        # Level 3 (Coordinator) can only delete their own events
        if current_user.privilege_level == 3 and event.created_by != current_user.id:
            flash('You can only delete events you created.', 'danger')
            return redirect(url_for('events'))

        # Delete associated registrations first
        Registration.query.filter_by(event_id=event_id).delete()
        db.session.delete(event)
        db.session.commit()
        flash('Event deleted successfully!', 'success')
        return redirect(url_for('events'))

    # -------------------------
    # Clubs / Chapters
    # -------------------------
    @app.route('/clubs')
    def clubs():
        clubs_ = Club.query.order_by(Club.name).all()
        return render_template('community/clubs.html', clubs=clubs_)

    @app.route('/clubs/<int:club_id>')
    def club_detail(club_id):
        club = Club.query.get(club_id)
        if not club:
            abort(404)

        def normalize_url(u):
            if not u:
                return u
            u = u.strip()
            if not u.startswith(('http://', 'https://')):
                return 'https://' + u
            return u

        club.contact = normalize_url(club.contact)
        club.website = normalize_url(club.website)
        return render_template('community/club_detail.html', club=club)

    @app.route('/chapters')
    def chapters():
        chapters_ = StudentChapter.query.order_by(StudentChapter.name).all()
        return render_template('community/chapters.html', chapters=chapters_)

    @app.route('/chapters/<int:chapter_id>')
    def chapter_detail(chapter_id):
        chapter = StudentChapter.query.get(chapter_id)
        if not chapter:
            abort(404)
        contact = (chapter.contact or "").strip()
        if contact and not contact.startswith(('http://', 'https://')):
            contact = 'https://' + contact
        chapter.contact = contact
        return render_template('community/chapter_detail.html', chapter=chapter)

    # -------------------------
    # ProjectHub
    # -------------------------
    @app.route('/projecthub')
    def projecthub():
        all_projects = Project.query.order_by(Project.created_at.desc()).all()
        return render_template('projects/projecthub.html', projects=all_projects)

    @app.route('/create_project', methods=['GET', 'POST'])
    def create_project():
        if request.method == 'POST':
            title = request.form.get('title')
            description = request.form.get('description')
            github = request.form.get('github')
            owner_email = request.form.get('owner_email')

            owner = User.query.filter_by(email=owner_email).first()
            if not owner:
                owner = User(name=owner_email.split('@')[0], email=owner_email)
                db.session.add(owner)
                db.session.commit()

            p = Project(title=title, description=description, github=github, owner=owner)
            db.session.add(p)
            db.session.commit()
            flash('Project created', 'success')
            return redirect(url_for('projects'))

        return render_template('projects/create_project.html')

    @app.route('/upload_project', methods=['GET', 'POST'])
    @login_required
    def upload_project():
        if request.method == 'POST':
            title = request.form.get('title')
            idea = request.form.get('idea')
            tech = request.form.get('tech')
            github = request.form.get('github')
            demo = request.form.get('demo')

            if not title or not idea:
                flash("Project title and idea are required.", "danger")
                return redirect(url_for('upload_project'))

            p = Project(
                title=title,
                description=idea + (f"\n\nTech Stack: {tech}" if tech else ""),
                github=github,
                owner=current_user
            )
            if demo:
                p.description += f"\n\nDemo Video: {demo}"

            db.session.add(p)
            db.session.commit()
            flash("Project uploaded successfully!", "success")
            return redirect(url_for('projecthub'))

        return render_template('projects/upload_project.html')

    # -------------------------
    # TeamUp
    # -------------------------
    @app.route('/teamup')
    def teamup():
        teams = Team.query.order_by(Team.id.desc()).all()
        return render_template('teams/teamup.html', teams=teams)

    # NOTE: keep only ONE create-team endpoint (no duplicates!)
    @app.route('/team/create', methods=['GET', 'POST'])
    @login_required
    def team_create():
        if request.method == 'POST':
            name = request.form['name'].strip()
            description = request.form.get('description', '').strip()
            size_limit = int(request.form.get('size_limit', '4'))
            event_id = request.form.get('event_id', '').strip()

            if not name:
                flash("Team name is required.", "danger")
                return redirect(url_for('team_create'))

            team = Team(
                name=name,
                description=description,
                leader_id=current_user.id,
                size_limit=size_limit,
                event_id=int(event_id) if event_id else None
            )
            # creator joins as first member
            team.members.append(current_user)

            db.session.add(team)
            db.session.commit()
            flash("Team created successfully!", "success")
            return redirect(url_for('teamup'))

        # Fetch upcoming/ongoing events for dropdown
        upcoming_events = Event.query.filter(Event.date >= datetime.utcnow()).order_by(Event.date).all()
        return render_template('teams/create_team.html', events=upcoming_events)

    @app.route('/teamup/<int:team_id>')
    def view_team(team_id):
        team = Team.query.get_or_404(team_id)
        # pending join requests for this team (leader will see controls on page)
        pending_requests = TeamJoinRequest.query.filter_by(team_id=team.id, status='pending').all()
        return render_template('teams/view_team.html', team=team, pending_requests=pending_requests)

    # ----- Team Group Chat -----
    @app.route('/teamup/<int:team_id>/chat', methods=['GET', 'POST'])
    @login_required
    def team_chat(team_id):
        team = Team.query.get_or_404(team_id)
        # Only team members can access the chat
        if current_user not in team.members:
            flash("You must be a team member to access the group chat.", "warning")
            return redirect(url_for('view_team', team_id=team_id))

        if request.method == 'POST':
            content = request.form.get('content', '').strip()
            if content:
                msg = TeamMessage(
                    team_id=team.id,
                    sender_id=current_user.id,
                    content=content
                )
                db.session.add(msg)
                db.session.commit()
            return redirect(url_for('team_chat', team_id=team_id))

        messages = TeamMessage.query.filter_by(team_id=team.id)\
            .order_by(TeamMessage.created_at.asc()).all()
        return render_template('teams/team_chat.html', team=team, messages=messages)

    # ----- Invite flow (invite by username) -----
    @app.route('/teamup/<int:team_id>/invite', methods=['POST'])
    @login_required
    def invite_user(team_id):
        team = Team.query.get_or_404(team_id)

        # only leader can invite (optional; remove if not required)
        if current_user.id != team.leader_id:
            abort(403)

        username = request.form.get("username", "").strip()
        user = User.query.filter_by(username=username).first()
        if not user:
            flash("User not found.", "danger")
            return redirect(url_for('view_team', team_id=team_id))

        if user in team.members:
            flash("User is already in the team.", "info")
            return redirect(url_for('view_team', team_id=team_id))

        existing = TeamInvite.query.filter_by(team_id=team.id, user_id=user.id).first()
        if existing:
            flash("User already invited.", "warning")
            return redirect(url_for('view_team', team_id=team_id))

        invite = TeamInvite(team_id=team.id, user_id=user.id, sender_id=current_user.id)
        db.session.add(invite)
        db.session.commit()
        flash("Invitation sent.", "success")
        return redirect(url_for('view_team', team_id=team_id))

    @app.route('/teamup/invitations')
    @login_required
    def team_invitations():
        invites = TeamInvite.query.filter_by(user_id=current_user.id).all()
        return render_template('teams/team_invitations.html', invites=invites)

    @app.route('/teamup/invite/<int:invite_id>/accept')
    @login_required
    def accept_invite(invite_id):
        invite = TeamInvite.query.get_or_404(invite_id)
        team = invite.team
        # size limit check
        if len(team.members) >= team.size_limit:
            flash("Team is full!", "danger")
            return redirect(url_for('team_invitations'))
        team.members.append(current_user)
        db.session.delete(invite)
        db.session.commit()
        flash("You joined the team!", "success")
        return redirect(url_for('teamup'))

    @app.route('/teamup/invite/<int:invite_id>/reject')
    @login_required
    def reject_invite(invite_id):
        invite = TeamInvite.query.get_or_404(invite_id)
        db.session.delete(invite)
        db.session.commit()
        flash("Invitation rejected.", "info")
        return redirect(url_for('team_invitations'))

    # ----- Join request flow (user asks to join; leader accepts/rejects) -----
    @app.route('/team/<int:team_id>/join', methods=['POST'])
    @login_required
    def request_join(team_id):
        team = Team.query.get_or_404(team_id)

        if current_user in team.members:
            flash("You are already in this team!", "info")
            return redirect(url_for('view_team', team_id=team_id))

        if len(team.members) >= team.size_limit:
            flash("Team is full!", "danger")
            return redirect(url_for('view_team', team_id=team_id))

        existing = TeamJoinRequest.query.filter_by(
            team_id=team_id, sender_id=current_user.id, status='pending'
        ).first()
        if existing:
            flash("Join request already sent!", "warning")
            return redirect(url_for('view_team', team_id=team_id))

        req = TeamJoinRequest(team_id=team_id, sender_id=current_user.id, status='pending')
        db.session.add(req)
        db.session.commit()
        flash("Join request sent!", "success")
        return redirect(url_for('view_team', team_id=team_id))

    @app.route('/team/join/<int:req_id>/accept')
    @login_required
    def accept_join(req_id):
        req = TeamJoinRequest.query.get_or_404(req_id)
        team = req.team

        if current_user.id != team.leader_id:
            abort(403)

        if len(team.members) >= team.size_limit:
            flash("Cannot accept — team is full!", "danger")
            return redirect(url_for('view_team', team_id=team.id))

        team.members.append(req.sender)
        req.status = "accepted"
        db.session.commit()
        flash("Member added!", "success")
        return redirect(url_for('view_team', team_id=team.id))

    @app.route('/team/join/<int:req_id>/reject')
    @login_required
    def reject_join(req_id):
        req = TeamJoinRequest.query.get_or_404(req_id)
        team = req.team
        if current_user.id != team.leader_id:
            abort(403)
        req.status = "rejected"
        db.session.commit()
        flash("Request rejected.", "info")
        return redirect(url_for('view_team', team_id=team.id))

    # -------------------------
    # Auth
    # -------------------------
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('auth/login.html')

        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username_or_email or not password:
            flash('Please enter username/email and password', 'warning')
            return redirect(url_for('login'))

        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid username/email or password', 'danger')
            return redirect(url_for('login'))

        login_user(user)
        flash('Logged in successfully', 'success')
        next_page = request.args.get('next')
        return redirect(next_page or url_for('profile'))

    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        if request.method == 'GET':
            return render_template('admin/admin_login.html')
        
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username_or_email or not password:
            flash('Please enter username/email and password', 'warning')
            return redirect(url_for('admin_login'))
        
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid credentials', 'danger')
            return redirect(url_for('admin_login'))
        
        if not user.is_admin:
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('admin_login'))
        
        login_user(user)
        flash('Admin login successful', 'success')
        return redirect(url_for('admin_dashboard'))

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Logged out successfully.', 'info')
        return redirect(url_for('index'))

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            mobile = request.form.get('mobile', '').strip()
            email = request.form.get('email', '').strip()
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')

            if not all([name, mobile, email, username, password]):
                flash('Please fill all required fields.', 'danger')
                return redirect(url_for('signup'))

            if not MOBILE_RE.match(mobile):
                flash('Mobile must be exactly 10 digits.', 'danger')
                return redirect(url_for('signup'))

            if not EMAIL_RE.match(email):
                flash('Invalid email address.', 'danger')
                return redirect(url_for('signup'))

            if not PASSWORD_RE.match(password):
                flash('Password must be at least 8 chars incl. upper, lower, number & special char.', 'danger')
                return redirect(url_for('signup'))

            if User.query.filter_by(email=email).first():
                flash('Email already registered.', 'danger')
                return redirect(url_for('signup'))
            if User.query.filter_by(username=username).first():
                flash('Username already taken.', 'danger')
                return redirect(url_for('signup'))

            user = User(name=name, mobile=mobile, email=email, username=username)
            user.password_hash = generate_password_hash(password)
            db.session.add(user)
            db.session.commit()

            login_user(user)
            flash('Account created and logged in. Welcome!', 'success')
            try:
                return redirect(url_for('profile_setup', user_id=user.id))
            except Exception:
                return redirect(url_for('profile'))

        return render_template('auth/signup.html')

    # -------------------------
    # Files / exports
    # -------------------------
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        upload_folder = current_app.config.get('UPLOAD_FOLDER')
        if not upload_folder:
            abort(404)
        return send_from_directory(upload_folder, filename, as_attachment=False)

    # -------------------------
    # Admin Routes
    # -------------------------
    @app.route('/admin')
    @admin_required
    def admin_dashboard():
        user_count = User.query.count()
        project_count = Project.query.count()
        event_count = Event.query.count()
        team_count = Team.query.count()
        club_count = Club.query.count()
        chapter_count = StudentChapter.query.count()
        
        users = User.query.order_by(User.created_at.desc()).limit(10).all()
        
        return render_template('admin/admin_dashboard.html',
                             user_count=user_count,
                             project_count=project_count,
                             event_count=event_count,
                             team_count=team_count,
                             club_count=club_count,
                             chapter_count=chapter_count,
                             recent_users=users)

    @app.route('/admin/users')
    @admin_required
    def admin_list_users():
        users = User.query.order_by(User.created_at.desc()).all()
        return render_template('admin/admin_users.html', users=users)

    @app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
    @admin_required
    def admin_delete_user(user_id):
        if user_id == current_user.id:
            flash('You cannot delete your own account.', 'danger')
            return redirect(url_for('admin_list_users'))
        
        user = User.query.get_or_404(user_id)
        
        # Delete user's projects
        Project.query.filter_by(owner_id=user_id).delete()
        
        # Remove user from teams
        for team in user.teams:
            team.members.remove(user)
            # If user was team leader, reassign or delete team
            if team.leader_id == user_id:
                if len(team.members) > 0:
                    team.leader_id = team.members[0].id
                else:
                    db.session.delete(team)
        
        # Delete team invites and join requests
        TeamInvite.query.filter_by(user_id=user_id).delete()
        TeamInvite.query.filter_by(sender_id=user_id).delete()
        TeamJoinRequest.query.filter_by(sender_id=user_id).delete()
        
        # Delete registrations
        Registration.query.filter_by(user_id=user_id).delete()
        
        # Delete user
        db.session.delete(user)
        db.session.commit()
        
        flash(f'User {user.username} has been deleted.', 'success')
        return redirect(url_for('admin_list_users'))

    @app.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
    @admin_required
    def admin_edit_user(user_id):
        user = User.query.get_or_404(user_id)
        
        if request.method == 'POST':
            user.name = request.form.get('name', user.name)
            user.email = request.form.get('email', user.email)
            user.username = request.form.get('username', user.username)
            user.mobile = request.form.get('mobile', user.mobile)
            user.roll_number = request.form.get('roll_number', user.roll_number)
            user.college = request.form.get('college', user.college)
            user.branch = request.form.get('branch', user.branch)
            user.year = request.form.get('year', user.year)
            user.skills = request.form.get('skills', user.skills)
            user.codechef = request.form.get('codechef', user.codechef)
            user.hackerrank = request.form.get('hackerrank', user.hackerrank)
            user.leetcode = request.form.get('leetcode', user.leetcode)
            
            # Update admin status
            is_admin = request.form.get('is_admin') == 'on'
            if user_id != current_user.id:  # Prevent self-demotion
                user.is_admin = is_admin
            
            # Update privilege level
            privilege_level = request.form.get('privilege_level', type=int)
            if privilege_level and privilege_level in [1, 2, 3, 4]:
                if user_id != current_user.id or privilege_level == 1:  # Can't demote self unless to admin
                    user.privilege_level = privilege_level
                    # Sync admin status with privilege level
                    if privilege_level == 1:
                        user.is_admin = True
                    elif privilege_level > 1 and not current_user.is_admin:
                        user.is_admin = False
            
            # Update password if provided
            new_password = request.form.get('password', '').strip()
            if new_password:
                if PASSWORD_RE.match(new_password):
                    user.password_hash = generate_password_hash(new_password)
                else:
                    flash('Password must be at least 8 chars incl. upper, lower, number & special char.', 'danger')
                    return redirect(url_for('admin_edit_user', user_id=user_id))
            
            db.session.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('admin_list_users'))
        
        return render_template('admin/admin_edit_user.html', user=user)

    @app.route('/admin/team/<int:team_id>/kick/<int:user_id>', methods=['POST'])
    @admin_required
    def admin_kick_user_from_team(team_id, user_id):
        team = Team.query.get_or_404(team_id)
        user = User.query.get_or_404(user_id)
        
        if user not in team.members:
            flash('User is not a member of this team.', 'warning')
            return redirect(url_for('view_team', team_id=team_id))
        
        # Don't allow kicking team leader
        if team.leader_id == user_id:
            flash('Cannot kick team leader. Assign a new leader first.', 'danger')
            return redirect(url_for('view_team', team_id=team_id))
        
        team.members.remove(user)
        db.session.commit()
        
        flash(f'{user.username} has been removed from {team.name}.', 'success')
        return redirect(url_for('view_team', team_id=team_id))

    @app.route('/search')
    def search_users():
        q = request.args.get('q', '').strip()
        results = []
        if q:
            search = f'%{q}%'
            results = User.query.filter(
                (User.name.ilike(search)) |
                (User.username.ilike(search)) |
                (User.skills.ilike(search))
            ).order_by(User.name).limit(50).all()
        return render_template('user/search_results.html', query=q, results=results)

    @app.route('/users')
    @admin_required
    def list_users():
        users = User.query.order_by(User.created_at.desc()).all()
        return render_template('user/users.html', users=users)

    @app.route('/export_users')
    @admin_required
    def export_users():
        users = User.query.order_by(User.id).all()
        fieldnames = [
            'id','username','name','email','mobile','roll_number',
            'codechef','hackerrank','leetcode',
            'college','branch','year','skills',
            'resume_filename','certificates_filename','created_at'
        ]
        si = io.StringIO()
        writer = csv.DictWriter(si, fieldnames=fieldnames)
        writer.writeheader()
        for u in users:
            writer.writerow({
                'id': u.id,
                'username': u.username,
                'name': u.name,
                'email': u.email,
                'mobile': u.mobile or '',
                'roll_number': u.roll_number or '',
                'codechef': getattr(u, 'codechef', '') or '',
                'hackerrank': getattr(u, 'hackerrank', '') or '',
                'leetcode': getattr(u, 'leetcode', '') or '',
                'college': u.college or '',
                'branch': u.branch or '',
                'year': u.year or '',
                'skills': u.skills or '',
                'resume_filename': getattr(u, 'resume_filename', '') or '',
                'certificates_filename': getattr(u, 'certificates_filename', '') or '',
                'created_at': u.created_at.isoformat() if getattr(u, 'created_at', None) else '',
            })
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=cloudroom_users.csv"
        output.headers["Content-type"] = "text/csv"
        return output

    # -------------------------
    # Direct Messages
    # -------------------------
    @app.context_processor
    def inject_unread_count():
        """Make unread message count available in all templates."""
        if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
            count = DirectMessage.query.filter_by(
                receiver_id=current_user.id, is_read=False
            ).count()
            return {'unread_msg_count': count}
        return {'unread_msg_count': 0}

    @app.route('/messages')
    @login_required
    def inbox():
        """Show all conversations grouped by the other user."""
        # Get all users the current user has exchanged messages with
        from sqlalchemy import or_, case, func

        # Subquery: for each conversation partner, get the latest message time
        sent = db.session.query(
            DirectMessage.receiver_id.label('partner_id'),
            func.max(DirectMessage.created_at).label('last_time')
        ).filter(DirectMessage.sender_id == current_user.id).group_by(DirectMessage.receiver_id)

        received = db.session.query(
            DirectMessage.sender_id.label('partner_id'),
            func.max(DirectMessage.created_at).label('last_time')
        ).filter(DirectMessage.receiver_id == current_user.id).group_by(DirectMessage.sender_id)

        # Union and get max per partner
        all_convos = sent.union_all(received).subquery()
        partners = db.session.query(
            all_convos.c.partner_id,
            func.max(all_convos.c.last_time).label('last_time')
        ).group_by(all_convos.c.partner_id).order_by(func.max(all_convos.c.last_time).desc()).all()

        conversations = []
        for partner_id, last_time in partners:
            partner = User.query.get(partner_id)
            if not partner:
                continue
            # Count unread from this partner
            unread = DirectMessage.query.filter_by(
                sender_id=partner_id, receiver_id=current_user.id, is_read=False
            ).count()
            # Get last message preview
            last_msg = DirectMessage.query.filter(
                ((DirectMessage.sender_id == current_user.id) & (DirectMessage.receiver_id == partner_id)) |
                ((DirectMessage.sender_id == partner_id) & (DirectMessage.receiver_id == current_user.id))
            ).order_by(DirectMessage.created_at.desc()).first()
            conversations.append({
                'partner': partner,
                'last_time': last_time,
                'unread': unread,
                'last_message': last_msg.content[:80] if last_msg else ''
            })

        return render_template('messaging/inbox.html', conversations=conversations)

    @app.route('/messages/<int:user_id>', methods=['GET', 'POST'])
    @login_required
    def conversation(user_id):
        """View conversation with a specific user and send messages."""
        other_user = User.query.get_or_404(user_id)
        if other_user.id == current_user.id:
            flash("You can't message yourself.", 'warning')
            return redirect(url_for('inbox'))

        if request.method == 'POST':
            content = request.form.get('content', '').strip()
            if content:
                msg = DirectMessage(
                    sender_id=current_user.id,
                    receiver_id=other_user.id,
                    content=content
                )
                db.session.add(msg)
                db.session.commit()
            return redirect(url_for('conversation', user_id=user_id))

        # Mark incoming messages as read
        DirectMessage.query.filter_by(
            sender_id=other_user.id, receiver_id=current_user.id, is_read=False
        ).update({'is_read': True})
        db.session.commit()

        # Fetch all messages between these two users
        messages = DirectMessage.query.filter(
            ((DirectMessage.sender_id == current_user.id) & (DirectMessage.receiver_id == other_user.id)) |
            ((DirectMessage.sender_id == other_user.id) & (DirectMessage.receiver_id == current_user.id))
        ).order_by(DirectMessage.created_at.asc()).all()

        return render_template('messaging/conversation.html', other_user=other_user, messages=messages)

    @app.route('/messages/<int:user_id>/send', methods=['POST'])
    @login_required
    def send_message(user_id):
        """Quick send message from another page (e.g. user profile)."""
        other_user = User.query.get_or_404(user_id)
        if other_user.id == current_user.id:
            flash("You can't message yourself.", 'warning')
            return redirect(url_for('inbox'))

        content = request.form.get('content', '').strip()
        if not content:
            flash('Message cannot be empty.', 'danger')
            return redirect(url_for('conversation', user_id=user_id))

        msg = DirectMessage(
            sender_id=current_user.id,
            receiver_id=other_user.id,
            content=content
        )
        db.session.add(msg)
        db.session.commit()
        flash('Message sent!', 'success')
        return redirect(url_for('conversation', user_id=user_id))

    # -------------------------
    # Leaderboard (sample)
    # -------------------------
    LEADERBOARD_QUERY = """
    WITH per_user AS (
      SELECT
        u.id AS user_id,
        u.username,
        COALESCE(MAX(CASE WHEN p.slug = 'hackerrank' THEN ps.score END), 0) AS hackerrank_score,
        COALESCE(MAX(CASE WHEN p.slug = 'codechef'   THEN ps.score END), 0) AS codechef_score,
        COALESCE(MAX(CASE WHEN p.slug = 'leetcode'   THEN ps.score END), 0) AS leetcode_score
      FROM users u
      LEFT JOIN platform_scores ps ON ps.user_id = u.id
      LEFT JOIN platforms p ON p.id = ps.platform_id
      GROUP BY u.id, u.username
    ),
    with_total AS (
      SELECT
        user_id, username,
        hackerrank_score, codechef_score, leetcode_score,
        (hackerrank_score + codechef_score + leetcode_score) AS total_score
      FROM per_user
    )
    SELECT
      user_id, username,
      hackerrank_score, codechef_score, leetcode_score,
      total_score,
      RANK() OVER (ORDER BY total_score DESC) AS rank
    FROM with_total
    ORDER BY total_score DESC
    LIMIT :limit OFFSET :offset;
    """

    @app.route("/leaderboard")
    def leaderboard():
        limit = 100
        offset = 0
        rows = []
        try:
            res = db.session.execute(text(LEADERBOARD_QUERY), {"limit": limit, "offset": offset})
            rows = [dict(r) for r in res.mappings().all()]
        except Exception:
            app.logger.exception("Leaderboard query failed; returning empty list.")
            rows = []
        return render_template("leaderboard/leaderboard.html", rows=rows)

    # -------------------------
    # Forum Routes (Reddit-style)
    # -------------------------
    @app.route('/forum')
    def forum():
        category_id = request.args.get('category', type=int)
        search_query = request.args.get('search', '').strip()
        
        query = ForumPost.query
        if category_id:
            query = query.filter_by(category_id=category_id)
        if search_query:
            query = query.filter(
                (ForumPost.title.contains(search_query)) |
                (ForumPost.content.contains(search_query))
            )
        
        posts = query.order_by(ForumPost.score.desc(), ForumPost.created_at.desc()).limit(50).all()
        categories = ForumCategory.query.order_by(ForumCategory.name).all()
        
        return render_template('forum/forum.html', posts=posts, categories=categories, 
                             selected_category=category_id, search_query=search_query)

    @app.route('/forum/post/<int:post_id>')
    def view_post(post_id):
        post = ForumPost.query.get_or_404(post_id)
        # Get top-level comments and their replies
        comments = ForumComment.query.filter_by(post_id=post_id, parent_id=None).order_by(ForumComment.score.desc(), ForumComment.created_at).all()
        # Load replies for each comment
        for comment in comments:
            comment.replies = ForumComment.query.filter_by(parent_id=comment.id).order_by(ForumComment.created_at).all()
        return render_template('forum/forum_post.html', post=post, comments=comments)

    @app.route('/forum/create', methods=['GET', 'POST'])
    @login_required
    def create_post():
        if current_user.is_banned:
            flash('You are banned from the forum.', 'danger')
            return redirect(url_for('forum'))
        
        if current_user.is_silenced:
            if current_user.silence_until and current_user.silence_until > datetime.utcnow():
                flash('You are silenced from posting until ' + current_user.silence_until.strftime('%Y-%m-%d %H:%M'), 'danger')
                return redirect(url_for('forum'))
            elif not current_user.silence_until:
                flash('You are permanently silenced from posting.', 'danger')
                return redirect(url_for('forum'))
            else:
                # Silence expired
                current_user.is_silenced = False
                current_user.silence_until = None
                db.session.commit()
        
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            category_id = request.form.get('category_id', type=int) or None
            
            if not title or not content:
                flash('Title and content are required.', 'danger')
                return redirect(url_for('create_post'))
            
            # Level 4 users (students) can only post in Questions, Study, or Doubts categories
            if current_user.privilege_level == 4:
                if category_id:
                    category = ForumCategory.query.get(category_id)
                    allowed_categories = ['questions', 'study', 'doubts']
                    if category and category.name.lower() not in allowed_categories:
                        flash('Students can only post in Questions, Study, or Doubts categories.', 'danger')
                        return redirect(url_for('create_post'))
                else:
                    flash('Students must select a category (Questions, Study, or Doubts).', 'danger')
                    return redirect(url_for('create_post'))
            
            # Level 2+ users can post in Announcements category (forum-wide announcements)
            if current_user.privilege_level <= 2 and category_id:
                category = ForumCategory.query.get(category_id)
                if category and category.name.lower() == 'announcements':
                    # Staff and Admin can post announcements
                    pass  # Allow it
            
            post = ForumPost(
                title=title,
                content=content,
                author_id=current_user.id,
                category_id=category_id
            )
            db.session.add(post)
            db.session.commit()
            flash('Post created successfully!', 'success')
            return redirect(url_for('view_post', post_id=post.id))
        
        # Filter categories based on privilege level
        all_categories = ForumCategory.query.order_by(ForumCategory.name).all()
        if current_user.privilege_level == 4:
            # Level 4 can only see Questions, Study, Doubts
            categories = [c for c in all_categories if c.name.lower() in ['questions', 'study', 'doubts']]
        elif current_user.privilege_level == 3:
            # Level 3 can see all except Announcements
            categories = [c for c in all_categories if c.name.lower() != 'announcements']
        else:
            # Level 1 and 2 can see all categories (including Announcements)
            categories = all_categories
        
        return render_template('forum/create_post.html', categories=categories, user_level=current_user.privilege_level)

    @app.route('/forum/post/<int:post_id>/comment', methods=['POST'])
    @login_required
    def add_comment(post_id):
        if current_user.is_banned:
            flash('You are banned from the forum.', 'danger')
            return redirect(url_for('view_post', post_id=post_id))
        
        if current_user.is_silenced:
            if current_user.silence_until and current_user.silence_until > datetime.utcnow():
                flash('You are silenced from commenting.', 'danger')
                return redirect(url_for('view_post', post_id=post_id))
            elif not current_user.silence_until:
                flash('You are permanently silenced from commenting.', 'danger')
                return redirect(url_for('view_post', post_id=post_id))
            else:
                current_user.is_silenced = False
                current_user.silence_until = None
                db.session.commit()
        
        post = ForumPost.query.get_or_404(post_id)
        if post.is_locked:
            flash('This post is locked.', 'danger')
            return redirect(url_for('view_post', post_id=post_id))
        
        content = request.form.get('content', '').strip()
        parent_id = request.form.get('parent_id', type=int) or None
        
        if not content:
            flash('Comment cannot be empty.', 'danger')
            return redirect(url_for('view_post', post_id=post_id))
        
        comment = ForumComment(
            content=content,
            author_id=current_user.id,
            post_id=post_id,
            parent_id=parent_id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Comment added!', 'success')
        return redirect(url_for('view_post', post_id=post_id))

    @app.route('/forum/post/<int:post_id>/vote', methods=['POST'])
    @login_required
    def vote_post(post_id):
        vote_type = request.form.get('vote_type')  # 'upvote' or 'downvote'
        post = ForumPost.query.get_or_404(post_id)
        
        existing_vote = ForumVote.query.filter_by(user_id=current_user.id, post_id=post_id).first()
        
        if existing_vote:
            if existing_vote.vote_type == vote_type:
                # Remove vote
                db.session.delete(existing_vote)
                if vote_type == 'upvote':
                    post.upvotes = max(0, post.upvotes - 1)
                else:
                    post.downvotes = max(0, post.downvotes - 1)
            else:
                # Change vote
                if existing_vote.vote_type == 'upvote':
                    post.upvotes = max(0, post.upvotes - 1)
                    post.downvotes += 1
                else:
                    post.downvotes = max(0, post.downvotes - 1)
                    post.upvotes += 1
                existing_vote.vote_type = vote_type
        else:
            # New vote
            vote = ForumVote(user_id=current_user.id, post_id=post_id, vote_type=vote_type)
            db.session.add(vote)
            if vote_type == 'upvote':
                post.upvotes += 1
            else:
                post.downvotes += 1
        
        post.score = post.upvotes - post.downvotes
        db.session.commit()
        return redirect(url_for('view_post', post_id=post_id))

    @app.route('/forum/comment/<int:comment_id>/vote', methods=['POST'])
    @login_required
    def vote_comment(comment_id):
        vote_type = request.form.get('vote_type')
        comment = ForumComment.query.get_or_404(comment_id)
        
        existing_vote = ForumVote.query.filter_by(user_id=current_user.id, comment_id=comment_id).first()
        
        if existing_vote:
            if existing_vote.vote_type == vote_type:
                db.session.delete(existing_vote)
                if vote_type == 'upvote':
                    comment.upvotes = max(0, comment.upvotes - 1)
                else:
                    comment.downvotes = max(0, comment.downvotes - 1)
            else:
                if existing_vote.vote_type == 'upvote':
                    comment.upvotes = max(0, comment.upvotes - 1)
                    comment.downvotes += 1
                else:
                    comment.downvotes = max(0, comment.downvotes - 1)
                    comment.upvotes += 1
                existing_vote.vote_type = vote_type
        else:
            vote = ForumVote(user_id=current_user.id, comment_id=comment_id, vote_type=vote_type)
            db.session.add(vote)
            if vote_type == 'upvote':
                comment.upvotes += 1
            else:
                comment.downvotes += 1
        
        comment.score = comment.upvotes - comment.downvotes
        db.session.commit()
        return redirect(url_for('view_post', post_id=comment.post_id))

    # -------------------------
    # Admin Forum Moderation
    # -------------------------
    @app.route('/admin/forum/users')
    @admin_required
    def admin_forum_users():
        users = User.query.order_by(User.username).all()
        return render_template('admin/admin_forum_users.html', users=users)

    @app.route('/admin/forum/user/<int:user_id>/ban', methods=['POST'])
    @admin_required
    def admin_ban_user(user_id):
        user = User.query.get_or_404(user_id)
        if user_id == current_user.id:
            flash('You cannot ban yourself.', 'danger')
            return redirect(url_for('admin_forum_users'))
        
        user.is_banned = True
        db.session.commit()
        flash(f'User {user.username} has been banned from the forum.', 'success')
        return redirect(url_for('admin_forum_users'))

    @app.route('/admin/forum/user/<int:user_id>/unban', methods=['POST'])
    @admin_required
    def admin_unban_user(user_id):
        user = User.query.get_or_404(user_id)
        user.is_banned = False
        db.session.commit()
        flash(f'User {user.username} has been unbanned.', 'success')
        return redirect(url_for('admin_forum_users'))

    @app.route('/admin/forum/user/<int:user_id>/silence', methods=['POST'])
    @admin_required
    def admin_silence_user(user_id):
        user = User.query.get_or_404(user_id)
        if user_id == current_user.id:
            flash('You cannot silence yourself.', 'danger')
            return redirect(url_for('admin_forum_users'))
        
        days = request.form.get('days', type=int) or 0
        if days > 0:
            user.silence_until = datetime.utcnow() + timedelta(days=days)
            user.is_silenced = True
        else:
            # Permanent silence
            user.is_silenced = True
            user.silence_until = None
        
        db.session.commit()
        if days > 0:
            flash(f'User {user.username} silenced for {days} days.', 'success')
        else:
            flash(f'User {user.username} permanently silenced.', 'success')
        return redirect(url_for('admin_forum_users'))

    @app.route('/admin/forum/user/<int:user_id>/unsilence', methods=['POST'])
    @admin_required
    def admin_unsilence_user(user_id):
        user = User.query.get_or_404(user_id)
        user.is_silenced = False
        user.silence_until = None
        db.session.commit()
        flash(f'User {user.username} unsilenced.', 'success')
        return redirect(url_for('admin_forum_users'))

    @app.route('/admin/forum/post/<int:post_id>/lock', methods=['POST'])
    @admin_required
    def admin_lock_post(post_id):
        post = ForumPost.query.get_or_404(post_id)
        post.is_locked = True
        db.session.commit()
        flash('Post locked.', 'success')
        return redirect(url_for('view_post', post_id=post_id))

    @app.route('/admin/forum/post/<int:post_id>/unlock', methods=['POST'])
    @admin_required
    def admin_unlock_post(post_id):
        post = ForumPost.query.get_or_404(post_id)
        post.is_locked = False
        db.session.commit()
        flash('Post unlocked.', 'success')
        return redirect(url_for('view_post', post_id=post_id))

    @app.route('/admin/forum/post/<int:post_id>/pin', methods=['POST'])
    @admin_required
    def admin_pin_post(post_id):
        post = ForumPost.query.get_or_404(post_id)
        post.is_pinned = True
        db.session.commit()
        flash('Post pinned.', 'success')
        return redirect(url_for('forum'))

    @app.route('/admin/forum/post/<int:post_id>/unpin', methods=['POST'])
    @admin_required
    def admin_unpin_post(post_id):
        post = ForumPost.query.get_or_404(post_id)
        post.is_pinned = False
        db.session.commit()
        flash('Post unpinned.', 'success')
        return redirect(url_for('forum'))

    # -------------------------
    # Calendar Routes
    # -------------------------
    @app.route('/calendar')
    def calendar():
        events = Event.query.order_by(Event.date).all()
        return render_template('events/calendar.html', events=events)

    @app.route('/admin/calendar')
    @staff_required
    def admin_calendar():
        """Level 2+ (Staff, Admin) can access calendar management"""
        events = Event.query.order_by(Event.date).all()
        return render_template('admin/admin_calendar.html', events=events)

    @app.route('/admin/calendar/event/create', methods=['GET', 'POST'])
    @staff_required
    def admin_create_event():
        """Level 2+ (Staff, Admin) can create calendar events"""
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            date_str = request.form.get('date', '').strip()
            end_date_str = request.form.get('end_date', '').strip()
            location = request.form.get('location', '').strip()
            register_url = request.form.get('register_url', '').strip()
            event_type = request.form.get('event_type', 'general').strip()
            color = request.form.get('color', '#007bff').strip()
            
            if not title or not date_str:
                flash('Title and date are required.', 'danger')
                return redirect(url_for('admin_create_event'))
            
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
                end_date = None
                if end_date_str:
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format.', 'danger')
                return redirect(url_for('admin_create_event'))
            
            # Handle image upload
            poster_filename = None
            if 'poster' in request.files:
                poster_file = request.files['poster']
                if poster_file and poster_file.filename:
                    if allowed_file(poster_file.filename):
                        poster_filename = secure_filename(f"event_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{poster_file.filename}")
                        images_folder = os.path.join(current_app.static_folder, 'images')
                        os.makedirs(images_folder, exist_ok=True)
                        poster_file.save(os.path.join(images_folder, poster_filename))
                    else:
                        flash('Invalid file type. Only images (png, jpg, jpeg) are allowed.', 'danger')
                        return redirect(url_for('admin_create_event'))
            
            event = Event(
                title=title,
                description=description,
                date=date,
                end_date=end_date,
                location=location,
                poster=poster_filename,
                register_url=register_url if register_url else None,
                event_type=event_type,
                color=color,
                created_by=current_user.id
            )
            db.session.add(event)
            db.session.commit()
            flash('Event created successfully!', 'success')
            return redirect(url_for('admin_calendar'))
        
        return render_template('admin/admin_create_event.html')

    @app.route('/admin/calendar/event/<int:event_id>/edit', methods=['GET', 'POST'])
    @staff_required
    def admin_edit_event(event_id):
        event = Event.query.get_or_404(event_id)
        
        if request.method == 'POST':
            event.title = request.form.get('title', event.title).strip()
            event.description = request.form.get('description', event.description).strip()
            date_str = request.form.get('date', '').strip()
            end_date_str = request.form.get('end_date', '').strip()
            event.location = request.form.get('location', event.location).strip()
            event.register_url = request.form.get('register_url', event.register_url or '').strip() or None
            event.event_type = request.form.get('event_type', event.event_type).strip()
            event.color = request.form.get('color', event.color).strip()
            
            if date_str:
                try:
                    event.date = datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    flash('Invalid date format.', 'danger')
                    return redirect(url_for('admin_edit_event', event_id=event_id))
            
            if end_date_str:
                try:
                    event.end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                except ValueError:
                    event.end_date = None
            else:
                event.end_date = None
            
            # Handle image upload
            if 'poster' in request.files:
                poster_file = request.files['poster']
                if poster_file and poster_file.filename:
                    if allowed_file(poster_file.filename):
                        poster_filename = secure_filename(f"event_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{poster_file.filename}")
                        images_folder = os.path.join(current_app.static_folder, 'images')
                        os.makedirs(images_folder, exist_ok=True)
                        poster_file.save(os.path.join(images_folder, poster_filename))
                        event.poster = poster_filename
                    else:
                        flash('Invalid file type. Only images (png, jpg, jpeg) are allowed.', 'danger')
                        return redirect(url_for('admin_edit_event', event_id=event_id))
            
            db.session.commit()
            flash('Event updated successfully!', 'success')
            return redirect(url_for('admin_calendar'))
        
        return render_template('admin/admin_edit_event.html', event=event)

    @app.route('/admin/calendar/event/<int:event_id>/delete', methods=['POST'])
    @staff_required
    def admin_delete_event(event_id):
        event = Event.query.get_or_404(event_id)
        db.session.delete(event)
        db.session.commit()
        flash('Event deleted successfully!', 'success')
        return redirect(url_for('admin_calendar'))

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
