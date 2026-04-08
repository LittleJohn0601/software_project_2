import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from blogapp import create_app, db


@pytest.fixture(scope='session')
def app():
    """Create a test application instance, reuse at session scope"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF protection for tests
    
    return app


@pytest.fixture(scope='session')
def client(app):
    """Create a test client"""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Database session isolated for each test function"""
    with app.app_context():
        db.create_all()
        yield db.session
        db.session.remove()
        db.drop_all()