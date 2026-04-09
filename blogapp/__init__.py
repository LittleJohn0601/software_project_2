# blogapp/__init__.py

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


import os
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import logging
from logging.handlers import RotatingFileHandler

# Global extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app() -> Flask:
    app = Flask(__name__)
    
    # ---------- Load configuration ----------
   
    from dotenv import load_dotenv
    env_file = '.env'

    if os.path.exists(env_file):
        load_dotenv(env_file)
        app.logger.info(f"Loaded configuration from {env_file}")
    else:
        app.logger.warning(f"No {env_file} file found, using environment variables only")
    
    # ---------- Base configuration ----------
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-fallback-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///greenlife.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Encryption configuration
    app.config['ENCRYPTION_MASTER_KEY'] = os.environ.get('ENCRYPTION_MASTER_KEY')

    app.config['DEBUG'] = os.environ.get('DEBUG', 'False').lower() == 'true'

    app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    app.config['REMEMBER_COOKIE_SECURE'] = os.environ.get('REMEMBER_COOKIE_SECURE', 'False').lower() == 'true'
    
    # ---------- Bind extensions ----------
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Login manager defaults
    login_manager.login_view = 'auth.login'
    login_manager.session_protection = 'strong'
    
    # ---------- Logging ----------
    log_dir = os.path.join(app.root_path, '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, 'greenlife.log')
    
    file_handler = RotatingFileHandler(
        log_path, maxBytes=10240, backupCount=10, encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    app.logger.handlers.clear()
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info(f'GreenLife app startup with encryption (loaded from {env_file})')
    app.logger.info(f'Log file location: {log_path}')
    
    if not app.logger.handlers:
        app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info(f'GreenLife app startup with encryption (loaded from {env_file})')

    """Add helper functions to all templates"""
    @app.context_processor
    def utility_processor():
        """Add helper functions to all templates"""
        def has_endpoint(name: str) -> bool:
            """Check if endpoint exists"""
            return name in app.view_functions
        return dict(has_endpoint=has_endpoint)
    
    # ---------- Register blueprints ----------
    with app.app_context():
        from blogapp.routes import auth, main, visualization
        from blogapp.routes.public import bp as public_bp
        
        app.register_blueprint(public_bp)
        app.register_blueprint(main.bp)
        app.register_blueprint(auth.bp, url_prefix='/auth')
        app.register_blueprint(visualization.bp, url_prefix='/api')
    
    # ---------- Auto-sync electricity prices on startup ----------
    with app.app_context():
        from blogapp.utils.price_sync import check_and_sync_on_startup
        check_and_sync_on_startup(app)
    
    return app
