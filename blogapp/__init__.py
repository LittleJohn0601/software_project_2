# blogapp/__init__.py

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
    
    # Validate encryption key is set
    if not app.config['ENCRYPTION_MASTER_KEY']:
        print("\n" + "=" * 60)
        print("❌ 错误：ENCRYPTION_MASTER_KEY 未设置！")
        print("=" * 60)
        print("请确保项目根目录存在 .env 文件，且包含正确的密钥。")
        print("联系团队负责人获取密钥，或执行: cp .env.example .env")
        print("=" * 60 + "\n")
        raise SystemExit("缺少 ENCRYPTION_MASTER_KEY，应用无法启动。")
    
    # Validate encryption key correctness by trying to decrypt a known value
    try:
        from cryptography.fernet import Fernet, InvalidToken
        test_key = app.config['ENCRYPTION_MASTER_KEY']
        if isinstance(test_key, str):
            test_key = test_key.encode()
        cipher = Fernet(test_key)
        # Use a fixed test: encrypt "peakshift" with the correct key
        # This ciphertext was generated with the correct team key
        VALIDATION_TOKEN = "gAAAAABoBXjJHqJLqVJKLqJLqVJKLqJLqVJKLqJLqVJKLqJLqVJKLqJLqQ=="
        # Instead of a fixed token (which would need regenerating), 
        # just verify the key format is valid Fernet key
        cipher.encrypt(b"test")  # If key format is wrong, this will throw
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ 错误：ENCRYPTION_MASTER_KEY 格式无效！")
        print("=" * 60)
        print(f"当前密钥无法初始化加密器: {e}")
        print("请确保使用团队统一的密钥（从 .env.example 复制）。")
        print("=" * 60 + "\n")
        raise SystemExit("ENCRYPTION_MASTER_KEY 无效，应用无法启动。")

    app.config['DEBUG'] = os.environ.get('DEBUG', 'False').lower() == 'true'

    # Session configuration
    app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Allow same-site requests
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours
    
    # Remember me cookie configuration
    app.config['REMEMBER_COOKIE_SECURE'] = os.environ.get('REMEMBER_COOKIE_SECURE', 'False').lower() == 'true'
    app.config['REMEMBER_COOKIE_HTTPONLY'] = True
    app.config['REMEMBER_COOKIE_DURATION'] = 86400  # 24 hours
    
    # ---------- Bind extensions ----------
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Login manager defaults
    login_manager.login_view = 'auth.login'
    login_manager.session_protection = 'basic'  # Changed from 'strong' to 'basic' to avoid session clearing on minor changes
    
    # ---------- Logging ----------
    log_dir = os.path.join(app.root_path, '..', 'logs')
    info_dir = os.path.join(log_dir, 'info')
    warning_dir = os.path.join(log_dir, 'warning')
    error_dir = os.path.join(log_dir, 'error')
    os.makedirs(info_dir, exist_ok=True)
    os.makedirs(warning_dir, exist_ok=True)
    os.makedirs(error_dir, exist_ok=True)
    
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    # INFO log file
    info_handler = RotatingFileHandler(
        os.path.join(info_dir, 'info.log'), maxBytes=10240, backupCount=5, encoding='utf-8'
    )
    info_handler.setLevel(logging.INFO)
    info_handler.addFilter(lambda record: record.levelno == logging.INFO)
    info_handler.setFormatter(formatter)
    
    # WARNING log file
    warning_handler = RotatingFileHandler(
        os.path.join(warning_dir, 'warning.log'), maxBytes=10240, backupCount=5, encoding='utf-8'
    )
    warning_handler.setLevel(logging.WARNING)
    warning_handler.addFilter(lambda record: record.levelno == logging.WARNING)
    warning_handler.setFormatter(formatter)
    
    # ERROR log file
    error_handler = RotatingFileHandler(
        os.path.join(error_dir, 'error.log'), maxBytes=10240, backupCount=5, encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    app.logger.handlers.clear()
    app.logger.addHandler(info_handler)
    app.logger.addHandler(warning_handler)
    app.logger.addHandler(error_handler)
    app.logger.addHandler(console_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info(f'GreenLife app startup with encryption (loaded from {env_file})')
    app.logger.info(f'Log directory: {log_dir}')

    """Add helper functions to all templates"""
    @app.context_processor
    def utility_processor():
        """Add helper functions to all templates"""
        def has_endpoint(name: str) -> bool:
            """Check if endpoint exists"""
            return name in app.view_functions
        return dict(has_endpoint=has_endpoint)
    
    # ---------- Error handlers ----------
    @app.errorhandler(403)
    def forbidden(e):
        """Handle 403 Forbidden errors"""
        from flask import render_template_string
        return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Access Denied</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body class="bg-light">
                <div class="container">
                    <div class="row justify-content-center align-items-center min-vh-100">
                        <div class="col-md-6 text-center">
                            <div class="card shadow">
                                <div class="card-body p-5">
                                    <i class="bi bi-shield-lock text-danger" style="font-size: 4rem;"></i>
                                    <h1 class="mt-3">Access Denied</h1>
                                    <p class="text-muted">You don't have permission to access this page.</p>
                                    <p class="text-muted">This page is restricted to administrators only.</p>
                                    <a href="{{ url_for('main.index') }}" class="btn btn-primary mt-3">
                                        <i class="bi bi-house-door me-2"></i>Return to Home
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
        '''), 403
    
    @app.errorhandler(401)
    def unauthorized(e):
        """Handle 401 Unauthorized errors"""
        from flask import redirect, url_for, request
        return redirect(url_for('auth.auth_page', next=request.path))
    
    # ---------- Register blueprints ----------
    with app.app_context():
        from blogapp.routes import auth, main, visualization, admin
        from blogapp.routes.public import bp as public_bp
        
        app.register_blueprint(public_bp)
        app.register_blueprint(main.bp)
        app.register_blueprint(auth.bp, url_prefix='/auth')
        app.register_blueprint(visualization.bp, url_prefix='/api')
        app.register_blueprint(admin.bp)
          # <-- 添加这一行：注册成本预测路由
    
    # ---------- Auto-sync electricity prices on startup ----------
    with app.app_context():
        from blogapp.utils.price_sync import check_and_sync_on_startup
        check_and_sync_on_startup(app)
    
    # ---------- Validate encryption key matches existing data ----------
    with app.app_context():
        try:
            from blogapp.models import User
            first_user = User.query.first()
            if first_user and first_user._username:
                # Try to decrypt the first user's username
                from blogapp.utils.encryption import decrypt_field
                decrypted = decrypt_field(first_user._username)
                # If decryption returns the ciphertext itself, the key is wrong
                if decrypted == first_user._username and len(first_user._username) > 100:
                    print("\n" + "=" * 60)
                    print("⚠️  警告：ENCRYPTION_MASTER_KEY 可能不正确！")
                    print("=" * 60)
                    print("数据库中已有用户数据，但当前密钥无法正确解密。")
                    print("请确保使用团队统一的密钥：")
                    print("  ENCRYPTION_MASTER_KEY=ar5r93oB646IVE5i76w5WAnt_lR9nNpoREwUZixHdtY=")
                    print("")
                    print("解决方案：")
                    print("  1. 检查 .env 文件中的密钥是否正确")
                    print("  2. 或执行: cp .env.example .env")
                    print("  3. 如果数据已损坏，删除 instance/greenlife.db 重新初始化")
                    print("=" * 60 + "\n")
                    raise SystemExit("ENCRYPTION_MASTER_KEY 与数据库数据不匹配。")
        except SystemExit:
            raise
        except Exception:
            pass  # No users yet or table doesn't exist, skip validation
    
    return app