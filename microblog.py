# microblog.py
# flask app is set in this file

from blogapp import create_app, db
from blogapp.models import HourlyElectricityPrice, GridElectricityPrice, TimeOfUsePeriod
import os
import pandas as pd

app = create_app()

# 自动初始化数据库（确保表结构存在）
with app.app_context():
    db_path = os.path.join(app.instance_path, 'greenlife.db')
    if not os.path.exists(db_path):
        print("📦 Database not found, creating...")
    else:
        print("📦 Database file exists, checking tables...")
    
    # 无论数据库文件是否存在，都执行 create_all()
    # create_all() 只会创建不存在的表，不会覆盖已有数据
    db.create_all()
    print("✅ Database initialized successfully!")
    
    # ========================================
    # 1. 导入代理公司电价数据
    # ========================================
    price_count = HourlyElectricityPrice.query.count()
    if price_count == 0:
        print("📊 Importing hourly electricity price data...")
        excel_path = os.path.join('blogapp', 'data', 'hourly_avg_30days(1).xlsx')
        
        if os.path.exists(excel_path):
            try:
                df = pd.read_excel(excel_path)
                hour_col = df.columns[0]
                price_col = df.columns[1]
                
                for index, row in df.iterrows():
                    # 处理时间格式（如 "00:00" 提取小时部分）
                    time_str = str(row[hour_col])
                    if ':' in time_str:
                        hour = int(time_str.split(':')[0])
                    else:
                        hour = int(time_str)
                    
                    # 生成时间段描述（如 "0-1", "1-2", "23-24"）
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
    # 2. 导入电网售卖价格数据
    # ========================================
    grid_price_count = GridElectricityPrice.query.count()
    if grid_price_count == 0:
        print("📊 Importing grid electricity price data...")
        excel_path = os.path.join('blogapp', 'data', '电网售卖价格.xlsx')
        
        if os.path.exists(excel_path):
            try:
                df = pd.read_excel(excel_path)
                # 跳过第一行（表头行）
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
    # 3. 导入分时电价时段数据
    # ========================================
    tou_count = TimeOfUsePeriod.query.count()
    if tou_count == 0:
        print("📊 Importing time-of-use period data...")
        excel_path = os.path.join('blogapp', 'data', '分时价格详情.xlsx')
        
        if os.path.exists(excel_path):
            try:
                df = pd.read_excel(excel_path)
                # 删除 NaN 行
                df = df.dropna()
                
                # 解析时间段并展开到每个小时
                for index, row in df.iterrows():
                    time_range = str(row['时间段'])
                    period_type = str(row['价格区间'])
                    
                    # 解析时间段（如 "0-7" 表示 0,1,2,3,4,5,6 点）
                    start, end = map(int, time_range.split('-'))
                    
                    # 为每个小时创建记录
                    for hour in range(start, end):
                        # 生成时间段描述
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
    # 使用 0.0.0.0 允许外部访问（Docker 需要）
    app.run(debug=True, host='0.0.0.0', port=5001)