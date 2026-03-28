# 测试代码，在项目根目录运行：python -m pytest tests/test_models.py -v

# tests/test_models.py
import sys
import os

# 获取项目根目录（tests的父目录）
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

print(f"项目根目录: {project_root}")
print(f"Python路径: {sys.path[:3]}")



import pytest
from blogapp import create_app, db
from blogapp.models import Factory, User

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def test_factory_carbon_emission(app):
    with app.app_context():
        # 先创建用户
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        factory = Factory(
            name='Test Factory',
            voltage_level=10,
            transformer_capacity=1000,
            daily_usage=100.0,
            work_periods='[]',
            working_days_per_month=30,
            user_id=user.id
        )
        db.session.add(factory)
        db.session.commit()
        
        # 验证月用电量计算
        assert factory.monthly_usage == 3000.0
        
        # 验证碳排放计算
        expected_emission = round(3000.0 * 0.6634, 2)  # 1989.0
        assert factory.carbon_emission == expected_emission