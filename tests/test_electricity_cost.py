import sys
import os
import pytest

print("="*60)
print("电费计算功能测试")
print("="*60)

from blogapp import create_app, db
from blogapp.models import User, Factory, GridElectricityPrice, TimeOfUsePeriod
from blogapp.services.electricity_cost import ElectricityCostCalculator


@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        setup_test_data()
        yield app
        db.drop_all()


def setup_test_data():
    """设置测试数据"""
    # 不需要 with app.app_context()，因为已经在 fixture 中了
    # 检查是否已有数据
    if Factory.query.count() > 0:
        print("✅ 已有工厂数据，直接使用")
        return
    
    print("\n📝 创建测试数据...")
    
    # 创建用户
    user = User(
        username='testuser',
        email='test@example.com',
        user_type='user'
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.flush()
    
    # 检查电网电价是否已存在（create_app 可能已经导入）
    if GridElectricityPrice.query.count() == 0:
        # 创建电网电价
        grid_prices = [
            GridElectricityPrice(voltage_level=10, peak_price=0.74, normal_price=0.57, valley_price=0.41, capacity_price=22.5),
            GridElectricityPrice(voltage_level=35, peak_price=0.71, normal_price=0.54, valley_price=0.38, capacity_price=22.5),
        ]
        for price in grid_prices:
            db.session.add(price)
    
    # 检查分时时段是否已存在
    if TimeOfUsePeriod.query.count() == 0:
        # 创建分时时段
        tou_config = [
            (0, 7, '低谷'), (7, 8, '平时'), (8, 11, '高峰'),
            (11, 13, '低谷'), (13, 17, '平时'), (17, 23, '高峰'), (23, 24, '平时'),
        ]
        for start, end, period_type in tou_config:
            for hour in range(start, end):
                tou = TimeOfUsePeriod(
                    hour=hour,
                    time_range=f"{hour:02d}:00-{(hour+1):02d}:00",
                    period_type=period_type
                )
                db.session.add(tou)
    
    # 创建工厂
    factory = Factory(
        name='测试工厂',
        location='上海',
        industry_type='制造业',
        voltage_level=10,
        transformer_capacity=1000,
        daily_usage=10000,
        working_days_per_month=26,
        work_periods='[{"start": 8, "end": 12}, {"start": 13, "end": 17}]',
        user_id=user.id
    )
    db.session.add(factory)
    
    db.session.commit()
    print(f"✅ 创建测试工厂: {factory.name}")


def test_calculator(app):
    """测试电费计算器"""
    with app.app_context():
        factories = Factory.query.all()
        
        if not factories:
            print("❌ 没有工厂数据")
            return
        
        for factory in factories:
            print(f"\n{'='*60}")
            print(f"工厂: {factory.name}")
            print(f"{'='*60}")
            print(f"电压等级: {factory.voltage_level}kV")
            print(f"变压器容量: {factory.transformer_capacity} kVA")
            print(f"日用电量: {factory.daily_usage} kWh/天")
            print(f"工作天数: {factory.working_days_per_month} 天/月")
            
            # 计算电费
            calculator = ElectricityCostCalculator(factory.id)
            result = calculator.calculate_monthly_cost()
            
            print(f"\n📊 电费计算结果:")
            print(f"  月总用电量: {result['total_usage']:,.2f} kWh")
            print(f"  月电量电费: {result['monthly_energy_cost']:,.2f} 元")
            print(f"  容量电费: {result['capacity_fee']:,.2f} 元")
            print(f"  月总电费: {result['total_monthly_cost']:,.2f} 元")
            print(f"  平均电价: {result['average_price']:.4f} 元/kWh")
            
            print(f"\n⏰ 每小时用电明细:")
            print(f"{'时段':<15} {'用电量(kWh)':<12} {'电价(元)':<12} {'成本(元)':<12} {'时段类型':<10}")
            print("-" * 65)
            
            for hour in result['hourly_breakdown']:
                if hour['usage'] > 0:
                    print(f"{hour['time_range']:<15} {hour['usage']:<12.2f} {hour['price']:<12.4f} "
                          f"{hour['cost']:<12.2f} {hour['period_type']:<10}")
            
            return result


def test_capacity_fee(app):
    """测试容量电费计算"""
    with app.app_context():
        factories = Factory.query.all()
        
        print(f"\n{'='*60}")
        print("容量电费计算测试")
        print(f"{'='*60}")
        
        for factory in factories:
            print(f"\n工厂: {factory.name}")
            print(f"  电压等级: {factory.voltage_level}kV")
            print(f"  变压器容量: {factory.transformer_capacity} kVA")
            print(f"  容量电费: {factory.capacity_fee} 元/月")
            
            # 计算理论值
            grid_price = GridElectricityPrice.query.filter_by(
                voltage_level=factory.voltage_level
            ).first()
            if grid_price:
                expected = factory.transformer_capacity * grid_price.capacity_price
                print(f"  理论值: {expected} 元/月")
                print(f"  ✅ 计算正确" if factory.capacity_fee == expected else "  ❌ 计算错误")


if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        print("\n🔧 初始化测试数据...")
        setup_test_data()
        
        # 运行测试
        test_capacity_fee()
        result = test_calculator()
        
        print("\n" + "="*60)
        print("✅ 电费计算功能测试完成!")
        print("="*60)