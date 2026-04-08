# blogapp/models.py
# Define database models: users, factories, time-of-use prices, grid prices, etc., including basic algorithms and property calculation logic such as monthly usage and carbon emissions!

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
    """Factory model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    industry_type = db.Column(db.String(50))  # Industry type
    voltage_level = db.Column(db.Integer, nullable=False)  # Voltage level (kV): 10, 35, 110, 220
    transformer_capacity = db.Column(db.Float, nullable=False)  # Transformer capacity (kVA)
    daily_usage = db.Column(db.Float, nullable=False)  # Daily usage (kWh/day)
    work_periods = db.Column(db.Text, nullable=False)  # Work periods JSON format: [{"start": 8, "end": 12}, {"start": 13, "end": 18}]
    working_days_per_month = db.Column(db.Integer, default=26)  # Working days per month
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def capacity_fee(self):
        """Calculate capacity fee (base fee) = capacity price * transformer capacity"""
        grid_price = GridElectricityPrice.query.filter_by(voltage_level=self.voltage_level).first()
        if grid_price:
            return round(grid_price.capacity_price * self.transformer_capacity, 2)
        return 0
    
    @property
    def monthly_usage(self):
        """Calculate monthly usage = daily usage * working days per month"""
        return round(self.daily_usage * self.working_days_per_month, 2)
    
    @property
    def carbon_emission(self):
        """Calculate monthly carbon emissions = monthly usage * carbon emission factor (0.6634 kgCO2/kWh)"""
        return round(self.monthly_usage * 0.6634, 2)
    
    def __repr__(self):
        return f'<Factory {self.name}>'


class HourlyElectricityPrice(db.Model):
    """Hourly electricity price table - stores per-hour electricity prices"""
    __tablename__ = 'hourly_electricity_price'
    
    id = db.Column(db.Integer, primary_key=True)
    hour = db.Column(db.Integer, nullable=False)  # Hour (0-23)
    time_range = db.Column(db.String(20), nullable=False)  # Time range (e.g. "0-1", "1-2")
    price = db.Column(db.Float, nullable=False)  # Price (CNY/kWh)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def actual_price(self):
        """Actual paid electricity price (including agent fee 0.01 CNY/kWh)"""
        return round(self.price + 0.01, 2)
    
    def __repr__(self):
        return f'<HourlyPrice {self.time_range} Price:{self.price}>'


class GridElectricityPrice(db.Model):
    """Grid sale price table - time-of-use and capacity prices by voltage level"""
    __tablename__ = 'grid_electricity_price'
    
    id = db.Column(db.Integer, primary_key=True)
    voltage_level = db.Column(db.Integer, nullable=False, unique=True)  # Voltage level (10, 35, 110, 220)
    peak_price = db.Column(db.Float, nullable=False)  # Peak electricity price (CNY/kWh)
    normal_price = db.Column(db.Float, nullable=False)  # Normal electricity price (CNY/kWh)
    valley_price = db.Column(db.Float, nullable=False)  # Valley electricity price (CNY/kWh)
    capacity_price = db.Column(db.Float, nullable=False)  # Capacity price (CNY/kVA·month)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<GridPrice {self.voltage_level}kV>'


class TimeOfUsePeriod(db.Model):
    """Time-of-use period table - defines each hour as peak/normal/valley"""
    __tablename__ = 'time_of_use_period'
    
    id = db.Column(db.Integer, primary_key=True)
    hour = db.Column(db.Integer, nullable=False, unique=True)  # Hour (0-23)
    time_range = db.Column(db.String(20), nullable=False)  # Time range (e.g. "0-1", "1-2")
    period_type = db.Column(db.String(10), nullable=False)  # Period type: peak/normal/valley
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TOU {self.time_range} {self.period_type}>'

# class PowerSource(db.Model):
#     """Power source configuration"""
#     id = db.Column(db.Integer, primary_key=True)
#     factory_id = db.Column(db.Integer, db.ForeignKey('factory.id'), nullable=False)
#     source_type = db.Column(db.String(50))  # coal, wind, solar, etc.
#     percentage = db.Column(db.Float)  # share percentage
#     carbon_factor = db.Column(db.Float)  # carbon emission factor gCO₂/kWh

# class ElectricityUsage(db.Model):
#     """Electricity usage record"""
#     id = db.Column(db.Integer, primary_key=True)
#     factory_id = db.Column(db.Integer, db.ForeignKey('factory.id'), nullable=False)
#     date = db.Column(db.Date, nullable=False)
#     usage_kwh = db.Column(db.Float, nullable=False)  # electricity usage
#     cost = db.Column(db.Float)  # electricity cost
#     carbon_emission = db.Column(db.Float)  # carbon emissions
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

# class ElectricityPrice(db.Model):
#     """Time-of-use electricity price"""
#     id = db.Column(db.Integer, primary_key=True)
#     time_period = db.Column(db.String(20))  # peak, normal, valley
#     start_hour = db.Column(db.Integer)
#     end_hour = db.Column(db.Integer)
#     price_per_kwh = db.Column(db.Float)  # CNY/kWh
#     region = db.Column(db.String(50))
