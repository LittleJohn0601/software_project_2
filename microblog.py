# microblog.py
# flask app is set in this file

from blogapp import create_app, db
from blogapp.models import HourlyElectricityPrice
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
    
    # 自动导入电价数据（如果表为空）
    price_count = HourlyElectricityPrice.query.count()
    if price_count == 0:
        print("📊 Importing electricity price data...")
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
                    
                    original_price = float(row[price_col])
                    price = round(original_price / 1000, 2)
                    
                    record = HourlyElectricityPrice(hour=hour, price=price)
                    db.session.add(record)
                
                db.session.commit()
                print(f"✅ Imported {len(df)} electricity price records!")
            except Exception as e:
                print(f"⚠️  Failed to import electricity prices: {e}")
                db.session.rollback()
        else:
            print(f"⚠️  Electricity price file not found: {excel_path}")
    else:
        print(f"✅ Electricity price data already exists ({price_count} records)")

if __name__ == '__main__':
    # 使用 0.0.0.0 允许外部访问（Docker 需要）
    app.run(debug=True, host='0.0.0.0', port=5001)