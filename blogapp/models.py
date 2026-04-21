# blogapp/models.py
# Define database models: users, factories, time-of-use prices, grid prices, etc., including basic algorithms and property calculation logic such as monthly usage and carbon emissions!

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from blogapp import db
from blogapp.utils.encryption import encrypt_field, decrypt_field

# Carbon emission factors
DEFAULT_GRID_CARBON_FACTOR = 0.6634  # kg CO₂/kWh
PHOTOVOLTAIC_CARBON_FACTOR = 0.0520  # kg CO₂/kWh


class User(UserMixin, db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    _username = db.Column('username', db.String(500), unique=True, nullable=False)
    _email = db.Column('email', db.String(500), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    user_type = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def username(self):
        if not self._username:
            return self._username
        try:
            return decrypt_field(self._username)
        except:
            return self._username
    
    @username.setter
    def username(self, value):
        if value:
            self._username = encrypt_field(value)
        else:
            self._username = value
    
    @property
    def email(self):
        if not self._email:
            return self._email
        try:
            return decrypt_field(self._email)
        except:
            return self._email
    
    @email.setter
    def email(self, value):
        if value:
            self._email = encrypt_field(value)
        else:
            self._email = value
    
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
    """Factory model with encrypted sensitive fields"""
    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column('name', db.String(500), nullable=False)  # Encrypted field
    _location = db.Column('location', db.String(500))  # Encrypted field
    _industry_type = db.Column('industry_type', db.String(500))  # Encrypted field
    voltage_level = db.Column(db.Integer, nullable=False)  # Voltage level (kV): 10, 35, 110, 220
    transformer_capacity = db.Column(db.Float, nullable=False)  # Transformer capacity (kVA)
    daily_usage = db.Column(db.Float, nullable=False)  # Daily usage (kWh/day)
    work_periods = db.Column(db.Text, nullable=False)  # Work periods JSON format: [{"start": 8, "end": 12}, {"start": 13, "end": 18}]
    working_days_per_month = db.Column(db.Integer, default=26)  # Working days per month
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def name(self):
        """Decrypt name when reading"""
        if not self._name:
            return self._name
        try:
            return decrypt_field(self._name)
        except:
            return self._name  # Return as-is if decryption fails (legacy data)
    
    @name.setter
    def name(self, value):
        """Encrypt name when writing"""
        if value:
            self._name = encrypt_field(value)
        else:
            self._name = value
    
    @property
    def location(self):
        """Decrypt location when reading"""
        if not self._location:
            return self._location
        try:
            return decrypt_field(self._location)
        except:
            return self._location  # Return as-is if decryption fails (legacy data)
    
    @location.setter
    def location(self, value):
        """Encrypt location when writing"""
        if value:
            self._location = encrypt_field(value)
        else:
            self._location = value
    
    @property
    def industry_type(self):
        """Decrypt industry_type when reading"""
        if not self._industry_type:
            return self._industry_type
        try:
            return decrypt_field(self._industry_type)
        except:
            return self._industry_type  # Return as-is if decryption fails (legacy data)
    
    @industry_type.setter
    def industry_type(self, value):
        """Encrypt industry_type when writing"""
        if value:
            self._industry_type = encrypt_field(value)
        else:
            self._industry_type = value
    
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
    def grid_carbon_factor(self):
        """Grid electricity carbon emission factor (kg CO₂/kWh)"""
        return DEFAULT_GRID_CARBON_FACTOR

    @property
    def pv_carbon_factor(self):
        """Photovoltaic electricity carbon emission factor (kg CO₂/kWh)"""
        return PHOTOVOLTAIC_CARBON_FACTOR

    @property
    def carbon_emission(self):
        """Calculate monthly carbon emissions using grid electricity factor"""
        return round(self.monthly_usage * self.grid_carbon_factor, 2)

    @property
    def pv_carbon_emission(self):
        """Calculate monthly carbon emissions if all electricity came from photovoltaic power"""
        return round(self.monthly_usage * self.pv_carbon_factor, 2)

    @property
    def pv_carbon_savings(self):
        """Calculate monthly carbon savings from switching all electricity to photovoltaic power"""
        return round(self.carbon_emission - self.pv_carbon_emission, 2)

    @property
    def pv_carbon_savings_percentage(self):
        """Calculate the percentage reduction in carbon emissions from full PV conversion"""
        if self.carbon_emission == 0:
            return 0.0
        return round(self.pv_carbon_savings / self.carbon_emission * 100, 2)
    
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
