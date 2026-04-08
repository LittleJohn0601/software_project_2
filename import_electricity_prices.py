#!/usr/bin/env python3
"""
Electricity price import script
Read time-of-use electricity price data from an Excel file and write it to the database
"""

import pandas as pd
import os
from microblog import app
from blogapp import db
from blogapp.models import HourlyElectricityPrice


def import_electricity_prices():
    """Import electricity price data"""
    
    # Excel file path
    excel_path = os.path.join('blogapp', 'data', 'hourly_avg_30days(1).xlsx')
    
    if not os.path.exists(excel_path):
        print(f"❌ File not found: {excel_path}")
        return
    
    print(f"📂 Reading file: {excel_path}")
    
    # Read Excel file
    df = pd.read_excel(excel_path)
    
    print(f"📊 Data shape: {df.shape}")
    print(f"📋 Column names: {df.columns.tolist()}")
    print(f"\nFirst 5 rows of data:")
    print(df.head())
    
    # Get column names (assuming first column is hour, second is price)
    hour_col = df.columns[0]
    price_col = df.columns[1]
    
    print(f"\n🔄 Starting data import...")
    print(f"   Hour column: {hour_col}")
    print(f"   Price column: {price_col}")
    
    with app.app_context():
        # Clearing existing data
        HourlyElectricityPrice.query.delete()
        print("🗑️  Old data cleared")
        
        # Importing new data
        imported_count = 0
        for index, row in df.iterrows():
            # Process time format (e.g. extract hour from "00:00")
            time_str = str(row[hour_col])
            if ':' in time_str:
                hour = int(time_str.split(':')[0])
            else:
                hour = int(time_str)
            
            # Generate time range string
            time_range = f"{hour:02d}:00-{(hour+1):02d}:00"
            
            original_price = float(row[price_col])
            
            # Divide price by 1000 and round to two decimals
            price = round(original_price / 1000, 2)
            
            # Create record - now includes time_range
            record = HourlyElectricityPrice(
                hour=hour,
                time_range=time_range,  # ← Add this field
                price=price
            )
            db.session.add(record)
            imported_count += 1
            
            print(f"   Hour {hour:2d}: {time_range} - {original_price:8.2f} → {price:.2f} CNY/kWh")
        
        # Commit to the database
        db.session.commit()
        print(f"\n✅ Successfully imported {imported_count} records！")
        
        # Verify data
        print("\n🔍 Verify data:")
        all_records = HourlyElectricityPrice.query.order_by(HourlyElectricityPrice.hour).all()
        print(f"   Total records in database: {len(all_records)} records")
        if all_records:
            print(f"   Hour range: {all_records[0].hour} - {all_records[-1].hour}")
            print(f"   Price range: {min(r.price for r in all_records):.2f} - {max(r.price for r in all_records):.2f} CNY/kWh")
            print(f"\n   First 5 records:")
            for r in all_records[:5]:
                print(f"     {r.time_range}: {r.price:.2f} CNY/kWh")


if __name__ == '__main__':
    print("=" * 60)
    print("Electricity Price Import Tool")
    print("=" * 60)
    import_electricity_prices()
    print("=" * 60)