# microblog.py
# flask app is set in this file

from blogapp import create_app, db
from blogapp.models import HourlyElectricityPrice, GridElectricityPrice, TimeOfUsePeriod
import os
import pandas as pd

app = create_app()

# Automatically initialize the database (ensure table structure exists)
with app.app_context():
    db_path = os.path.join(app.instance_path, 'greenlife.db')
    db_exists = os.path.exists(db_path)
    
    if not db_exists:
        print("📦 Database not found, creating new database...")
    else:
        print("📦 Database file exists, checking tables...")
    
    # Even if the database file exists, execute create_all()
    # create_all() only creates missing tables and does not overwrite existing data
    db.create_all()
    print("✅ Database tables initialized!")
    
    # ========================================
    # 1. Import supplier electricity price data
    # ========================================
    try:
        price_count = HourlyElectricityPrice.query.count()
    except:
        # If the query fails, the table may be corrupted; set count to 0 to force re-import
        price_count = 0
    
    if price_count == 0:
        print("📊 Importing hourly electricity price data...")
        excel_path = os.path.join('data', 'excel', 'hourly_avg_30days(1).xlsx')
        
        if os.path.exists(excel_path):
            try:
                df = pd.read_excel(excel_path)
                hour_col = df.columns[0]
                price_col = df.columns[1]
                
                for index, row in df.iterrows():
                    # Process time format (e.g. extract hour from "00:00")
                    time_str = str(row[hour_col])
                    if ':' in time_str:
                        hour = int(time_str.split(':')[0])
                    else:
                        hour = int(time_str)
                    
                    # Generate time range description (e.g. "0-1", "1-2", "23-24")
                    next_hour = (hour + 1) % 24
                    if next_hour == 0:
                        time_range = f"{hour}-24"
                    else:
                        time_range = f"{hour}-{next_hour}"
                    
                    original_price = float(row[price_col])
                    price = round(original_price / 1000, 2)
                    
                    record = HourlyElectricityPrice(
                        hour=hour,
                        time_range=time_range,
                        price=price
                    )
                    db.session.add(record)
                
                db.session.commit()
                print(f"✅ Imported {len(df)} hourly price records!")
            except Exception as e:
                print(f"⚠️  Failed to import hourly prices: {e}")
                db.session.rollback()
        else:
            print(f"⚠️  Hourly price file not found: {excel_path}")
    else:
        print(f"✅ Hourly price data already exists ({price_count} records)")
    
    # ========================================
    # 2. Import grid electricity price data
    # ========================================
    try:
        grid_price_count = GridElectricityPrice.query.count()
    except:
        grid_price_count = 0
    
    if grid_price_count == 0:
        print("📊 Importing grid electricity price data...")
        excel_path = os.path.join('data', 'excel', '电网售卖价格.xlsx')
        
        if os.path.exists(excel_path):
            try:
                df = pd.read_excel(excel_path)
                # Skip the first row (header row with "高峰", "平时", "低谷")
                df = df.iloc[1:]
                
                for index, row in df.iterrows():
                    voltage_level = int(row['电压等级'])
                    peak_price = float(row['分时电价'])
                    normal_price = float(row['Unnamed: 2'])
                    valley_price = float(row['Unnamed: 3'])
                    capacity_price = float(row['容量电价'])
                    
                    record = GridElectricityPrice(
                        voltage_level=voltage_level,
                        peak_price=peak_price,
                        normal_price=normal_price,
                        valley_price=valley_price,
                        capacity_price=capacity_price
                    )
                    db.session.add(record)
                
                db.session.commit()
                print(f"✅ Imported {len(df)} grid price records!")
            except Exception as e:
                print(f"⚠️  Failed to import grid prices: {e}")
                db.session.rollback()
        else:
            print(f"⚠️  Grid price file not found: {excel_path}")
    else:
        print(f"✅ Grid price data already exists ({grid_price_count} records)")
    
    # ========================================
    # 3. Import time-of-use period data
    # ========================================
    try:
        tou_count = TimeOfUsePeriod.query.count()
    except:
        tou_count = 0
    
    if tou_count == 0:
        print("📊 Importing time-of-use period data...")
        excel_path = os.path.join('data', 'excel', '分时价格详情.xlsx')
        
        if os.path.exists(excel_path):
            try:
                df = pd.read_excel(excel_path)
                # Drop NaN rows
                df = df.dropna()
                
                # Parse time ranges and expand to every hour
                for index, row in df.iterrows():
                    time_range = str(row['时间段'])
                    period_type = str(row['价格区间'])
                    
                    # Parse time ranges (e.g. "0-7" means hours 0-6)
                    start, end = map(int, time_range.split('-'))
                    
                    # Create records for each hour
                    for hour in range(start, end):
                        # Generate time period description
                        next_hour = (hour + 1) % 24
                        if next_hour == 0:
                            time_range = f"{hour}-24"
                        else:
                            time_range = f"{hour}-{next_hour}"
                        
                        record = TimeOfUsePeriod(
                            hour=hour,
                            time_range=time_range,
                            period_type=period_type
                        )
                        db.session.add(record)
                
                db.session.commit()
                print(f"✅ Imported time-of-use period data (24 hours)!")
            except Exception as e:
                print(f"⚠️  Failed to import TOU periods: {e}")
                db.session.rollback()
        else:
            print(f"⚠️  TOU period file not found: {excel_path}")
    else:
        print(f"✅ TOU period data already exists ({tou_count} records)")

if __name__ == '__main__':
    # Use 0.0.0.0 to allow external access (required for Docker)
    app.run(debug=True, host='0.0.0.0', port=5001)