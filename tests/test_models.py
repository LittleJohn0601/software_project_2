
import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

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