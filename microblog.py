# microblog.py
# flask app is set in this file

from blogapp import create_app, db
import os

app = create_app()

# 自动初始化数据库（确保表结构存在）
with app.app_context():
    db_path = os.path.join(app.instance_path, 'greenlife.db')
    if not os.path.exists(db_path):
        print("📦 Database not found, creating...")
    else:
        print("📦 Database file exists, checking tables...")
    
    # 无论数据库文件是否存在，都执行 create_all()
    # create_all() 只会创建不存在的表，不会覆盖已有数据
    db.create_all()
    print("✅ Database initialized successfully!")

if __name__ == '__main__':
    # 使用 0.0.0.0 允许外部访问（Docker 需要）
    app.run(debug=True, host='0.0.0.0', port=5001)