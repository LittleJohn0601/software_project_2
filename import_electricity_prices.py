#!/usr/bin/env python3
"""
导入电价数据脚本
从 Excel 文件读取分时电价数据并写入数据库
"""

import pandas as pd
import os
from microblog import app
from blogapp import db
from blogapp.models import HourlyElectricityPrice


def import_electricity_prices():
    """导入电价数据"""
    
    # Excel 文件路径
    excel_path = os.path.join('blogapp', 'data', 'hourly_avg_30days(1).xlsx')
    
    if not os.path.exists(excel_path):
        print(f"❌ 文件不存在: {excel_path}")
        return
    
    print(f"📂 读取文件: {excel_path}")
    
    # 读取 Excel 文件
    df = pd.read_excel(excel_path)
    
    print(f"📊 数据形状: {df.shape}")
    print(f"📋 列名: {df.columns.tolist()}")
    print(f"\n前5行数据:")
    print(df.head())
    
    # 获取列名（假设第一列是小时，第二列是价格）
    hour_col = df.columns[0]
    price_col = df.columns[1]
    
    print(f"\n🔄 开始导入数据...")
    print(f"   小时列: {hour_col}")
    print(f"   价格列: {price_col}")
    
    with app.app_context():
        # 清空现有数据
        HourlyElectricityPrice.query.delete()
        print("🗑️  已清空旧数据")
        
        # 导入新数据
        imported_count = 0
        for index, row in df.iterrows():
            # 处理时间格式（如 "00:00" 提取小时部分）
            time_str = str(row[hour_col])
            if ':' in time_str:
                hour = int(time_str.split(':')[0])
            else:
                hour = int(time_str)
            
            original_price = float(row[price_col])
            
            # 价格除以 1000，保留两位小数
            price = round(original_price / 1000, 2)
            
            # 创建记录
            record = HourlyElectricityPrice(
                hour=hour,
                price=price
            )
            db.session.add(record)
            imported_count += 1
            
            print(f"   Hour {hour:2d}: {original_price:8.2f} → {price:.2f} 元/kWh")
        
        # 提交到数据库
        db.session.commit()
        print(f"\n✅ 成功导入 {imported_count} 条记录！")
        
        # 验证数据
        print("\n🔍 验证数据:")
        all_records = HourlyElectricityPrice.query.order_by(HourlyElectricityPrice.hour).all()
        print(f"   数据库中共有 {len(all_records)} 条记录")
        print(f"   小时范围: {all_records[0].hour} - {all_records[-1].hour}")
        print(f"   价格范围: {min(r.price for r in all_records):.2f} - {max(r.price for r in all_records):.2f} 元/kWh")


if __name__ == '__main__':
    print("=" * 60)
    print("电价数据导入工具")
    print("=" * 60)
    import_electricity_prices()
    print("=" * 60)
