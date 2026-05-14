"""
Equipment Recommendation Service Tests
Tests the energy-saving equipment recommendation logic.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from blogapp import create_app, db
from blogapp.models import User, Factory
from blogapp.services.equipment_recommendation import get_equipment_recommendations


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


def make_factory(daily_usage, industry_type='Steel', transformer_capacity=500):
    """Helper to create a factory"""
    factory = Factory(
        name='Equipment Test Factory',
        industry_type=industry_type,
        voltage_level=10,
        transformer_capacity=transformer_capacity,
        daily_usage=daily_usage,
        work_periods='[{"start": 8, "end": 18}]',
        working_days_per_month=26,
        user_id=1
    )
    db.session.add(factory)
    db.session.commit()
    return factory


class TestEquipmentRecommendations:
    """Test equipment recommendation generation"""

    def test_returns_list(self, app, init_db):
        """Should return a list of recommendations"""
        with app.app_context():
            factory = make_factory(5000)
            result = get_equipment_recommendations(factory)
            assert isinstance(result, list)

    def test_recommendation_structure(self, app, init_db):
        """Each recommendation has required fields"""
        with app.app_context():
            factory = make_factory(10000)
            result = get_equipment_recommendations(factory)

            if len(result) > 0:
                for rec in result:
                    assert 'category' in rec
                    assert 'icon' in rec
                    assert 'investment_formatted' in rec
                    assert 'annual_saving_formatted' in rec
                    assert 'payback_years' in rec

    def test_small_factory_recommendations(self, app, init_db):
        """Small factory gets appropriate recommendations"""
        with app.app_context():
            factory = make_factory(500)  # Small daily usage
            result = get_equipment_recommendations(factory)
            # Should still return recommendations (possibly fewer)
            assert isinstance(result, list)

    def test_large_factory_recommendations(self, app, init_db):
        """Large factory gets recommendations"""
        with app.app_context():
            factory = make_factory(50000)  # Large daily usage
            result = get_equipment_recommendations(factory)
            assert isinstance(result, list)
            # Large factories should get at least some recommendations
            assert len(result) > 0

    def test_different_industries(self, app, init_db):
        """Different industry types get recommendations"""
        with app.app_context():
            industries = ['Steel', 'Aluminum Smelting', 'Textile', 'Chemical']
            for industry in industries:
                factory = Factory(
                    name=f'{industry} Factory',
                    industry_type=industry,
                    voltage_level=10,
                    transformer_capacity=1000,
                    daily_usage=10000,
                    work_periods='[{"start": 8, "end": 18}]',
                    working_days_per_month=26,
                    user_id=1
                )
                db.session.add(factory)
                db.session.commit()

                result = get_equipment_recommendations(factory)
                assert isinstance(result, list), f"Failed for industry: {industry}"

                db.session.delete(factory)
                db.session.commit()

    def test_none_factory_returns_empty(self, app, init_db):
        """None factory returns empty list or None"""
        with app.app_context():
            result = get_equipment_recommendations(None)
            assert result is None or result == []

    def test_payback_years_positive(self, app, init_db):
        """Payback years should be positive"""
        with app.app_context():
            factory = make_factory(20000)
            result = get_equipment_recommendations(factory)
            for rec in result:
                assert rec['payback_years'] > 0
