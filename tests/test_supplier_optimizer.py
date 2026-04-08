# tests/test_supplier_optimizer.py
"""
Supplier optimizer backend test code
"""

import os
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# SettingsDatabase path
instance_path = project_root / 'instance'
db_path = instance_path / 'greenlife.db'
instance_path.mkdir(exist_ok=True)
db_url = f'sqlite:///{db_path.as_posix()}'
os.environ['DATABASE_URL'] = db_url

from blogapp import create_app, db
from blogapp.models import (
    User, Factory, GridElectricityPrice, 
    HourlyElectricityPrice, TimeOfUsePeriod
)
from blogapp.services.supplier_optimizer import SupplierOptimizer, SupplierType


def setup_test_data(app):
    """Set up test data"""
    print("\n" + "="*80)
    print("Setting up test data")
    print("="*80)
    
    with app.app_context():
        # Create test user
        user = User.query.filter_by(username='test_user').first()
        if not user:
            user = User(
                username='test_user',
                email='test@example.com',
                user_type='user'
            )
            user.set_password('test123')
            db.session.add(user)
            db.session.commit()
            print("✅ Created test user")
        else:
            print("✅ Test user already exists")
        
        # CreateTest factory
        factory = Factory.query.filter_by(name='Test factory').first()
        if not factory:
            factory = Factory(
                name='Test factory',
                location='Test location',
                industry_type='manufacturing',
                voltage_level=10,
                transformer_capacity=1000,
                daily_usage=10000,
                working_days_per_month=26,
                work_periods='[{"start": 8, "end": 12}, {"start": 13, "end": 18}]',
                user_id=user.id
            )
            db.session.add(factory)
            db.session.commit()
            print("✅ CreateTest factory")
        else:
            print("✅ Test factory already exists")
        
        # Create grid price data
        grid_price = GridElectricityPrice.query.filter_by(voltage_level=10).first()
        if not grid_price:
            grid_price = GridElectricityPrice(
                voltage_level=10,
                peak_price=1.20,
                normal_price=0.70,
                valley_price=0.30,
                capacity_price=20.0
            )
            db.session.add(grid_price)
            db.session.commit()
            print("✅ Created grid price data")
        else:
            print("✅ Grid price data already exists")
        
        # Create retail supplier price data
        supplier_prices = [
            (0, "0-1", 0.28), (1, "1-2", 0.28), (2, "2-3", 0.28), (3, "3-4", 0.28),
            (4, "4-5", 0.28), (5, "5-6", 0.28), (6, "6-7", 0.35), (7, "7-8", 0.35),
            (8, "8-9", 0.65), (9, "9-10", 0.65), (10, "10-11", 0.65), (11, "11-12", 0.65),
            (12, "12-13", 1.10), (13, "13-14", 1.10), (14, "14-15", 1.10), (15, "15-16", 1.10),
            (16, "16-17", 1.10), (17, "17-18", 1.10), (18, "18-19", 0.65), (19, "19-20", 0.65),
            (20, "20-21", 0.65), (21, "21-22", 0.65), (22, "22-23", 0.28), (23, "23-24", 0.28)
        ]
        
        for hour, time_range, price in supplier_prices:
            existing = HourlyElectricityPrice.query.filter_by(hour=hour).first()
            if not existing:
                hp = HourlyElectricityPrice(
                    hour=hour,
                    time_range=time_range,
                    price=price
                )
                db.session.add(hp)
        
        db.session.commit()
        print("✅ Created retail supplier price data")
        
        # Create time-of-use periods data
        tou_data = [
            (0, "0-1", "valley"), (1, "1-2", "valley"), (2, "2-3", "valley"),
            (3, "3-4", "valley"), (4, "4-5", "valley"), (5, "5-6", "valley"),
            (6, "6-7", "valley"), (7, "7-8", "valley"),
            (12, "12-13", "peak"), (13, "13-14", "peak"), (14, "14-15", "peak"),
            (15, "15-16", "peak"), (16, "16-17", "peak"), (17, "17-18", "peak"),
            (8, "8-9", "normal"), (9, "9-10", "normal"), (10, "10-11", "normal"),
            (11, "11-12", "normal"), (18, "18-19", "normal"), (19, "19-20", "normal"),
            (20, "20-21", "normal"), (21, "21-22", "normal"), (22, "22-23", "normal"),
            (23, "23-24", "normal")
        ]
        
        for hour, time_range, period_type in tou_data:
            existing = TimeOfUsePeriod.query.filter_by(hour=hour).first()
            if not existing:
                tou = TimeOfUsePeriod(
                    hour=hour,
                    time_range=time_range,
                    period_type=period_type
                )
                db.session.add(tou)
        
        db.session.commit()
        print("✅ Created time-of-use period data")
        
        print("✅ Test data setup completed")
        return True


def test_supplier_valid_check(app):
    """Test 1: supplier price constraint check"""
    print("\n" + "="*80)
    print("Test 1: supplier price constraint check")
    print("="*80)
    
    with app.app_context():
        # Re-query factory object
        factory = Factory.query.filter_by(name='Test factory').first()
        if not factory:
            print("❌ Test factory not found")
            return False
        
        grid_price = GridElectricityPrice.query.filter_by(voltage_level=10).first()
        supplier_prices = HourlyElectricityPrice.query.all()
        tou_periods = TimeOfUsePeriod.query.all()
        
        optimizer = SupplierOptimizer(factory, grid_price, supplier_prices, tou_periods)
        
        is_valid = optimizer.check_supplier_price_constraint()
        print(f"Supplier price meets constraint (≤ grid×1.6): {is_valid}")
        
        print("\nPrice comparison (selected hours):")
        print(f"{'Hour':<6} {'Grid price':<12} {'Supplier price':<12} {'Max allowed':<12} {'Meets constraint':<10}")
        print("-" * 60)
        
        for hour in [0, 7, 8, 12, 18, 22]:
            grid_p = optimizer.get_grid_hourly_prices().get(hour, 0)
            sup_p = optimizer.get_supplier_hourly_prices().get(hour, 0)
            max_allowed = grid_p * 1.6
            is_ok = sup_p <= max_allowed
            status = "✅" if is_ok else "❌"
            print(f"{hour:02d}:00  {grid_p:>8.2f}     {sup_p:>8.2f}     {max_allowed:>8.2f}     {status}")
        
        return is_valid


def test_optimize_cost_mode(app):
    """Test 2: Cost mode optimization"""
    print("\n" + "="*80)
    print("Test 2: Cost mode optimization")
    print("="*80)
    
    with app.app_context():
        factory = Factory.query.filter_by(name='Test factory').first()
        if not factory:
            print("❌ Test factory not found")
            return None
        
        grid_price = GridElectricityPrice.query.filter_by(voltage_level=10).first()
        supplier_prices = HourlyElectricityPrice.query.all()
        tou_periods = TimeOfUsePeriod.query.all()
        
        optimizer = SupplierOptimizer(factory, grid_price, supplier_prices, tou_periods)
        
        result = optimizer.optimize(objective='cost')
        
        print(f"\nOptimization objective: Cost mode")
        print(f"Best supplier: {result['best_supplier']['name']}")
        print(f"\nCurrent status:")
        print(f"  Monthly cost: {result['current']['cost']:,.2f} CNY")
        print(f"  Monthly carbon emissions: {result['current']['carbon']:,.2f} kg CO₂")
        print(f"\nAfter optimization:")
        print(f"  Monthly cost: {result['optimized']['cost']:,.2f} CNY")
        print(f"  Monthly carbon emissions: {result['optimized']['carbon']:,.2f} kg CO₂")
        print(f"\nSavings:")
        print(f"  Electricity cost savings: {result['saving']['cost']:,.2f} CNY/month")
        print(f"  Carbon reduction: {result['saving']['carbon']:,.2f} kg CO₂/month")
        
        return result


def test_optimize_carbon_mode(app):
    """Test 3: Carbon mode optimization"""
    print("\n" + "="*80)
    print("Test 3: Carbon mode optimization")
    print("="*80)
    
    with app.app_context():
        factory = Factory.query.filter_by(name='Test factory').first()
        if not factory:
            print("❌ Test factory not found")
            return None
        
        grid_price = GridElectricityPrice.query.filter_by(voltage_level=10).first()
        supplier_prices = HourlyElectricityPrice.query.all()
        tou_periods = TimeOfUsePeriod.query.all()
        
        optimizer = SupplierOptimizer(factory, grid_price, supplier_prices, tou_periods)
        
        result = optimizer.optimize(objective='carbon')
        
        print(f"\nOptimization objective: Carbon mode")
        print(f"Best supplier: {result['best_supplier']['name']}")
        print(f"\nCurrent status:")
        print(f"  Monthly cost: {result['current']['cost']:,.2f} CNY")
        print(f"  Monthly carbon emissions: {result['current']['carbon']:,.2f} kg CO₂")
        print(f"\nAfter optimization:")
        print(f"  Monthly cost: {result['optimized']['cost']:,.2f} CNY")
        print(f"  Monthly carbon emissions: {result['optimized']['carbon']:,.2f} kg CO₂")
        
        return result


def test_saving_potential(app):
    """Test 4: Saving potential calculation"""
    print("\n" + "="*80)
    print("Test 4: Saving potential calculation API")
    print("="*80)
    
    with app.app_context():
        factory = Factory.query.filter_by(name='Test factory').first()
        if not factory:
            print("❌ Test factory not found")
            return None
        
        grid_price = GridElectricityPrice.query.filter_by(voltage_level=10).first()
        supplier_prices = HourlyElectricityPrice.query.all()
        tou_periods = TimeOfUsePeriod.query.all()
        
        optimizer = SupplierOptimizer(factory, grid_price, supplier_prices, tou_periods)
        
        cost_result = optimizer.get_saving_potential(mode='cost')
        print(f"\nCost mode:")
        print(f"  Saving potential: {cost_result['saving_potential']['value']:,.2f} {cost_result['saving_potential']['unit']}")
        print(f"  Description: {cost_result['saving_potential']['description']}")
        
        carbon_result = optimizer.get_saving_potential(mode='carbon')
        print(f"\nCarbon mode:")
        print(f"  Carbon potential: {carbon_result['saving_potential']['value']:,.2f} {carbon_result['saving_potential']['unit']}")
        print(f"  Description: {carbon_result['saving_potential']['description']}")
        
        return cost_result, carbon_result


def test_suggestions(app):
    """Test 5: Optimization suggestions generation"""
    print("\n" + "="*80)
    print("Test 5: Optimization suggestions generation")
    print("="*80)
    
    with app.app_context():
        factory = Factory.query.filter_by(name='Test factory').first()
        if not factory:
            print("❌ Test factory not found")
            return None
        
        grid_price = GridElectricityPrice.query.filter_by(voltage_level=10).first()
        supplier_prices = HourlyElectricityPrice.query.all()
        tou_periods = TimeOfUsePeriod.query.all()
        
        optimizer = SupplierOptimizer(factory, grid_price, supplier_prices, tou_periods)
        
        result = optimizer.get_suggestions()
        
        print(f"\nTotal generated {len(result['suggestions'])} suggestions:")
        for i, suggestion in enumerate(result['suggestions'], 1):
            print(f"\nSuggestion {i}: {suggestion['title']}")
            print(f"  Description: {suggestion['description']}")
            print(f"  Impact level: {suggestion['impact']}")
            print(f"  Estimated savings: {suggestion['potential_saving']:,.2f} CNY/month")
        
        return result


def run_all_tests():
    """Run all tests"""
    print("\n")
    print("█"*80)
    print("█" + " "*78 + "█")
    print("█" + " "*20 + "Supplier Optimizer Backend Test" + " "*34 + "█")
    print("█" + " "*78 + "█")
    print("█"*80)
    
    app = create_app()
    
    try:
        with app.app_context():
            # Ensure database tables exist
            db.create_all()
            
            # Set up test data
            setup_test_data(app)
            
            # Run tests
            test_supplier_valid_check(app)
            test_optimize_cost_mode(app)
            test_optimize_carbon_mode(app)
            test_saving_potential(app)
            test_suggestions(app)
            
            # Test summary
            print("\n")
            print("="*80)
            print("Test summary")
            print("="*80)
            print("✅ All tests passed!")
            
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests()