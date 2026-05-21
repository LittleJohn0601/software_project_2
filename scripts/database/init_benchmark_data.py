#!/usr/bin/env python3
"""
初始化行业能效基准数据
运行: python scripts/database/init_benchmark_data.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from blogapp import create_app, db
from blogapp.models import IndustryBenchmark

# 行业基准数据
BENCHMARK_DATA = [
    {
        'industry_type': 'Aluminum Smelting',
        'avg_intensity': 13500,
        'excellent_intensity': 11000,
        'poor_intensity': 16000,
        'output_per_kwh': 8.5,
    },
    {
        'industry_type': 'Steel',
        'avg_intensity': 4500,
        'excellent_intensity': 3800,
        'poor_intensity': 5200,
        'output_per_kwh': 12.0,
    },
    {
        'industry_type': 'Cement',
        'avg_intensity': 3200,
        'excellent_intensity': 2600,
        'poor_intensity': 3800,
        'output_per_kwh': 9.0,
    },
    {
        'industry_type': 'Chemical',
        'avg_intensity': 1800,
        'excellent_intensity': 1400,
        'poor_intensity': 2200,
        'output_per_kwh': 15.0,
    },
    {
        'industry_type': 'Coal Refining',
        'avg_intensity': 2200,
        'excellent_intensity': 1700,
        'poor_intensity': 2700,
        'output_per_kwh': 11.0,
    },
    {
        'industry_type': 'Textile',
        'avg_intensity': 800,
        'excellent_intensity': 600,
        'poor_intensity': 1000,
        'output_per_kwh': 18.0,
    },
    {
        'industry_type': 'Other',
        'avg_intensity': 1500,
        'excellent_intensity': 1000,
        'poor_intensity': 2000,
        'output_per_kwh': 14.0,
    },
]

def init_benchmark_data():
    """初始化行业基准数据"""
    app = create_app()
    with app.app_context():
        # 检查是否已有数据
        existing = IndustryBenchmark.query.first()
        if existing:
            print("⚠️  数据库已有行业基准数据，跳过初始化")
            print("   如需重新初始化，请先清空 industry_benchmark 表")
            return
        
        # 插入数据
        for data in BENCHMARK_DATA:
            benchmark = IndustryBenchmark(**data)
            db.session.add(benchmark)
        
        db.session.commit()
        print(f"✅ 成功插入 {len(BENCHMARK_DATA)} 条行业基准数据")
        
        # 打印数据
        print("\n📊 行业基准数据列表:")
        print("-" * 60)
        for b in IndustryBenchmark.query.all():
            print(f"  {b.industry_type}: average={b.avg_intensity}, excellent={b.excellent_intensity}, poor={b.poor_intensity}, output={b.output_per_kwh} yuan/kWh")

if __name__ == '__main__':
    init_benchmark_data()