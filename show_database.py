# show_database.py
"""
数据库内容查看脚本 - 在控制台打印所有数据
放在项目根目录运行
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# ============================================================
# 设置数据库路径 - 使用绝对路径避免路径问题
# ============================================================

# 定义数据库路径
instance_path = project_root / 'instance'
db_path = instance_path / 'greenlife.db'

# 确保 instance 目录存在
instance_path.mkdir(exist_ok=True)

# 设置数据库 URL（使用绝对路径，转换为 POSIX 格式）
# SQLite 路径需要使用正斜杠或 file:// 格式
db_url = f'sqlite:///{db_path.as_posix()}'
os.environ['DATABASE_URL'] = db_url

print(f"\n数据库路径: {db_url}")
print(f"数据库文件是否存在: {db_path.exists()}")
if db_path.exists():
    print(f"文件大小: {db_path.stat().st_size} bytes")
else:
    print("警告: 数据库文件不存在，将创建新数据库")

# ============================================================
# 导入应用和模型
# ============================================================

from blogapp import create_app, db
from blogapp.models import User, Factory, HourlyElectricityPrice, GridElectricityPrice, TimeOfUsePeriod


def print_separator(title):
    """打印分隔线"""
    print("\n" + "=" * 100)
    print(f"  {title}")
    print("=" * 100)


def print_table_data(title, data_list, max_width=25):
    """打印表数据"""
    if not data_list:
        print(f"\n{title}: 无数据")
        return
    
    print(f"\n{title}: 共 {len(data_list)} 条记录")
    print("-" * 100)
    
    # 获取所有字段
    if data_list:
        fields = list(data_list[0].keys())
        
        # 打印表头
        headers = []
        for field in fields:
            headers.append(f"{field:<{max_width}}")
        print(" | ".join(headers))
        print("-" * 100)
        
        # 打印数据行
        for row in data_list:
            values = []
            for field in fields:
                value = row.get(field, "")
                if isinstance(value, str) and len(value) > max_width:
                    value = value[:max_width-3] + "..."
                values.append(f"{str(value):<{max_width}}")
            print(" | ".join(values))
    
    print("-" * 100)


def main():
    """主函数"""
    app = create_app()
    
    with app.app_context():
        # 打印标题
        print("\n")
        print("█" * 100)
        print("█" + " " * 98 + "█")
        print("█" + " " * 35 + "数据库内容查看" + " " * 39 + "█")
        print("█" + " " * 98 + "█")
        print("█" * 100)
        
        # 打印实际使用的数据库路径
        actual_db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
        print(f"\n实际使用的数据库路径: {actual_db_uri}")
        
        # 1. 用户表
        users = User.query.all()
        users_data = []
        for u in users:
            users_data.append({
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'user_type': u.user_type,
                'created_at': u.created_at.strftime('%Y-%m-%d %H:%M:%S') if u.created_at else None
            })
        print_table_data("用户表 (User)", users_data, max_width=20)
        
        # 2. 工厂表
        factories = Factory.query.all()
        factories_data = []
        for f in factories:
            factories_data.append({
                'id': f.id,
                'name': f.name,
                'location': f.location or '-',
                'industry_type': f.industry_type or '-',
                'voltage_level': f"{f.voltage_level}kV",
                'transformer_capacity': f"{f.transformer_capacity}kVA",
                'daily_usage': f"{f.daily_usage}kWh",
                'working_days': f.working_days_per_month,
                'monthly_usage': f"{f.monthly_usage}kWh",
                'capacity_fee': f"¥{f.capacity_fee}",
                'user_id': f.user_id,
                'created_at': f.created_at.strftime('%Y-%m-%d') if f.created_at else None
            })
        print_table_data("工厂表 (Factory)", factories_data, max_width=18)
        
        # 单独打印工作时间段信息
        if factories:
            print("\n  工作时间段详情:")
            for f in factories:
                print(f"    - {f.name}: {f.work_periods}")
        
        # 3. 分时电价表
        hourly_prices = HourlyElectricityPrice.query.order_by(HourlyElectricityPrice.hour).all()
        hourly_data = []
        for hp in hourly_prices:
            hourly_data.append({
                'id': hp.id,
                'hour': f"{hp.hour}:00-{hp.hour+1}:00",
                'time_range': hp.time_range,
                'price': f"¥{hp.price}/kWh",
                'actual_price': f"¥{hp.actual_price}/kWh",
                'created_at': hp.created_at.strftime('%Y-%m-%d') if hp.created_at else None
            })
        print_table_data("分时电价表 (HourlyElectricityPrice)", hourly_data, max_width=18)
        
        # 4. 电网电价表
        grid_prices = GridElectricityPrice.query.order_by(GridElectricityPrice.voltage_level).all()
        grid_data = []
        for gp in grid_prices:
            grid_data.append({
                'id': gp.id,
                'voltage_level': f"{gp.voltage_level}kV",
                'peak_price': f"¥{gp.peak_price}/kWh",
                'normal_price': f"¥{gp.normal_price}/kWh",
                'valley_price': f"¥{gp.valley_price}/kWh",
                'capacity_price': f"¥{gp.capacity_price}/kVA·月",
                'created_at': gp.created_at.strftime('%Y-%m-%d') if gp.created_at else None
            })
        print_table_data("电网电价表 (GridElectricityPrice)", grid_data, max_width=18)
        
        # 5. 分时时段表
        tou_periods = TimeOfUsePeriod.query.order_by(TimeOfUsePeriod.hour).all()
        tou_data = []
        for tp in tou_periods:
            tou_data.append({
                'id': tp.id,
                'hour': f"{tp.hour}:00-{tp.hour+1}:00",
                'time_range': tp.time_range,
                'period_type': tp.period_type,
                'created_at': tp.created_at.strftime('%Y-%m-%d') if tp.created_at else None
            })
        print_table_data("分时时段表 (TimeOfUsePeriod)", tou_data, max_width=18)
        
        # 统计信息
        print("\n")
        print("=" * 100)
        print("  统计信息")
        print("=" * 100)
        print(f"  User 表记录数:                 {len(users)}")
        print(f"  Factory 表记录数:              {len(factories)}")
        print(f"  HourlyElectricityPrice 表记录数: {len(hourly_prices)}")
        print(f"  GridElectricityPrice 表记录数:   {len(grid_prices)}")
        print(f"  TimeOfUsePeriod 表记录数:        {len(tou_periods)}")
        print("=" * 100)
        print(f"  总计: {len(users) + len(factories) + len(hourly_prices) + len(grid_prices) + len(tou_periods)} 条记录")
        print("=" * 100)


if __name__ == '__main__':
    main()