from functools import wraps
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.extensions import db
from app.models import User, AuditLog

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'error': 'Authentication required. Please log in.'}), 401
            flash('Please log in to access the National Health Command Center.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session.clear()
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email
            session['user_role'] = user.role
            session.permanent = True

            # Audit log login (Innovation 10)
            audit = AuditLog(
                user_id=user.id,
                action="LOGIN",
                description=f"User {user.name} ({user.email}) authenticated as {user.role}.",
                timestamp=datetime.utcnow(),
                ip_address=request.remote_addr or '127.0.0.1'
            )
            db.session.add(audit)
            db.session.commit()

            flash(f"Welcome to HealthSync AI Command Center, {user.name}.", "success")
            next_url = request.args.get('next')
            return redirect(next_url or url_for('main.dashboard'))
        else:
            flash("Invalid national officer credentials. Check demo credentials and try again.", "danger")

    return render_template('login.html')


@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    user_id = session.get('user_id')
    user_name = session.get('user_name', 'Officer')

    if user_id:
        audit = AuditLog(
            user_id=user_id,
            action="LOGOUT",
            description=f"User {user_name} logged out from the command center session.",
            timestamp=datetime.utcnow(),
            ip_address=request.remote_addr or '127.0.0.1'
        )
        db.session.add(audit)
        db.session.commit()

    session.clear()
    flash("You have been securely logged out of the National Command Center.", "info")
    return redirect(url_for('auth.login'))


@auth_bp.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        session.clear()
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['user_email'] = user.email
        session['user_role'] = user.role

        audit = AuditLog(
            user_id=user.id,
            action="API_LOGIN",
            description=f"API session started for {user.name} ({user.role}).",
            timestamp=datetime.utcnow(),
            ip_address=request.remote_addr or '127.0.0.1'
        )
        db.session.add(audit)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Authentication successful',
            'user': user.to_dict()
        }), 200

    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401


@auth_bp.route('/api/auth/logout', methods=['POST'])
def api_logout():
    user_id = session.get('user_id')
    if user_id:
        audit = AuditLog(
            user_id=user_id,
            action="API_LOGOUT",
            description=f"User {session.get('user_name')} logged out via API.",
            timestamp=datetime.utcnow(),
            ip_address=request.remote_addr or '127.0.0.1'
        )
        db.session.add(audit)
        db.session.commit()
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200
