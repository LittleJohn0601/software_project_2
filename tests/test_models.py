
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from blogapp import create_app, db
from blogapp.models import Factory, User

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def test_factory_carbon_emission(app):
    with app.app_context():
        # Create the user first
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        factory = Factory(
            name='Test Factory',
            voltage_level=10,
            transformer_capacity=1000,
            daily_usage=100.0,
            work_periods='[]',
            working_days_per_month=30,
            user_id=user.id
        )
        db.session.add(factory)
        db.session.commit()
        
        # Verify monthly usage calculation
        assert factory.monthly_usage == 3000.0
        
        # Verify carbon emission calculation
        expected_emission = round(3000.0 * 0.6634, 2)  # 1989.0
        assert factory.carbon_emission == expected_emission
        
        # Verify photovoltaic carbon savings calculation
        expected_pv_emission = round(3000.0 * 0.0520, 2)  # 156.0
        expected_savings = round(expected_emission - expected_pv_emission, 2)
        assert factory.pv_carbon_emission == expected_pv_emission
        assert factory.pv_carbon_savings == expected_savings
        assert factory.pv_carbon_savings_percentage == round(expected_savings / expected_emission * 100, 2)