"""
Integration Tests
Verify that features work together as expected.
Tests the interaction between authentication, factory management,
cost calculation, and optimization services.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from blogapp import create_app, db
from blogapp.models import (
    User, Factory, GridElectricityPrice,
    HourlyElectricityPrice, TimeOfUsePeriod, IndustryBenchmark
)


@pytest.fixture(scope='function')
def app():
    """Create test application"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['LOGIN_DISABLED'] = False
    return app


@pytest.fixture(scope='function')
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture(scope='function')
def init_db(app):
    """Initialize database with all required data"""
    with app.app_context():
        db.create_all()

        # Create users
        admin = User(username='admin', email='admin@test.com', user_type='admin')
        admin.set_password('admin123')
        db.session.add(admin)

        user = User(username='testuser', email='user@test.com', user_type='user')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        # Create grid prices
        for voltage in [10, 35, 110, 220]:
            gp = GridElectricityPrice(
                voltage_level=voltage,
                peak_price=1.2,
                normal_price=0.8,
                valley_price=0.4,
                capacity_price=22.5
            )
            db.session.add(gp)

        # Create TOU periods
        tou_config = {
            'Peak': [8, 9, 10, 11, 14, 15, 16, 17],
            'Normal': [6, 7, 12, 13, 18, 19, 20, 21],
            'Valley': [0, 1, 2, 3, 4, 5, 22, 23]
        }
        for period_type, hours in tou_config.items():
            for hour in hours:
                tou = TimeOfUsePeriod(
                    hour=hour,
                    time_range=f"{hour}-{hour+1}",
                    period_type=period_type
                )
                db.session.add(tou)

        # Create hourly supplier prices
        for hour in range(24):
            price = 0.3 if hour < 6 else (0.9 if 8 <= hour <= 17 else 0.5)
            hp = HourlyElectricityPrice(hour=hour, time_range=f"{hour}-{hour+1}", price=price)
            db.session.add(hp)

        # Create industry benchmarks
        benchmarks = [
            {'industry_type': 'Steel', 'avg_intensity': 4500, 'excellent_intensity': 3800, 'poor_intensity': 5200, 'output_per_kwh': 12.0},
            {'industry_type': 'Other', 'avg_intensity': 1500, 'excellent_intensity': 1000, 'poor_intensity': 2000, 'output_per_kwh': 14.0},
        ]
        for b in benchmarks:
            db.session.add(IndustryBenchmark(**b))

        db.session.commit()

        yield db

        db.session.remove()
        db.drop_all()


def login(client, username, password):
    """Helper: login a user"""
    return client.post('/auth/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)


def create_factory(client, data):
    """Helper: create a factory via API"""
    return client.post('/api/factory/create',
                       data=json.dumps(data),
                       content_type='application/json')


class TestAuthAndFactoryIntegration:
    """Test auth + factory management working together"""

    def test_login_then_create_factory(self, app, client, init_db):
        """User logs in and creates a factory successfully"""
        with app.app_context():
            login(client, 'testuser', 'password123')

            resp = create_factory(client, {
                'name': 'Integration Factory',
                'location': 'Test City',
                'industry_type': 'Steel',
                'voltage_level': 10,
                'transformer_capacity': 500,
                'daily_usage': 1000,
                'working_days_per_month': 22,
                'work_periods': json.dumps([{'start': 8, 'end': 18}])
            })

            data = resp.get_json()
            assert data['success'] is True

    def test_unauthenticated_cannot_create_factory(self, app, client, init_db):
        """Unauthenticated user cannot create factory"""
        with app.app_context():
            resp = create_factory(client, {
                'name': 'Unauthorized Factory',
                'industry_type': 'Steel',
                'voltage_level': 10,
                'transformer_capacity': 500,
                'daily_usage': 1000,
                'working_days_per_month': 22,
                'work_periods': json.dumps([{'start': 8, 'end': 18}])
            })
            # Should redirect to login (302) or return 401
            assert resp.status_code in [302, 401, 403]

    def test_factory_details_include_cost_analysis(self, app, client, init_db):
        """Factory details endpoint returns cost analysis data"""
        with app.app_context():
            login(client, 'testuser', 'password123')

            # Create factory
            resp = create_factory(client, {
                'name': 'Cost Analysis Factory',
                'location': 'Test',
                'industry_type': 'Steel',
                'voltage_level': 10,
                'transformer_capacity': 800,
                'daily_usage': 2000,
                'working_days_per_month': 22,
                'work_periods': json.dumps([{'start': 8, 'end': 12}, {'start': 13, 'end': 17}])
            })
            factory_data = resp.get_json()
            assert factory_data['success'] is True
            factory_id = factory_data['factory']['id']

            # Get factory details
            resp = client.get(f'/api/factory/{factory_id}/details')
            details = resp.get_json()

            assert details['success'] is True
            assert 'cost_analysis' in details
            assert details['cost_analysis']['total_monthly_cost'] > 0
            assert details['cost_analysis']['capacity_fee'] == 800 * 22.5
            assert len(details['cost_analysis']['hourly_breakdown']) == 24


class TestFactoryAndBenchmarkIntegration:
    """Test factory + efficiency benchmark working together"""

    def test_benchmark_returns_data_for_valid_industry(self, app, client, init_db):
        """Benchmark API returns data when factory has valid industry type"""
        with app.app_context():
            login(client, 'testuser', 'password123')

            resp = create_factory(client, {
                'name': 'Benchmark Factory',
                'industry_type': 'Steel',
                'voltage_level': 10,
                'transformer_capacity': 500,
                'daily_usage': 5000,
                'working_days_per_month': 26,
                'work_periods': json.dumps([{'start': 0, 'end': 24}])
            })
            factory_id = resp.get_json()['factory']['id']

            resp = client.get(f'/api/factory/{factory_id}/efficiency-benchmark')
            data = resp.get_json()

            assert data['success'] is True
            assert data['data'] is not None
            assert data['data']['industry'] == 'Steel'
            assert data['data']['level'] in ['excellent', 'good', 'average', 'poor']


class TestFactoryAndOptimizationIntegration:
    """Test factory + optimization suggestions working together"""

    def test_optimization_suggestions_generated(self, app, client, init_db):
        """Optimization suggestions are generated for a factory"""
        with app.app_context():
            login(client, 'testuser', 'password123')

            resp = create_factory(client, {
                'name': 'Optimization Factory',
                'industry_type': 'Steel',
                'voltage_level': 10,
                'transformer_capacity': 1000,
                'daily_usage': 5000,
                'working_days_per_month': 26,
                'work_periods': json.dumps([{'start': 8, 'end': 18}])
            })
            factory_id = resp.get_json()['factory']['id']

            resp = client.get(f'/api/factory/{factory_id}/suggestions')
            data = resp.get_json()

            assert data['success'] is True
            assert 'suggestions' in data

    def test_saving_potential_cost_mode(self, app, client, init_db):
        """Saving potential API works in cost mode"""
        with app.app_context():
            login(client, 'testuser', 'password123')

            resp = create_factory(client, {
                'name': 'Saving Factory',
                'industry_type': 'Steel',
                'voltage_level': 10,
                'transformer_capacity': 500,
                'daily_usage': 3000,
                'working_days_per_month': 22,
                'work_periods': json.dumps([{'start': 8, 'end': 17}])
            })
            factory_id = resp.get_json()['factory']['id']

            resp = client.get(f'/api/factory/{factory_id}/optimization?mode=cost')
            data = resp.get_json()

            assert data['success'] is True
            assert 'saving_potential' in data


class TestAdminIntegration:
    """Test admin features integration"""

    def test_admin_can_view_all_users(self, app, client, init_db):
        """Admin can access user list"""
        with app.app_context():
            login(client, 'admin', 'admin123')

            resp = client.get('/api/admin/users')
            data = resp.get_json()

            assert data['success'] is True
            assert len(data['users']) >= 1  # At least one user exists

    def test_admin_api_survives_proxy_ip_change(self, app, client, init_db):
        """Admin AJAX requests remain authenticated when proxy source IP changes"""
        with app.app_context():
            client.post('/auth/login', data={
                'username': 'admin',
                'password': 'admin123'
            }, environ_base={'REMOTE_ADDR': '66.235.111.6'})

            users_resp = client.get(
                '/api/admin/users',
                environ_base={'REMOTE_ADDR': '66.235.111.7'}
            )
            factories_resp = client.get(
                '/api/admin/factories',
                environ_base={'REMOTE_ADDR': '66.235.111.7'}
            )

            assert users_resp.status_code == 200
            assert users_resp.get_json()['success'] is True
            assert factories_resp.status_code == 200
            assert factories_resp.get_json()['success'] is True

    def test_admin_api_unauthenticated_returns_json(self, app, client, init_db):
        """Unauthenticated admin API requests do not return HTML redirects"""
        with app.app_context():
            resp = client.get('/api/admin/users')

            assert resp.status_code == 401
            assert resp.content_type.startswith('application/json')
            assert resp.get_json()['success'] is False

    def test_regular_user_cannot_access_admin(self, app, client, init_db):
        """Regular user cannot access admin endpoints"""
        with app.app_context():
            login(client, 'testuser', 'password123')

            resp = client.get('/api/admin/users')
            # Should be forbidden
            assert resp.status_code in [302, 403]


class TestEncryptionIntegration:
    """Test encryption works across the full flow"""

    def test_register_login_with_encrypted_fields(self, app, client, init_db):
        """User can register and login with encrypted username/email"""
        with app.app_context():
            # Register
            resp = client.post('/auth/register', data={
                'username': 'newuser',
                'email': 'new@test.com',
                'password': 'secure123',
                'user_type': 'user'
            }, follow_redirects=True)

            # Login with the new account
            resp = login(client, 'newuser', 'secure123')
            assert resp.status_code == 200

    def test_encrypted_username_stored_differently(self, app, client, init_db):
        """Encrypted username in DB differs from plaintext"""
        with app.app_context():
            user = User.query.filter_by(user_type='user').first()
            # The raw DB column should be encrypted (longer than plaintext)
            assert len(user._username) > len('testuser')
            # But the property should return plaintext
            assert user.username == 'testuser'


# ===========================================================
# Admin Action Tests (ban/unban user, delete factory)
# ===========================================================

class TestAdminBanUnban:
    """Test admin ban/unban functionality"""
    
    def test_admin_can_ban_user(self, app, client, init_db):
        """Admin can ban a regular user"""
        with app.app_context():
            user_id = User.query.filter_by(user_type='user').first().id
            login(client, 'admin', 'admin123')
            
            resp = client.post(f'/api/admin/user/{user_id}/ban')
            data = resp.get_json()
            
            assert data['success'] is True
            user = User.query.get(user_id)
            assert user.is_banned is True
            assert user.banned_at is not None
    
    def test_admin_can_unban_user(self, app, client, init_db):
        """Admin can unban a previously banned user"""
        with app.app_context():
            user = User.query.filter_by(user_type='user').first()
            user.is_banned = True
            db.session.commit()
            user_id = user.id
            
            login(client, 'admin', 'admin123')
            resp = client.post(f'/api/admin/user/{user_id}/unban')
            data = resp.get_json()
            
            assert data['success'] is True
            user = User.query.get(user_id)
            assert user.is_banned is False
    
    def test_cannot_ban_admin_users(self, app, client, init_db):
        """Admin users cannot be banned"""
        with app.app_context():
            admin_user = User.query.filter_by(user_type='admin').first()
            login(client, 'admin', 'admin123')
            
            resp = client.post(f'/api/admin/user/{admin_user.id}/ban')
            data = resp.get_json()
            
            assert data['success'] is False
    
    def test_cannot_ban_self(self, app, client, init_db):
        """Admin cannot ban themselves"""
        with app.app_context():
            admin_user = User.query.filter_by(user_type='admin').first()
            login(client, 'admin', 'admin123')
            
            resp = client.post(f'/api/admin/user/{admin_user.id}/ban')
            data = resp.get_json()
            
            assert data['success'] is False
    
    def test_regular_user_cannot_ban(self, app, client, init_db):
        """Regular users cannot ban anyone"""
        with app.app_context():
            target_id = User.query.filter_by(user_type='user').first().id
            login(client, 'testuser', 'password123')
            
            resp = client.post(f'/api/admin/user/{target_id}/ban')
            assert resp.status_code in [302, 401, 403]
    
    def test_banned_user_cannot_login(self, app, client, init_db):
        """Banned users cannot log in"""
        with app.app_context():
            user = User.query.filter_by(user_type='user').first()
            user.is_banned = True
            db.session.commit()
        
        # Logout admin first
        client.get('/auth/logout')
        
        # Try to log in as banned user
        with app.app_context():
            resp = client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'password123'
            }, follow_redirects=False)
            
            # Should be redirected back to auth page (not dashboard)
            assert resp.status_code == 302
            assert '/dashboard' not in resp.location


class TestAdminDeleteFactory:
    """Test admin factory deletion"""
    
    def test_admin_can_soft_delete_factory(self, app, client, init_db):
        """Admin can soft-delete a factory"""
        with app.app_context():
            login(client, 'testuser', 'password123')
            resp = create_factory(client, {
                'name': 'To Delete Factory',
                'industry_type': 'Steel',
                'voltage_level': 10,
                'transformer_capacity': 500,
                'daily_usage': 1000,
                'working_days_per_month': 22,
                'work_periods': json.dumps([{'start': 8, 'end': 18}])
            })
            factory_id = resp.get_json()['factory']['id']
            
            client.get('/auth/logout')
            login(client, 'admin', 'admin123')
            
            resp = client.post(f'/api/admin/factory/{factory_id}/delete')
            data = resp.get_json()
            
            assert data['success'] is True
            factory = Factory.query.get(factory_id)
            assert factory.is_deleted is True
            assert factory.deleted_at is not None
            assert factory.deleted_by_admin_id is not None
    
    def test_user_cannot_see_deleted_factory(self, app, client, init_db):
        """User does not see soft-deleted factories in their list"""
        with app.app_context():
            login(client, 'testuser', 'password123')
            resp = create_factory(client, {
                'name': 'Hidden Factory',
                'industry_type': 'Steel',
                'voltage_level': 10,
                'transformer_capacity': 500,
                'daily_usage': 1000,
                'working_days_per_month': 22,
                'work_periods': json.dumps([{'start': 8, 'end': 18}])
            })
            factory_id = resp.get_json()['factory']['id']
            
            # Soft delete via direct DB
            from datetime import datetime
            f = Factory.query.get(factory_id)
            f.is_deleted = True
            f.deleted_at = datetime.utcnow()
            db.session.commit()
            
            # User factory list should not include it
            resp = client.get('/api/factories')
            data = resp.get_json()
            ids = [fac['id'] for fac in data['factories']]
            assert factory_id not in ids
    
    def test_user_sees_deletion_notification(self, app, client, init_db):
        """User can fetch notifications about admin-deleted factories"""
        with app.app_context():
            login(client, 'testuser', 'password123')
            resp = create_factory(client, {
                'name': 'Notif Factory',
                'industry_type': 'Steel',
                'voltage_level': 10,
                'transformer_capacity': 500,
                'daily_usage': 1000,
                'working_days_per_month': 22,
                'work_periods': json.dumps([{'start': 8, 'end': 18}])
            })
            factory_id = resp.get_json()['factory']['id']
            
            from datetime import datetime
            f = Factory.query.get(factory_id)
            f.is_deleted = True
            f.deleted_at = datetime.utcnow()
            db.session.commit()
            
            resp = client.get('/api/factories/deleted-notifications')
            data = resp.get_json()
            
            assert data['success'] is True
            assert len(data['notifications']) >= 1
            assert any(n['name'] == 'Notif Factory' for n in data['notifications'])
            assert any('Beijing Time' in (n['deleted_at'] or '') for n in data['notifications'])


class TestEncryptionTestApiSecurity:
    """Test that encryption-test API requires admin"""
    
    def test_regular_user_cannot_access_encryption_test(self, app, client, init_db):
        """Regular user is forbidden from /api/encryption-test"""
        with app.app_context():
            login(client, 'testuser', 'password123')
            resp = client.get('/api/encryption-test')
            assert resp.status_code in [302, 401, 403]
    
    def test_admin_can_access_encryption_test(self, app, client, init_db):
        """Admin can access /api/encryption-test"""
        with app.app_context():
            login(client, 'admin', 'admin123')
            resp = client.get('/api/encryption-test')
            assert resp.status_code == 200
            data = resp.get_json()
            assert data['success'] is True
