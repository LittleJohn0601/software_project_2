#!/bin/bash
# Docker 容器启动脚本

echo "🚀 Starting PeakShift application..."

# 检查数据库是否存在
if [ ! -f "/app/instance/greenlife.db" ]; then
    echo "📦 Database not found, initializing..."
    python init_db.py
    echo "✅ Database initialized successfully!"
else
    echo "✅ Database already exists"
fi

# 启动 Flask 应用
echo "🌐 Starting Flask server on port 5001..."
python microblog.py
