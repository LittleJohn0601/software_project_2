#!/usr/bin/env python3
"""
电价数据自动同步工具
在应用启动时检查Excel文件，如果数据不同则自动更新数据库
"""

import pandas as pd
import os
import hashlib
from blogapp import db
from blogapp.models import HourlyElectricityPrice


def get_file_hash(filepath):
    """计算文件的MD5哈希值"""
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def get_db_data_hash():
    """计算数据库中电价数据的哈希值"""
    prices = HourlyElectricityPrice.query.order_by(HourlyElectricityPrice.hour).all()
    if not prices:
        return None
    
    # 将所有价格数据拼接成字符串（按小时排序）
    data_str = ''.join([f'{p.hour}:{p.price:.4f}' for p in prices])
    return hashlib.md5(data_str.encode()).hexdigest()


def get_excel_data_hash(excel_path):
    """计算Excel文件中电价数据的哈希值"""
    try:
        df = pd.read_excel(excel_path)
        # 按照导入逻辑处理数据
        data_parts = []
        for index, row in df.iterrows():
            hour_col = df.columns[0]
            price_col = df.columns[1]
            
            time_str = str(row[hour_col])
            if ':' in time_str:
                hour = int(time_str.split(':')[0])
            else:
                hour = int(time_str)
            
            # 价格除以1000并保留2位小数（与导入逻辑一致）
            original_price = float(row[price_col])
            price = round(original_price / 1000, 2)
            
            data_parts.append(f'{hour}:{price:.4f}')
        
        data_str = ''.join(data_parts)
        return hashlib.md5(data_str.encode()).hexdigest()
    except Exception:
        return None


def sync_electricity_prices(app, force=False):
    """
    同步电价数据
    
    Args:
        app: Flask应用实例
        force: 是否强制更新（忽略哈希检查）
    
    Returns:
        bool: 是否进行了更新
    """
    excel_path = os.path.join('data', 'excel', 'hourly_avg_30days(1).xlsx')
    
    if not os.path.exists(excel_path):
        app.logger.warning(f"电价数据文件不存在: {excel_path}")
        return False
    
    with app.app_context():
        # 检查是否需要更新
        if not force:
            excel_hash = get_excel_data_hash(excel_path)
            db_hash = get_db_data_hash()
            
            # 如果数据库为空，需要导入
            if db_hash is None:
                app.logger.info("数据库中没有电价数据，开始导入...")
            # 如果哈希相同，不需要更新
            elif excel_hash and db_hash and excel_hash == db_hash:
                app.logger.info("电价数据已是最新，无需更新")
                return False
            else:
                app.logger.info("检测到电价数据变化，开始更新...")
        
        # 读取Excel文件
        try:
            df = pd.read_excel(excel_path)
            app.logger.info(f"读取电价数据文件: {excel_path}")
        except Exception as e:
            app.logger.error(f"读取Excel文件失败: {e}")
            return False
        
        # 获取列名
        hour_col = df.columns[0]
        price_col = df.columns[1]
        
        # 清除旧数据
        HourlyElectricityPrice.query.delete()
        app.logger.info("清除旧的电价数据")
        
        # 导入新数据
        imported_count = 0
        for index, row in df.iterrows():
            # 处理时间格式
            time_str = str(row[hour_col])
            if ':' in time_str:
                hour = int(time_str.split(':')[0])
            else:
                hour = int(time_str)
            
            # 生成时间范围字符串
            time_range = f"{hour}-{hour+1}"
            
            # 价格除以1000并保留2位小数
            original_price = float(row[price_col])
            price = round(original_price / 1000, 2)
            
            # 创建记录
            record = HourlyElectricityPrice(
                hour=hour,
                time_range=time_range,
                price=price
            )
            db.session.add(record)
            imported_count += 1
        
        # 提交到数据库
        try:
            db.session.commit()
            app.logger.info(f"✅ 成功导入 {imported_count} 条电价记录")
            
            # 验证数据
            all_records = HourlyElectricityPrice.query.order_by(HourlyElectricityPrice.hour).all()
            if all_records:
                min_price = min(r.price for r in all_records)
                max_price = max(r.price for r in all_records)
                app.logger.info(f"价格范围: {min_price:.2f} - {max_price:.2f} 元/kWh")
            
            return True
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"导入电价数据失败: {e}")
            return False


def check_and_sync_on_startup(app):
    """
    应用启动时检查并同步电价数据
    
    Args:
        app: Flask应用实例
    """
    app.logger.info("=" * 60)
    app.logger.info("检查电价数据...")
    
    try:
        updated = sync_electricity_prices(app, force=False)
        if updated:
            app.logger.info("✅ 电价数据已更新")
        else:
            app.logger.info("✅ 电价数据检查完成")
    except Exception as e:
        app.logger.error(f"❌ 电价数据同步失败: {e}")
    
    app.logger.info("=" * 60)
