# show_database.py
"""
Database content viewer script - print all data to the console
Run from the project root directory
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# ============================================================
# Set database path - use absolute path to avoid issues
# ============================================================

# Define database path
instance_path = project_root / 'instance'
db_path = instance_path / 'greenlife.db'

# Ensure instance directory exists
instance_path.mkdir(exist_ok=True)

# Set database URL (use absolute path, convert to POSIX format)
# SQLite paths require forward slashes or file:// format
db_url = f'sqlite:///{db_path.as_posix()}'
os.environ['DATABASE_URL'] = db_url

print(f"\nDatabase path: {db_url}")
print(f"Database file exists: {db_path.exists()}")
if db_path.exists():
    print(f"File size: {db_path.stat().st_size} bytes")
else:
    print("Warning: database file not found, will create new database")

# ============================================================
# Import app and models
# ============================================================

from blogapp import create_app, db
from blogapp.models import User, Factory, HourlyElectricityPrice, GridElectricityPrice, TimeOfUsePeriod


def print_separator(title):
    """Print separator line"""
    print("\n" + "=" * 100)
    print(f"  {title}")
    print("=" * 100)


def print_table_data(title, data_list, max_width=25):
    """Print table data"""
    if not data_list:
        print(f"\n{title}: No data")
        return
    
    print(f"\n{title}: Total {len(data_list)} records")
    print("-" * 100)
    
    # Get all fields
    if data_list:
        fields = list(data_list[0].keys())
        
        # Print table header
        headers = []
        for field in fields:
            headers.append(f"{field:<{max_width}}")
        print(" | ".join(headers))
        print("-" * 100)
        
        # Print data rows
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
    """Main function"""
    app = create_app()
    
    with app.app_context():
        # Print title
        print("\n")
        print("█" * 100)
        print("█" + " " * 98 + "█")
        print("█" + " " * 35 + "Database Content Viewer" + " " * 39 + "█")
        print("█" + " " * 98 + "█")
        print("█" * 100)
        
        # Print actual database path in use
        actual_db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
        print(f"\nActual database path in use: {actual_db_uri}")
        
        # 1. User table
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
        print_table_data("User table (User)", users_data, max_width=20)
        
        # 2. Factory table
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
        print_table_data("Factory table (Factory)", factories_data, max_width=18)
        
        # Print work periods information separately
        if factories:
            print("\n  Work periods details:")
            for f in factories:
                print(f"    - {f.name}: {f.work_periods}")
        
        # 3. Hourly electricity price table
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
        print_table_data("Hourly electricity price table (HourlyElectricityPrice)", hourly_data, max_width=18)
        
        # 4. Grid electricity price table
        grid_prices = GridElectricityPrice.query.order_by(GridElectricityPrice.voltage_level).all()
        grid_data = []
        for gp in grid_prices:
            grid_data.append({
                'id': gp.id,
                'voltage_level': f"{gp.voltage_level}kV",
                'peak_price': f"¥{gp.peak_price}/kWh",
                'normal_price': f"¥{gp.normal_price}/kWh",
                'valley_price': f"¥{gp.valley_price}/kWh",
                'capacity_price': f"¥{gp.capacity_price}/kVA·month",
                'created_at': gp.created_at.strftime('%Y-%m-%d') if gp.created_at else None
            })
        print_table_data("Grid electricity price table (GridElectricityPrice)", grid_data, max_width=18)
        
        # 5. Time-of-use period table
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
        print_table_data("Time-of-use period table (TimeOfUsePeriod)", tou_data, max_width=18)
        
        # Statistics
        print("\n")
        print("=" * 100)
        print("  Statistics")
        print("=" * 100)
        print(f"  User table record count:                 {len(users)}")
        print(f"  Factory table record count:              {len(factories)}")
        print(f"  HourlyElectricityPrice table record count: {len(hourly_prices)}")
        print(f"  GridElectricityPrice table record count:   {len(grid_prices)}")
        print(f"  TimeOfUsePeriod table record count:        {len(tou_periods)}")
        print("=" * 100)
        print(f"  Total: {len(users) + len(factories) + len(hourly_prices) + len(grid_prices) + len(tou_periods)} records")
        print("=" * 100)


if __name__ == '__main__':
    main()