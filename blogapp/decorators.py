from functools import wraps
from flask import abort
from flask_login import current_user


def staff_required(f):
    """Decorator to restrict access to staff and admin only"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated and is staff or admin
        if not current_user.is_authenticated or current_user.user_type not in ['staff', 'admin']:
            abort(403)  # Forbidden access
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to restrict access to admin only"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated and is admin
        if not current_user.is_authenticated:
            abort(401)  # Unauthorized - not logged in
        if current_user.user_type != 'admin':
            abort(403)  # Forbidden - logged in but not admin
        return f(*args, **kwargs)
    return decorated_function