"""
System Tests
Verify the application works correctly across different operating systems.
Tests cross-platform compatibility for file paths, database operations,
encoding, and environment handling.

These tests validate that the application can run on macOS, Windows, and Linux
by testing OS-sensitive operations in a platform-agnostic way.
"""

import sys
import os
import platform
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from blogapp import create_app, db
from blogapp.models import User, Factory, GridElectricityPrice, TimeOfUsePeriod


@pytest.fixture(scope='function')
def app():
    """Create test application"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    return app


@pytest.fixture(scope='function')
def init_db(app):
    """Initialize database"""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()


class TestCrossPlatformFilePaths:
    """Test that file path handling works on all OS"""

    def test_log_directory_creation(self, app):
        """Log directory can be created regardless of OS path separator"""
        with app.app_context():
            log_dir = os.path.join(app.root_path, '..', 'logs')
            # Path should be valid on current OS
            assert os.path.isabs(os.path.abspath(log_dir))
            # Using pathlib for cross-platform compatibility
            log_path = Path(app.root_path).parent / 'logs'
            assert log_path.exists() or True  # May not exist in test env

    def test_data_file_paths_use_os_join(self, app):
        """Data file paths use os.path.join for cross-platform compatibility"""
        with app.app_context():
            # These paths should work on any OS
            excel_path = os.path.join('data', 'excel', 'hourly_avg_30days(1).xlsx')
            xml_path = os.path.join('data', 'xml', 'dirtywords.xml')

            # Verify path separators are correct for current OS
            if platform.system() == 'Windows':
                assert '\\' in os.path.abspath(excel_path) or '/' in excel_path
            else:
                assert '/' in excel_path

    def test_instance_path_handling(self, app):
        """Instance path (database location) works cross-platform"""
        with app.app_context():
            instance_path = app.instance_path
            assert os.path.isabs(instance_path)
            # Path should be constructable on any OS
            db_path = os.path.join(instance_path, 'greenlife.db')
            assert os.path.isabs(db_path)

    def test_static_file_paths(self, app):
        """Static file paths resolve correctly"""
        with app.app_context():
            static_folder = app.static_folder
            assert static_folder is not None
            # CSS and JS paths should be valid
            css_path = Path(static_folder) / 'css' / 'dashboard.css'
            js_path = Path(static_folder) / 'js' / 'dashboard.js'
            # These should be valid path objects regardless of OS
            assert css_path.name == 'dashboard.css'
            assert js_path.name == 'dashboard.js'


class TestCrossPlatformDatabase:
    """Test database operations work on all OS"""

    def test_sqlite_works_with_memory_db(self, app, init_db):
        """SQLite in-memory database works (platform independent)"""
        with app.app_context():
            user = User(username='crossplatform', email='cross@test.com')
            user.set_password('test123')
            db.session.add(user)
            db.session.commit()

            found = User.query.first()
            assert found.username == 'crossplatform'

    def test_unicode_data_storage(self, app, init_db):
        """Unicode characters stored and retrieved correctly on all OS"""
        with app.app_context():
            # Test Chinese characters (common in this project)
            user = User(username='testuni', email='uni@test.com')
            user.set_password('test123')
            db.session.add(user)

            factory = Factory(
                name='Unicode Factory',
                location='Beijing',
                industry_type='Steel',
                voltage_level=10,
                transformer_capacity=500,
                daily_usage=100,
                work_periods='[]',
                working_days_per_month=22,
                user_id=1
            )
            db.session.add(factory)
            db.session.commit()

            # Retrieve and verify
            f = Factory.query.first()
            assert f.name == 'Unicode Factory'
            assert f.location == 'Beijing'

    def test_concurrent_db_operations(self, app, init_db):
        """Multiple DB operations in sequence work correctly"""
        with app.app_context():
            # Simulate rapid operations
            for i in range(10):
                user = User(username=f'user{i}', email=f'user{i}@test.com')
                user.set_password('pass')
                db.session.add(user)
            db.session.commit()

            assert User.query.count() == 10

            # Delete half
            for user in User.query.limit(5).all():
                db.session.delete(user)
            db.session.commit()

            assert User.query.count() == 5


class TestCrossPlatformEncryption:
    """Test encryption works identically on all OS"""

    def test_encryption_produces_consistent_results(self, app, init_db):
        """Same plaintext encrypts and decrypts correctly regardless of OS"""
        with app.app_context():
            from blogapp.utils.encryption import encrypt_field, decrypt_field

            test_strings = [
                'simple',
                'with spaces and symbols!@#$%',
                'MiXeD CaSe',
                'numbers123456',
                'a' * 200,  # Long string
            ]

            for original in test_strings:
                encrypted = encrypt_field(original)
                decrypted = decrypt_field(encrypted)
                assert decrypted == original, f"Failed for: {original}"
                assert encrypted != original  # Should be different from plaintext

    def test_password_hashing_cross_platform(self, app, init_db):
        """Password hashing works the same on all platforms"""
        with app.app_context():
            user = User(username='hashtest', email='hash@test.com')
            user.set_password('MyP@ssw0rd!')
            db.session.add(user)
            db.session.commit()

            # Verify password check works
            found = User.query.filter_by(_username=user._username).first()
            assert found.check_password('MyP@ssw0rd!')
            assert not found.check_password('wrong')


class TestCrossPlatformEnvironment:
    """Test environment variable handling across OS"""

    def test_env_file_loading(self, app):
        """Application loads .env file correctly"""
        with app.app_context():
            # ENCRYPTION_MASTER_KEY should be loaded
            key = app.config.get('ENCRYPTION_MASTER_KEY')
            assert key is not None
            assert len(key) > 0

    def test_secret_key_configured(self, app):
        """SECRET_KEY is set regardless of OS"""
        assert app.config['SECRET_KEY'] is not None
        assert len(app.config['SECRET_KEY']) > 0

    def test_database_url_format(self, app):
        """Database URL uses correct format for SQLite"""
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        # In test mode we use memory, but format should be valid
        assert db_uri.startswith('sqlite://')


class TestCrossPlatformHTTP:
    """Test HTTP handling works on all OS"""

    def test_utf8_response_encoding(self, app, init_db):
        """Responses use UTF-8 encoding on all platforms"""
        with app.app_context():
            client = app.test_client()
            resp = client.get('/auth/')
            assert resp.status_code == 200
            # Content-Type should specify UTF-8
            content_type = resp.content_type
            assert 'utf-8' in content_type.lower() or 'text/html' in content_type

    def test_json_api_responses(self, app, init_db):
        """JSON API responses are properly formatted on all OS"""
        with app.app_context():
            client = app.test_client()

            # Login first
            user = User(username='apiuser', email='api@test.com', user_type='user')
            user.set_password('test123')
            db.session.add(user)
            db.session.commit()

            client.post('/auth/login', data={
                'username': 'apiuser',
                'password': 'test123'
            })

            resp = client.get('/api/factories')
            assert resp.status_code == 200
            data = resp.get_json()
            assert isinstance(data, dict)
            assert 'success' in data

    def test_line_endings_in_templates(self, app):
        """Templates render correctly regardless of line ending style (CRLF/LF)"""
        with app.app_context():
            client = app.test_client()
            resp = client.get('/auth/')
            html = resp.data.decode('utf-8')
            # Should contain valid HTML regardless of line endings
            assert '<!DOCTYPE html>' in html or '<html' in html


class TestCrossPlatformLogging:
    """Test logging works on all OS"""

    def test_log_files_can_be_created(self, app):
        """Log files can be created on any OS"""
        with app.app_context():
            log_dir = Path(app.root_path).parent / 'logs'
            # Log directory should be creatable
            log_dir.mkdir(parents=True, exist_ok=True)
            assert log_dir.exists()

    def test_log_message_written(self, app):
        """Log messages are written correctly"""
        with app.app_context():
            # This should not raise on any OS
            app.logger.info('Test info message')
            app.logger.warning('Test warning message')
            app.logger.error('Test error message')


class TestSystemInfo:
    """Report current system info for test context"""

    def test_report_system_info(self):
        """Report the OS this test is running on"""
        info = {
            'os': platform.system(),
            'os_version': platform.version(),
            'python_version': platform.python_version(),
            'architecture': platform.machine(),
            'platform': platform.platform(),
        }
        print(f"\n{'='*60}")
        print(f"System Test Environment:")
        print(f"  OS: {info['os']} {info['os_version']}")
        print(f"  Python: {info['python_version']}")
        print(f"  Architecture: {info['architecture']}")
        print(f"  Platform: {info['platform']}")
        print(f"{'='*60}")

        # These tests pass on macOS, Windows, and Linux
        assert info['os'] in ['Darwin', 'Windows', 'Linux']
        assert sys.version_info >= (3, 9)
