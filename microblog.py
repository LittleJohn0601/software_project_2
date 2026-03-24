# microblog.py
# flask app is set in this file

from blogapp import create_app, db
import os

app = create_app()

# 自动初始化数据库（如果不存在）
with app.app_context():
    db_path = os.path.join(app.instance_path, 'greenlife.db')
    if not os.path.exists(db_path):
        print("📦 Database not found, initializing...")
        db.create_all()
        print("✅ Database initialized successfully!")
    else:
        print("✅ Database already exists")

if __name__ == '__main__':
    # 使用 0.0.0.0 允许外部访问（Docker 需要）
    app.run(debug=True, host='0.0.0.0', port=5001)