# blogapp/models.py
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from blogapp import db


class User(UserMixin, db.Model):
    """User model for PeakShift system"""
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    user_type = db.Column(db.String(20), default='user')  # user, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_admin(self):
        """Check if user is admin"""
        return self.user_type == 'admin'
    
    def __repr__(self):
        return f'<User {self.username}>'


class Factory(db.Model):
    """工厂模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    industry_type = db.Column(db.String(50))  # 行业类型
    monthly_usage = db.Column(db.Float, default=0)  # 月用电量 (kWh)
    monthly_cost = db.Column(db.Float, default=0)  # 月电费 (元)
    carbon_emission = db.Column(db.Float, default=0)  # 碳排放量 (kg)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Factory {self.name}>'


class HourlyElectricityPrice(db.Model):
    """分时电价表 - 存储每小时的电价"""
    __tablename__ = 'hourly_electricity_price'
    
    id = db.Column(db.Integer, primary_key=True)
    hour = db.Column(db.Integer, nullable=False)  # 小时 (0-23)
    time_range = db.Column(db.String(20), nullable=False)  # 时间段 (如 "0-1", "1-2")
    price = db.Column(db.Float, nullable=False)  # 电价 (元/kWh)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def actual_price(self):
        """实际支付电价（含代理费 0.01 元/kWh）"""
        return round(self.price + 0.01, 2)
    
    def __repr__(self):
        return f'<HourlyPrice {self.time_range} Price:{self.price}>'


class GridElectricityPrice(db.Model):
    """电网售卖价格表 - 不同电压等级的分时电价和容量电价"""
    __tablename__ = 'grid_electricity_price'
    
    id = db.Column(db.Integer, primary_key=True)
    voltage_level = db.Column(db.Integer, nullable=False, unique=True)  # 电压等级 (10, 35, 110, 220)
    peak_price = db.Column(db.Float, nullable=False)  # 高峰电价 (元/kWh)
    normal_price = db.Column(db.Float, nullable=False)  # 平时电价 (元/kWh)
    valley_price = db.Column(db.Float, nullable=False)  # 低谷电价 (元/kWh)
    capacity_price = db.Column(db.Float, nullable=False)  # 容量电价 (元/kVA·月)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<GridPrice {self.voltage_level}kV>'


class TimeOfUsePeriod(db.Model):
    """分时电价时段表 - 定义每小时属于高峰/平时/低谷"""
    __tablename__ = 'time_of_use_period'
    
    id = db.Column(db.Integer, primary_key=True)
    hour = db.Column(db.Integer, nullable=False, unique=True)  # 小时 (0-23)
    time_range = db.Column(db.String(20), nullable=False)  # 时间段 (如 "0-1", "1-2")
    period_type = db.Column(db.String(10), nullable=False)  # 时段类型: 高峰/平时/低谷
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TOU {self.time_range} {self.period_type}>'

# class PowerSource(db.Model):
#     """电力来源配置"""
#     id = db.Column(db.Integer, primary_key=True)
#     factory_id = db.Column(db.Integer, db.ForeignKey('factory.id'), nullable=False)
#     source_type = db.Column(db.String(50))  # 火电、风电、太阳能等
#     percentage = db.Column(db.Float)  # 占比
#     carbon_factor = db.Column(db.Float)  # 碳排放因子 gCO₂/kWh

# class ElectricityUsage(db.Model):
#     """用电记录"""
#     id = db.Column(db.Integer, primary_key=True)
#     factory_id = db.Column(db.Integer, db.ForeignKey('factory.id'), nullable=False)
#     date = db.Column(db.Date, nullable=False)
#     usage_kwh = db.Column(db.Float, nullable=False)  # 用电量
#     cost = db.Column(db.Float)  # 电费
#     carbon_emission = db.Column(db.Float)  # 碳排放量
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

# class ElectricityPrice(db.Model):
#     """分时电价"""
#     id = db.Column(db.Integer, primary_key=True)
#     time_period = db.Column(db.String(20))  # 峰、平、谷
#     start_hour = db.Column(db.Integer)
#     end_hour = db.Column(db.Integer)
#     price_per_kwh = db.Column(db.Float)  # 元/kWh
#     region = db.Column(db.String(50))
