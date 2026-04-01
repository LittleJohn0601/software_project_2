import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
import pytest
from blogapp import create_app, db
from blogapp.models import Factory, User, GridElectricityPrice, TimeOfUsePeriod
from blogapp.services.electricity_cost import ElectricityCostCalculator


@pytest.fixture(scope='function')
def app():
    """创建测试用的应用实例"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    return app


@pytest.fixture(scope='function')
def db_session(app):
    """每个测试函数独立的数据库会话"""
    with app.app_context():
        db.create_all()
        yield db.session
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def test_user(db_session):
    """创建测试用户"""
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture(scope='function')
def test_grid_price(db_session):
    """创建测试电价配置 - 必须包含所有字段"""
    # 检查是否已存在，避免重复插入
    existing = GridElectricityPrice.query.filter_by(voltage_level=10).first()
    if existing:
        return existing
    
    grid_price = GridElectricityPrice(
        voltage_level=10,
        peak_price=1.2,
        normal_price=0.8,
        valley_price=0.4,
        capacity_price=22.5  # 必须提供这个字段
    )
    db_session.add(grid_price)
    db_session.commit()
    return grid_price


@pytest.fixture(scope='function')
def test_tou_periods(db_session):
    """创建测试分时电价时段"""
    # 检查是否已存在数据
    if TimeOfUsePeriod.query.count() > 0:
        return TimeOfUsePeriod.query.all()
    
    periods_data = [
        (0, '0-1', '低谷'), (1, '1-2', '低谷'), (2, '2-3', '低谷'), (3, '3-4', '低谷'),
        (4, '4-5', '低谷'), (5, '5-6', '低谷'), (6, '6-7', '平时'), (7, '7-8', '平时'),
        (8, '8-9', '高峰'), (9, '9-10', '高峰'), (10, '10-11', '高峰'), (11, '11-12', '高峰'),
        (12, '12-13', '平时'), (13, '13-14', '平时'), (14, '14-15', '高峰'), (15, '15-16', '高峰'),
        (16, '16-17', '高峰'), (17, '17-18', '高峰'), (18, '18-19', '平时'), (19, '19-20', '平时'),
        (20, '20-21', '平时'), (21, '21-22', '平时'), (22, '22-23', '低谷'), (23, '23-0', '低谷')
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
    """创建测试工厂"""
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
    """电费计算器测试类"""
    
    def test_calculator_initialization(self, db_session, test_factory, test_grid_price, test_tou_periods):
        """测试计算器初始化"""
        calculator = ElectricityCostCalculator(test_factory.id)
        
        assert calculator.factory.id == test_factory.id
        assert calculator.factory.name == 'Test Factory'
        assert calculator.grid_price.voltage_level == 10
        # 使用实际的 grid_price 数据进行断言
        assert calculator.grid_price.peak_price == test_grid_price.peak_price
        assert len(calculator.tou_periods) == 24
        
    def test_calculator_factory_not_found(self, db_session):
        """测试工厂不存在的情况"""
        with pytest.raises(ValueError, match="Factory with id 999 not found"):
            ElectricityCostCalculator(999)
    
    def test_calculator_grid_price_not_found(self, db_session, test_user):
        """测试电价配置不存在的情况"""
        factory = Factory(
            name='Test Factory No Price',
            location='Test',
            industry_type='Test',
            voltage_level=35,  # 没有配置的电压等级
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
        """测试获取每小时电价"""
        calculator = ElectricityCostCalculator(test_factory.id)
        
        # 测试高峰时段电价
        assert calculator.get_price_for_hour(8) == 1.2
        assert calculator.get_price_for_hour(10) == 1.2
        assert calculator.get_price_for_hour(14) == 1.2
        
        # 测试平时电价
        assert calculator.get_price_for_hour(12) == 0.8
        assert calculator.get_price_for_hour(18) == 0.8
        assert calculator.get_price_for_hour(6) == 0.8
        
        # 测试低谷电价
        assert calculator.get_price_for_hour(22) == 0.4
        assert calculator.get_price_for_hour(0) == 0.4
        assert calculator.get_price_for_hour(4) == 0.4
    
    def test_calculate_monthly_cost_basic(self, db_session, test_factory, test_grid_price, test_tou_periods):
        """测试基本月电费计算"""
        calculator = ElectricityCostCalculator(test_factory.id)
        result = calculator.calculate_monthly_cost()
        
        # 验证结果结构
        assert 'factory_id' in result
        assert 'factory_name' in result
        assert 'total_usage' in result
        assert 'daily_energy_cost' in result
        assert 'monthly_energy_cost' in result
        assert 'capacity_fee' in result
        assert 'total_monthly_cost' in result
        assert 'hourly_breakdown' in result
        
        # 验证工厂信息
        assert result['factory_id'] == test_factory.id
        assert result['factory_name'] == 'Test Factory'
        assert result['voltage_level'] == 10
        assert result['month_days'] == 22
        
        # 验证用电量计算
        expected_usage = test_factory.daily_usage * test_factory.working_days_per_month
        assert result['total_usage'] == expected_usage
        assert result['daily_usage'] == test_factory.daily_usage
        
        # 验证容量电费
        expected_capacity_fee = test_factory.transformer_capacity * 22.5
        assert result['capacity_fee'] == expected_capacity_fee
        
        # 验证电费合理性
        assert result['daily_energy_cost'] > 0
        assert result['monthly_energy_cost'] > 0
        assert result['total_monthly_cost'] > 0
        
        # 验证平均电价在合理范围内（0.4-1.2之间）
        assert 0.4 <= result['average_price'] <= 1.2
    
    def test_capacity_fee_calculation(self, db_session, test_user, test_grid_price, test_tou_periods):
        """测试容量电费计算"""
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
        """测试边界情况"""
        # 测试零用电量
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
        assert result['capacity_fee'] > 0  # 容量电费仍然存在
        
        # 测试空工作时间表
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
        
        # 没有工作时间，用电量应该为0
        assert result['total_usage'] == 0
        for hour in result['hourly_breakdown']:
            assert hour['usage'] == 0


def test_integration_with_real_data(app, db_session):
    """集成测试：使用真实数据场景"""
    with app.app_context():
        # 创建用户
        user = User(username='integration_user', email='integration@test.com')
        user.set_password('test123')
        db_session.add(user)
        db_session.flush()
        
        # 创建电价配置 - 必须包含 capacity_price
        grid_price = GridElectricityPrice(
            voltage_level=10,
            peak_price=1.2594,
            normal_price=0.8231,
            valley_price=0.3182,
            capacity_price=22.5
        )
        db_session.add(grid_price)
        
        # 创建分时时段
        periods_data = [
            (0, '0-1', '低谷'), (1, '1-2', '低谷'), (2, '2-3', '低谷'), (3, '3-4', '低谷'),
            (4, '4-5', '低谷'), (5, '5-6', '低谷'), (6, '6-7', '平时'), (7, '7-8', '平时'),
            (8, '8-9', '高峰'), (9, '9-10', '高峰'), (10, '10-11', '高峰'), (11, '11-12', '高峰'),
            (12, '12-13', '平时'), (13, '13-14', '平时'), (14, '14-15', '高峰'), (15, '15-16', '高峰'),
            (16, '16-17', '高峰'), (17, '17-18', '高峰'), (18, '18-19', '平时'), (19, '19-20', '平时'),
            (20, '20-21', '平时'), (21, '21-22', '平时'), (22, '22-23', '低谷'), (23, '23-0', '低谷')
        ]
        
        for hour, time_range, period_type in periods_data:
            period = TimeOfUsePeriod(
                hour=hour,
                time_range=time_range,
                period_type=period_type
            )
            db_session.add(period)
        
        # 创建工厂
        factory = Factory(
            name='真实工厂',
            location='深圳市南山区',
            industry_type='电子制造',
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
        
        # 计算电费
        calculator = ElectricityCostCalculator(factory.id)
        result = calculator.calculate_monthly_cost()
        
        # 验证结果
        assert result['total_usage'] > 0
        assert result['total_monthly_cost'] > 0
        assert result['capacity_fee'] == 800 * 22.5
        assert len(result['hourly_breakdown']) == 24
        
        # 打印结果
        print(f"\n工厂名称: {result['factory_name']}")
        print(f"月用电量: {result['total_usage']} kWh")
        print(f"电度电费: {result['monthly_energy_cost']} 元")
        print(f"容量电费: {result['capacity_fee']} 元")
        print(f"总电费: {result['total_monthly_cost']} 元")
        print(f"平均电价: {result['average_price']} 元/kWh")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])