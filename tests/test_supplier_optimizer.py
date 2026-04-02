# tests/test_supplier_optimizer.py
"""
供应商优化器后端测试代码
"""

import os
import sys
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置数据库路径
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
    """设置测试数据"""
    print("\n" + "="*80)
    print("设置测试数据")
    print("="*80)
    
    with app.app_context():
        # 创建测试用户
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
            print("✅ 创建测试用户")
        else:
            print("✅ 测试用户已存在")
        
        # 创建测试工厂
        factory = Factory.query.filter_by(name='测试工厂').first()
        if not factory:
            factory = Factory(
                name='测试工厂',
                location='测试地点',
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
            print("✅ 创建测试工厂")
        else:
            print("✅ 测试工厂已存在")
        
        # 创建电网价格数据
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
            print("✅ 创建电网价格数据")
        else:
            print("✅ 电网价格数据已存在")
        
        # 创建售电公司价格数据
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
        print("✅ 创建售电公司价格数据")
        
        # 创建分时时段数据
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
        print("✅ 创建分时时段数据")
        
        print("✅ 测试数据设置完成")
        return True


def test_supplier_valid_check(app):
    """测试1: 供应商价格约束检查"""
    print("\n" + "="*80)
    print("测试1: 供应商价格约束检查")
    print("="*80)
    
    with app.app_context():
        # 重新查询工厂对象
        factory = Factory.query.filter_by(name='测试工厂').first()
        if not factory:
            print("❌ 未找到测试工厂")
            return False
        
        grid_price = GridElectricityPrice.query.filter_by(voltage_level=10).first()
        supplier_prices = HourlyElectricityPrice.query.all()
        tou_periods = TimeOfUsePeriod.query.all()
        
        optimizer = SupplierOptimizer(factory, grid_price, supplier_prices, tou_periods)
        
        is_valid = optimizer.check_supplier_price_constraint()
        print(f"供应商价格是否满足约束 (≤ 电网×1.6): {is_valid}")
        
        print("\n价格对比（部分小时）:")
        print(f"{'小时':<6} {'电网价格':<12} {'售电价格':<12} {'最大允许':<12} {'是否满足':<10}")
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
    """测试2: 省钱模式优化"""
    print("\n" + "="*80)
    print("测试2: 省钱模式优化")
    print("="*80)
    
    with app.app_context():
        factory = Factory.query.filter_by(name='测试工厂').first()
        if not factory:
            print("❌ 未找到测试工厂")
            return None
        
        grid_price = GridElectricityPrice.query.filter_by(voltage_level=10).first()
        supplier_prices = HourlyElectricityPrice.query.all()
        tou_periods = TimeOfUsePeriod.query.all()
        
        optimizer = SupplierOptimizer(factory, grid_price, supplier_prices, tou_periods)
        
        result = optimizer.optimize(objective='cost')
        
        print(f"\n优化目标: 省钱模式")
        print(f"最优供应商: {result['best_supplier']['name']}")
        print(f"\n当前情况:")
        print(f"  月电费: {result['current']['cost']:,.2f} 元")
        print(f"  月碳排放: {result['current']['carbon']:,.2f} kg CO₂")
        print(f"\n优化后:")
        print(f"  月电费: {result['optimized']['cost']:,.2f} 元")
        print(f"  月碳排放: {result['optimized']['carbon']:,.2f} kg CO₂")
        print(f"\n节省:")
        print(f"  电费节省: {result['saving']['cost']:,.2f} 元/月")
        print(f"  碳减排: {result['saving']['carbon']:,.2f} kg CO₂/月")
        
        return result


def test_optimize_carbon_mode(app):
    """测试3: 减排模式优化"""
    print("\n" + "="*80)
    print("测试3: 减排模式优化")
    print("="*80)
    
    with app.app_context():
        factory = Factory.query.filter_by(name='测试工厂').first()
        if not factory:
            print("❌ 未找到测试工厂")
            return None
        
        grid_price = GridElectricityPrice.query.filter_by(voltage_level=10).first()
        supplier_prices = HourlyElectricityPrice.query.all()
        tou_periods = TimeOfUsePeriod.query.all()
        
        optimizer = SupplierOptimizer(factory, grid_price, supplier_prices, tou_periods)
        
        result = optimizer.optimize(objective='carbon')
        
        print(f"\n优化目标: 减排模式")
        print(f"最优供应商: {result['best_supplier']['name']}")
        print(f"\n当前情况:")
        print(f"  月电费: {result['current']['cost']:,.2f} 元")
        print(f"  月碳排放: {result['current']['carbon']:,.2f} kg CO₂")
        print(f"\n优化后:")
        print(f"  月电费: {result['optimized']['cost']:,.2f} 元")
        print(f"  月碳排放: {result['optimized']['carbon']:,.2f} kg CO₂")
        
        return result


def test_saving_potential(app):
    """测试4: 节省潜力计算"""
    print("\n" + "="*80)
    print("测试4: 节省潜力计算 API")
    print("="*80)
    
    with app.app_context():
        factory = Factory.query.filter_by(name='测试工厂').first()
        if not factory:
            print("❌ 未找到测试工厂")
            return None
        
        grid_price = GridElectricityPrice.query.filter_by(voltage_level=10).first()
        supplier_prices = HourlyElectricityPrice.query.all()
        tou_periods = TimeOfUsePeriod.query.all()
        
        optimizer = SupplierOptimizer(factory, grid_price, supplier_prices, tou_periods)
        
        cost_result = optimizer.get_saving_potential(mode='cost')
        print(f"\n省钱模式:")
        print(f"  节省潜力: {cost_result['saving_potential']['value']:,.2f} {cost_result['saving_potential']['unit']}")
        print(f"  描述: {cost_result['saving_potential']['description']}")
        
        carbon_result = optimizer.get_saving_potential(mode='carbon')
        print(f"\n减排模式:")
        print(f"  减排潜力: {carbon_result['saving_potential']['value']:,.2f} {carbon_result['saving_potential']['unit']}")
        print(f"  描述: {carbon_result['saving_potential']['description']}")
        
        return cost_result, carbon_result


def test_suggestions(app):
    """测试5: 优化建议生成"""
    print("\n" + "="*80)
    print("测试5: 优化建议生成")
    print("="*80)
    
    with app.app_context():
        factory = Factory.query.filter_by(name='测试工厂').first()
        if not factory:
            print("❌ 未找到测试工厂")
            return None
        
        grid_price = GridElectricityPrice.query.filter_by(voltage_level=10).first()
        supplier_prices = HourlyElectricityPrice.query.all()
        tou_periods = TimeOfUsePeriod.query.all()
        
        optimizer = SupplierOptimizer(factory, grid_price, supplier_prices, tou_periods)
        
        result = optimizer.get_suggestions()
        
        print(f"\n共生成 {len(result['suggestions'])} 条建议:")
        for i, suggestion in enumerate(result['suggestions'], 1):
            print(f"\n建议 {i}: {suggestion['title']}")
            print(f"  描述: {suggestion['description']}")
            print(f"  影响程度: {suggestion['impact']}")
            print(f"  预计节省: {suggestion['potential_saving']:,.2f} 元/月")
        
        return result


def run_all_tests():
    """运行所有测试"""
    print("\n")
    print("█"*80)
    print("█" + " "*78 + "█")
    print("█" + " "*20 + "供应商优化器后端测试" + " "*34 + "█")
    print("█" + " "*78 + "█")
    print("█"*80)
    
    app = create_app()
    
    try:
        with app.app_context():
            # 确保数据库表存在
            db.create_all()
            
            # 设置测试数据
            setup_test_data(app)
            
            # 运行测试
            test_supplier_valid_check(app)
            test_optimize_cost_mode(app)
            test_optimize_carbon_mode(app)
            test_saving_potential(app)
            test_suggestions(app)
            
            # 测试总结
            print("\n")
            print("="*80)
            print("测试总结")
            print("="*80)
            print("✅ 所有测试通过！")
            
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests()