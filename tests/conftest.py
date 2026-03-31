import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from blogapp import create_app, db


@pytest.fixture(scope='session')
def app():
    """创建测试用的应用实例，session级别复用"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False  # 禁用 CSRF 保护便于测试
    
    return app


@pytest.fixture(scope='session')
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """每个测试函数独立的数据库会话"""
    with app.app_context():
        db.create_all()
        yield db.session
        db.session.remove()
        db.drop_all()