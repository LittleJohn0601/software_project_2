# blogapp/routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from blogapp import db, login_manager
from blogapp.models import User
from blogapp.forms import LoginForm, RegistrationForm
from datetime import datetime

bp = Blueprint('auth', __name__)


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))


@bp.route('/', methods=['GET'])
def auth_page():
    """Unified authentication page (login + register)"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    login_form = LoginForm()
    register_form = RegistrationForm()
    
    return render_template('auth/auth.html', 
                         login_form=login_form, 
                         register_form=register_form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration with encrypted email"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # GET request redirect to unified authentication page
    if request.method == 'GET':
        return redirect(url_for('auth.auth_page') + '?mode=register')
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip().lower()  # Encrypted automatically
        password = form.password.data
        user_type = form.user_type.data
        
        # Check if username already exists (need to check all users since username is encrypted)
        for u in User.query.all():
            try:
                if u.username == username:
                    flash('Username already exists', 'danger')
                    return redirect(url_for('auth.auth_page') + '?mode=register')
            except Exception:
                continue
        
        # Check if email already exists (need to check all users since email is encrypted)
        for u in User.query.all():
            try:
                if u.email == email:
                    flash('Email already exists', 'danger')
                    return redirect(url_for('auth.auth_page') + '?mode=register')
            except Exception:
                continue
        
        # Create user (email will be encrypted automatically)
        user = User(
            username=username,
            email=email,  # The setter in User model will encrypt it
            user_type=user_type
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        current_app.logger.info(f"New user registered: {username}")
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.auth_page'))
    
    # Form validation failed, return to registration page
    return redirect(url_for('auth.auth_page') + '?mode=register')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    # Authenticated users are redirected to the homepage directly
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    # GET request redirect to unified authentication page
    if request.method == 'GET':
        return redirect(url_for('auth.auth_page'))

    form = LoginForm()

    if form.validate_on_submit():
        username_or_email = form.username.data.strip()
        password = form.password.data
        
        # Since username and email are encrypted, we need to check all users
        user = None
        for u in User.query.all():
            try:
                # Check if input matches username or email
                if u.username == username_or_email or u.email == username_or_email:
                    user = u
                    break
            except Exception as e:
                # Decryption failed for this user (likely encrypted with a different key)
                current_app.logger.warning(
                    f"Failed to decrypt user data for user_id={u.id}: {e}. "
                    f"This user may have been created with a different encryption key."
                )
                continue

        # First check username + password
        if user and user.check_password(password):

            # ⭐ First check if the user is in banned period
            if hasattr(user, 'is_banned') and user.is_banned:
                now = datetime.now()
                remaining = user.ban_until - now
                days = remaining.days
                hours = remaining.seconds // 3600
                minutes = (remaining.seconds % 3600) // 60

                ban_msg = (
                    "Your account is currently BANNED.\n"
                    f"Reason: {user.ban_reason or 'No reason provided'}\n"
                    f"Ban will be lifted at: {user.ban_until.strftime('%Y-%m-%d %H:%M UTC')}\n"
                    f"Time left: {days} day(s) {hours} hour(s) {minutes} minute(s)."
                )

                current_app.logger.warning(
                    "Banned user '%s' attempted to log in. Reason=%s, until=%s",
                    user.username, user.ban_reason, user.ban_until
                )

                flash(ban_msg, 'danger')
                return redirect(url_for('auth.auth_page'))

            # ⭐ Normal login
            login_user(user)
            current_app.logger.info("User '%s' logged in successfully.", user.username)
            flash('Login successful!', 'success')
            
            # Redirect admin to admin dashboard, regular users to user dashboard
            if user.is_admin:
                return redirect(url_for('admin.admin_dashboard'))
            else:
                return redirect(url_for('main.dashboard'))

        # Username/Email does not exist or password is incorrect
        current_app.logger.warning("Failed login attempt for username/email='%s'", username_or_email)
        flash('Invalid username/email or password', 'danger')

    return redirect(url_for('auth.auth_page'))


@bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    current_app.logger.info("User '%s' logged out.", current_user.username)
    logout_user()
    flash('Successfully logged out', 'success')
    return redirect(url_for('main.index'))