"""
Green Power Service Tests
Tests the green power procurement recommendation logic.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from blogapp import create_app, db
from blogapp.models import User, Factory
from blogapp.services.green_power import GreenPowerService, get_green_power_recommendation


@pytest.fixture(scope='function')
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    return app


@pytest.fixture(scope='function')
def init_db(app):
    with app.app_context():
        db.create_all()
        user = User(username='testuser', email='test@test.com', user_type='user')
        user.set_password('pass')
        db.session.add(user)
        db.session.commit()
        yield db
        db.session.remove()
        db.drop_all()


class TestGreenPowerTiers:
    """Test tier classification based on monthly usage"""

    def test_small_tier(self, app, init_db):
        """< 100,000 kWh should be classified as small"""
        with app.app_context():
            result = GreenPowerService.get_recommendation(50000)
            assert result['tier'] == 'small'
            assert result['strategy'] == 'green_certificate'
            assert result['certificates_needed'] == 50.0

    def test_medium_tier(self, app, init_db):
        """100,000 - 1,000,000 kWh should be classified as medium"""
        with app.app_context():
            result = GreenPowerService.get_recommendation(500000)
            assert result['tier'] == 'medium'
            assert result['strategy'] == 'green_ppa'
            assert result['certificates_needed'] is None

    def test_large_tier(self, app, init_db):
        """> 1,000,000 kWh should be classified as large"""
        with app.app_context():
            result = GreenPowerService.get_recommendation(2000000)
            assert result['tier'] == 'large'
            assert result['strategy'] == 'pv_certificate'

    def test_boundary_small_medium(self, app, init_db):
        """Exactly 100,000 kWh should be medium tier"""
        with app.app_context():
            result = GreenPowerService.get_recommendation(100000)
            assert result['tier'] == 'medium'

    def test_boundary_medium_large(self, app, init_db):
        """Exactly 1,000,000 kWh should be large tier"""
        with app.app_context():
            result = GreenPowerService.get_recommendation(1000000)
            assert result['tier'] == 'large'


class TestGreenPowerProjectTypes:
    """Test existing vs incremental project pricing"""

    def test_existing_project(self, app, init_db):
        """Existing project uses benchmark price"""
        with app.app_context():
            result = GreenPowerService.get_recommendation(200000, project_type='existing')
            assert 'benchmark' in result['price_info'].lower() or '0.332' in result['price_info']
            assert '2025' in result['policy_note']

    def test_incremental_project(self, app, init_db):
        """Incremental project uses bidding mechanism"""
        with app.app_context():
            result = GreenPowerService.get_recommendation(200000, project_type='incremental')
            assert 'bidding' in result['price_info'].lower() or 'incremental' in result['price_info'].lower()


class TestGreenPowerOutput:
    """Test output structure and calculations"""

    def test_result_structure(self, app, init_db):
        """Result contains all required fields"""
        with app.app_context():
            result = GreenPowerService.get_recommendation(300000)
            required_keys = [
                'success', 'tier', 'tier_name', 'description', 'strategy',
                'steps', 'monthly_usage', 'estimated_cost_per_month',
                'carbon_reduction_per_month', 'price_info', 'policy_note',
                'platforms', 'benchmark_price'
            ]
            for key in required_keys:
                assert key in result, f"Missing key: {key}"

    def test_carbon_reduction_calculation(self, app, init_db):
        """Carbon reduction is calculated correctly"""
        with app.app_context():
            usage = 500000
            result = GreenPowerService.get_recommendation(usage)
            expected = round(usage * 0.0006634, 2)
            assert result['carbon_reduction_per_month'] == expected

    def test_platforms_not_empty(self, app, init_db):
        """Platforms list should contain entries"""
        with app.app_context():
            result = GreenPowerService.get_recommendation(100000)
            assert len(result['platforms']) > 0
            for p in result['platforms']:
                assert 'name' in p
                assert 'url' in p

    def test_steps_not_empty(self, app, init_db):
        """Steps list should contain entries"""
        with app.app_context():
            result = GreenPowerService.get_recommendation(100000)
            assert len(result['steps']) > 0

    def test_get_recommendation_with_factory(self, app, init_db):
        """get_green_power_recommendation works with factory object"""
        with app.app_context():
            factory = Factory(
                name='Green Factory',
                industry_type='Steel',
                voltage_level=10,
                transformer_capacity=500,
                daily_usage=5000,
                work_periods='[{"start": 8, "end": 18}]',
                working_days_per_month=26,
                user_id=1
            )
            db.session.add(factory)
            db.session.commit()

            result = get_green_power_recommendation(factory)
            assert result is not None
            assert result['monthly_usage'] == factory.monthly_usage

    def test_get_recommendation_with_none_factory(self, app, init_db):
        """get_green_power_recommendation returns None for None factory"""
        with app.app_context():
            result = get_green_power_recommendation(None)
            assert result is None
