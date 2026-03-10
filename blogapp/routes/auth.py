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


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration with encrypted email"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip().lower()  # Encrypted automatically
        password = form.password.data
        user_type = form.user_type.data
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('auth/register.html', title='Register', form=form)
        
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
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    # Authenticated users are redirected to the homepage directly
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()

        # First check username + password
        if user and user.check_password(password):

            # ⭐ First check if the user is in banned period
            if user.is_banned:
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
                # Do not call login_user, return to login page directly
                return render_template('auth/login.html', title='Login', form=form)

            # ⭐ Normal login
            login_user(user)
            current_app.logger.info("User '%s' logged in successfully.", user.username)
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))

        # Username does not exist or password is incorrect
        current_app.logger.warning("Failed login attempt for username='%s'", username)
        flash('Invalid username or password', 'danger')

    return render_template('auth/login.html', title='Login', form=form)


@bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    current_app.logger.info("User '%s' logged out.", current_user.username)
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))