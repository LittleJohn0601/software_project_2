import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
import pytest
from blogapp import create_app, db
from blogapp.models import Factory, User, GridElectricityPrice, TimeOfUsePeriod
from blogapp.services.electricity_cost import ElectricityCostCalculator


@pytest.fixture(scope='function')
def app():
    """Create test application instance"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    return app


@pytest.fixture(scope='function')
def db_session(app):
    """Database session isolated for each test function"""
    with app.app_context():
        db.create_all()
        yield db.session
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def test_user(db_session):
    """Create test user"""
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture(scope='function')
def test_grid_price(db_session):
    """Create test electricity price configuration - must include all fields"""
    # Check existence to avoid duplicate inserts
    existing = GridElectricityPrice.query.filter_by(voltage_level=10).first()
    if existing:
        return existing
    
    grid_price = GridElectricityPrice(
        voltage_level=10,
        peak_price=1.2,
        normal_price=0.8,
        valley_price=0.4,
        capacity_price=22.5  # Must provide this field
    )
    db_session.add(grid_price)
    db_session.commit()
    return grid_price


@pytest.fixture(scope='function')
def test_tou_periods(db_session):
    """Create test time-of-use pricing periods"""
    # Check if data already exists
    if TimeOfUsePeriod.query.count() > 0:
        return TimeOfUsePeriod.query.all()
    
    periods_data = [
        (0, '0-1', 'Valley'), (1, '1-2', 'Valley'), (2, '2-3', 'Valley'), (3, '3-4', 'Valley'),
        (4, '4-5', 'Valley'), (5, '5-6', 'Valley'), (6, '6-7', 'Normal'), (7, '7-8', 'Normal'),
        (8, '8-9', 'Peak'), (9, '9-10', 'Peak'), (10, '10-11', 'Peak'), (11, '11-12', 'Peak'),
        (12, '12-13', 'Normal'), (13, '13-14', 'Normal'), (14, '14-15', 'Peak'), (15, '15-16', 'Peak'),
        (16, '16-17', 'Peak'), (17, '17-18', 'Peak'), (18, '18-19', 'Normal'), (19, '19-20', 'Normal'),
        (20, '20-21', 'Normal'), (21, '21-22', 'Normal'), (22, '22-23', 'Valley'), (23, '23-0', 'Valley')
    ]
    
    for hour, time_range, period_type in periods_data:
        period = TimeOfUsePeriod(
            hour=hour,
            time_range=time_range,
            period_type=period_type
        )
        db_session.add(period)
    db_session.commit()
    return periods_data


@pytest.fixture(scope='function')
def test_factory(db_session, test_user, test_grid_price, test_tou_periods):
    """CreateTest factory"""
    work_periods = [
        {'start': 8, 'end': 12},
        {'start': 13, 'end': 17}
    ]
    
    factory = Factory(
        name='Test Factory',
        location='Test Location',
        industry_type='Manufacturing',
        voltage_level=10,
        transformer_capacity=500,
        daily_usage=200.0,
        work_periods=json.dumps(work_periods),
        working_days_per_month=22,
        user_id=test_user.id
    )
    db_session.add(factory)
    db_session.commit()
    return factory


class TestElectricityCostCalculator:
    """Electricity cost calculator test class"""
    
    def test_calculator_initialization(self, db_session, test_factory, test_grid_price, test_tou_periods):
        """Test calculator initialization"""
        calculator = ElectricityCostCalculator(test_factory.id)
        
        assert calculator.factory.id == test_factory.id
        assert calculator.factory.name == 'Test Factory'
        assert calculator.grid_price.voltage_level == 10
        # Use actual grid_price data for assertions
        assert calculator.grid_price.peak_price == test_grid_price.peak_price
        assert len(calculator.tou_periods) == 24
        
    def test_calculator_factory_not_found(self, db_session):
        """Test factory not found case"""
        with pytest.raises(ValueError, match="Factory with id 999 not found"):
            ElectricityCostCalculator(999)
    
    def test_calculator_grid_price_not_found(self, db_session, test_user):
        """Test grid price configuration missing case"""
        factory = Factory(
            name='Test Factory No Price',
            location='Test',
            industry_type='Test',
            voltage_level=35,  # Unconfigured voltage level
            transformer_capacity=500,
            daily_usage=200.0,
            work_periods='[]',
            working_days_per_month=22,
            user_id=test_user.id
        )
        db_session.add(factory)
        db_session.commit()
        
        with pytest.raises(ValueError, match="Grid price not found for voltage level 35"):
            ElectricityCostCalculator(factory.id)
    
    def test_get_price_for_hour(self, db_session, test_factory, test_grid_price, test_tou_periods):
        """Test get price for hour"""
        calculator = ElectricityCostCalculator(test_factory.id)
        
        # Test peak period electricity price
        assert calculator.get_price_for_hour(8) == 1.2
        assert calculator.get_price_for_hour(10) == 1.2
        assert calculator.get_price_for_hour(14) == 1.2
        
        # Test normal electricity price
        assert calculator.get_price_for_hour(12) == 0.8
        assert calculator.get_price_for_hour(18) == 0.8
        assert calculator.get_price_for_hour(6) == 0.8
        
        # Test valley electricity price
        assert calculator.get_price_for_hour(22) == 0.4
        assert calculator.get_price_for_hour(0) == 0.4
        assert calculator.get_price_for_hour(4) == 0.4
    
    def test_calculate_monthly_cost_basic(self, db_session, test_factory, test_grid_price, test_tou_periods):
        """Test basic monthly cost calculation"""
        calculator = ElectricityCostCalculator(test_factory.id)
        result = calculator.calculate_monthly_cost()
        
        # Verify result structure
        assert 'factory_id' in result
        assert 'factory_name' in result
        assert 'total_usage' in result
        assert 'daily_energy_cost' in result
        assert 'monthly_energy_cost' in result
        assert 'capacity_fee' in result
        assert 'total_monthly_cost' in result
        assert 'hourly_breakdown' in result
        
        # Verify factory information
        assert result['factory_id'] == test_factory.id
        assert result['factory_name'] == 'Test Factory'
        assert result['voltage_level'] == 10
        assert result['month_days'] == 22
        
        # Verify usage calculation
        expected_usage = test_factory.daily_usage * test_factory.working_days_per_month
        assert result['total_usage'] == expected_usage
        assert result['daily_usage'] == test_factory.daily_usage
        
        # Verify capacity fee
        expected_capacity_fee = test_factory.transformer_capacity * 22.5
        assert result['capacity_fee'] == expected_capacity_fee
        
        # Verify cost reasonableness
        assert result['daily_energy_cost'] > 0
        assert result['monthly_energy_cost'] > 0
        assert result['total_monthly_cost'] > 0
        
        # Verify average price is within a reasonable range (0.4-1.2)
        assert 0.4 <= result['average_price'] <= 1.2
    
    def test_capacity_fee_calculation(self, db_session, test_user, test_grid_price, test_tou_periods):
        """Test capacity fee calculation"""
        capacities = [315, 500, 800, 1000, 1250]
        
        for capacity in capacities:
            factory = Factory(
                name=f'Factory {capacity}kVA',
                location='Test',
                industry_type='Test',
                voltage_level=10,
                transformer_capacity=capacity,
                daily_usage=100.0,
                work_periods='[{"start": 8, "end": 17}]',
                working_days_per_month=22,
                user_id=test_user.id
            )
            db_session.add(factory)
            db_session.commit()
            
            calculator = ElectricityCostCalculator(factory.id)
            result = calculator.calculate_monthly_cost()
            
            expected_capacity_fee = capacity * 22.5
            assert result['capacity_fee'] == expected_capacity_fee
            
            db_session.delete(factory)
            db_session.commit()
    
    def test_edge_cases(self, db_session, test_user, test_grid_price, test_tou_periods):
        """Test edge cases"""
        # Test zero electricity usage
        factory_zero = Factory(
            name='Zero Usage Factory',
            location='Test',
            industry_type='Test',
            voltage_level=10,
            transformer_capacity=500,
            daily_usage=0,
            work_periods='[{"start": 8, "end": 17}]',
            working_days_per_month=22,
            user_id=test_user.id
        )
        db_session.add(factory_zero)
        db_session.commit()
        
        calculator = ElectricityCostCalculator(factory_zero.id)
        result = calculator.calculate_monthly_cost()
        
        assert result['total_usage'] == 0
        assert result['daily_energy_cost'] == 0
        assert result['monthly_energy_cost'] == 0
        assert result['average_price'] == 0
        assert result['capacity_fee'] > 0  # Capacity fee still exists
        
        # Test empty work schedule
        factory_empty = Factory(
            name='Empty Schedule Factory',
            location='Test',
            industry_type='Test',
            voltage_level=10,
            transformer_capacity=500,
            daily_usage=100,
            work_periods='[]',
            working_days_per_month=22,
            user_id=test_user.id
        )
        db_session.add(factory_empty)
        db_session.commit()
        
        calculator = ElectricityCostCalculator(factory_empty.id)
        result = calculator.calculate_monthly_cost()
        
        # No work time, electricity usage should be 0
        assert result['total_usage'] == 0
        for hour in result['hourly_breakdown']:
            assert hour['usage'] == 0


def test_integration_with_real_data(app, db_session):
    """Integration test: using real data scenario"""
    with app.app_context():
        # Create user
        user = User(username='integration_user', email='integration@test.com')
        user.set_password('test123')
        db_session.add(user)
        db_session.flush()
        
        # Create electricity price configuration - must include capacity_price
        grid_price = GridElectricityPrice(
            voltage_level=10,
            peak_price=1.2594,
            normal_price=0.8231,
            valley_price=0.3182,
            capacity_price=22.5
        )
        db_session.add(grid_price)
        
        # Create time-of-use periods
        periods_data = [
            (0, '0-1', 'Valley'), (1, '1-2', 'Valley'), (2, '2-3', 'Valley'), (3, '3-4', 'Valley'),
            (4, '4-5', 'Valley'), (5, '5-6', 'Valley'), (6, '6-7', 'Normal'), (7, '7-8', 'Normal'),
            (8, '8-9', 'Peak'), (9, '9-10', 'Peak'), (10, '10-11', 'Peak'), (11, '11-12', 'Peak'),
            (12, '12-13', 'Normal'), (13, '13-14', 'Normal'), (14, '14-15', 'Peak'), (15, '15-16', 'Peak'),
            (16, '16-17', 'Peak'), (17, '17-18', 'Peak'), (18, '18-19', 'Normal'), (19, '19-20', 'Normal'),
            (20, '20-21', 'Normal'), (21, '21-22', 'Normal'), (22, '22-23', 'Valley'), (23, '23-0', 'Valley')
        ]
        
        for hour, time_range, period_type in periods_data:
            period = TimeOfUsePeriod(
                hour=hour,
                time_range=time_range,
                period_type=period_type
            )
            db_session.add(period)
        
        # Create factory
        factory = Factory(
            name='Real Factory',
            location='Nanshan District, Shenzhen',
            industry_type='Electronics Manufacturing',
            voltage_level=10,
            transformer_capacity=800,
            daily_usage=1250.5,
            work_periods=json.dumps([
                {'start': 8, 'end': 12},
                {'start': 13, 'end': 17},
                {'start': 18, 'end': 21}
            ]),
            working_days_per_month=22,
            user_id=user.id
        )
        db_session.add(factory)
        db_session.commit()
        
        # Calculate electricity cost
        calculator = ElectricityCostCalculator(factory.id)
        result = calculator.calculate_monthly_cost()
        
        # Verify results
        assert result['total_usage'] > 0
        assert result['total_monthly_cost'] > 0
        assert result['capacity_fee'] == 800 * 22.5
        assert len(result['hourly_breakdown']) == 24
        
        # Print results
        print(f"\nFactory name: {result['factory_name']}")
        print(f"Monthly electricity usage: {result['total_usage']} kWh")
        print(f"Energy charge: {result['monthly_energy_cost']} CNY")
        print(f"Capacity fee: {result['capacity_fee']} CNY")
        print(f"Total electricity cost: {result['total_monthly_cost']} CNY")
        print(f"Average electricity price: {result['average_price']} CNY/kWh")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])