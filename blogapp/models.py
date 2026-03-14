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
    company_name = db.Column(db.String(100))  # 企业名称
    user_type = db.Column(db.String(20), default='user')  # user, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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


# TODO: Add your PeakShift models here
# Example models for your industrial energy system:

# class Factory(db.Model):
#     """工厂模型"""
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     location = db.Column(db.String(200))
#     industry_type = db.Column(db.String(50))  # 行业类型
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
