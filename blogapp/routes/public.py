# blogapp/routes/public.py
from flask import Blueprint, render_template, session, redirect, url_for, current_app

# Define blueprint for public routes
bp = Blueprint("public", __name__)

@bp.get("/")
def index():
    """Public home page - redirect to login"""
    return redirect(url_for("auth.login"))

@bp.get("/about")
def about():
    """Public about page"""
    return render_template("about.html", title="About")

@bp.get("/contact")
def contact():
    """Public contact page"""
    return render_template("contact.html", title="Contact")

@bp.get("/logout")
def logout():
    """Fallback logout for guests"""
    # Redirect to auth logout if available, otherwise clear session
    if "auth.logout" in current_app.view_functions:
        return redirect(url_for("auth.logout"))
    session.clear()
    return redirect(url_for("public.index"))