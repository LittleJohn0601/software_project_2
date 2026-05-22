"""
Supplier Optimizer Tests
Tests the supplier price comparison and optimization logic.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from blogapp import create_app, db
from blogapp.models import (
    User, Factory, GridElectricityPrice,
    HourlyElectricityPrice, TimeOfUsePeriod
)
from blogapp.services.supplier_optimizer import SupplierOptimizer


@pytest.fixture(scope='function')
def app():
    """Create test application"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    return app


@pytest.fixture(scope='function')
def setup_data(app):
    """Set up all required test data"""
    with app.app_context():
        db.create_all()

        # Create user
        user = User(username='test_user', email='test@example.com', user_type='user')
        user.set_password('test123')
        db.session.add(user)
        db.session.commit()

        # Create factory
        factory = Factory(
            name='Test factory',
            location='Test location',
            industry_type='Steel',
            voltage_level=10,
            transformer_capacity=1000,
            daily_usage=10000,
            working_days_per_month=26,
            work_periods='[{"start": 8, "end": 12}, {"start": 13, "end": 18}]',
            user_id=user.id
        )
        db.session.add(factory)
        db.session.commit()

        # Create grid price
        grid_price = GridElectricityPrice(
            voltage_level=10,
            peak_price=1.20,
            normal_price=0.70,
            valley_price=0.30,
            capacity_price=20.0
        )
        db.session.add(grid_price)

        # Create supplier hourly prices
        supplier_prices_data = [
            (0, "0-1", 0.28), (1, "1-2", 0.28), (2, "2-3", 0.28), (3, "3-4", 0.28),
            (4, "4-5", 0.28), (5, "5-6", 0.28), (6, "6-7", 0.35), (7, "7-8", 0.35),
            (8, "8-9", 0.65), (9, "9-10", 0.65), (10, "10-11", 0.65), (11, "11-12", 0.65),
            (12, "12-13", 1.10), (13, "13-14", 1.10), (14, "14-15", 1.10), (15, "15-16", 1.10),
            (16, "16-17", 1.10), (17, "17-18", 1.10), (18, "18-19", 0.65), (19, "19-20", 0.65),
            (20, "20-21", 0.65), (21, "21-22", 0.65), (22, "22-23", 0.28), (23, "23-24", 0.28)
        ]
        for hour, time_range, price in supplier_prices_data:
            db.session.add(HourlyElectricityPrice(hour=hour, time_range=time_range, price=price))

        # Create TOU periods
        tou_data = [
            (0, "0-1", "Valley"), (1, "1-2", "Valley"), (2, "2-3", "Valley"),
            (3, "3-4", "Valley"), (4, "4-5", "Valley"), (5, "5-6", "Valley"),
            (6, "6-7", "Valley"), (7, "7-8", "Valley"),
            (8, "8-9", "Normal"), (9, "9-10", "Normal"), (10, "10-11", "Normal"),
            (11, "11-12", "Normal"), (12, "12-13", "Peak"), (13, "13-14", "Peak"),
            (14, "14-15", "Peak"), (15, "15-16", "Peak"), (16, "16-17", "Peak"),
            (17, "17-18", "Peak"), (18, "18-19", "Normal"), (19, "19-20", "Normal"),
            (20, "20-21", "Normal"), (21, "21-22", "Normal"), (22, "22-23", "Normal"),
            (23, "23-24", "Normal")
        ]
        for hour, time_range, period_type in tou_data:
            db.session.add(TimeOfUsePeriod(hour=hour, time_range=time_range, period_type=period_type))

        db.session.commit()

        yield {
            'factory': factory,
            'grid_price': grid_price,
        }

        db.session.remove()
        db.drop_all()


def test_supplier_valid_check(app, setup_data):
    """Test supplier price constraint check"""
    with app.app_context():
        factory = Factory.query.first()
        grid_price = GridElectricityPrice.query.filter_by(voltage_level=10).first()
        supplier_prices = HourlyElectricityPrice.query.all()
        tou_periods = TimeOfUsePeriod.query.all()

        optimizer = SupplierOptimizer(factory, grid_price, supplier_prices, tou_periods)
        is_valid = optimizer.check_supplier_price_constraint()

        # Should return a boolean
        assert isinstance(is_valid, bool)


def test_optimize_cost_mode(app, setup_data):
    """Test cost optimization mode"""
    with app.app_context():
        factory = Factory.query.first()
        grid_price = GridElectricityPrice.query.filter_by(voltage_level=10).first()
        supplier_prices = HourlyElectricityPrice.query.all()
        tou_periods = TimeOfUsePeriod.query.all()

        optimizer = SupplierOptimizer(factory, grid_price, supplier_prices, tou_periods)
        result = optimizer.optimize(objective='cost')

        assert 'best_supplier' in result
        assert 'current' in result
        assert 'optimized' in result
        assert 'saving' in result
        assert result['current']['cost'] > 0


def test_optimize_carbon_mode(app, setup_data):
    """Test carbon optimization mode"""
    with app.app_context():
        factory = Factory.query.first()
        grid_price = GridElectricityPrice.query.filter_by(voltage_level=10).first()
        supplier_prices = HourlyElectricityPrice.query.all()
        tou_periods = TimeOfUsePeriod.query.all()

        optimizer = SupplierOptimizer(factory, grid_price, supplier_prices, tou_periods)
        result = optimizer.optimize(objective='carbon')

        assert 'best_supplier' in result
        assert result['current']['carbon'] > 0


def test_saving_potential(app, setup_data):
    """Test saving potential calculation"""
    with app.app_context():
        factory = Factory.query.first()
        grid_price = GridElectricityPrice.query.filter_by(voltage_level=10).first()
        supplier_prices = HourlyElectricityPrice.query.all()
        tou_periods = TimeOfUsePeriod.query.all()

        optimizer = SupplierOptimizer(factory, grid_price, supplier_prices, tou_periods)

        cost_result = optimizer.get_saving_potential(mode='cost')
        assert 'saving_potential' in cost_result
        assert 'value' in cost_result['saving_potential']
        assert 'unit' in cost_result['saving_potential']

        carbon_result = optimizer.get_saving_potential(mode='carbon')
        assert 'saving_potential' in carbon_result


def test_suggestions(app, setup_data):
    """Test optimization suggestions generation"""
    with app.app_context():
        factory = Factory.query.first()
        grid_price = GridElectricityPrice.query.filter_by(voltage_level=10).first()
        supplier_prices = HourlyElectricityPrice.query.all()
        tou_periods = TimeOfUsePeriod.query.all()

        optimizer = SupplierOptimizer(factory, grid_price, supplier_prices, tou_periods)
        result = optimizer.get_suggestions()

        assert 'suggestions' in result
        assert isinstance(result['suggestions'], list)
        # Each suggestion should have required fields
        for s in result['suggestions']:
            assert 'title' in s
            assert 'description' in s
            assert 'impact' in s
