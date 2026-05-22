# blogapp/routes/public.py
"""
Public routes (no login required)
Public routes
"""

from flask import Blueprint, redirect, url_for

# Create blueprint
bp = Blueprint("public", __name__)


@bp.get("/")
def index():
    """Home page - redirect to authentication page"""
    return redirect(url_for("auth.auth_page"))
