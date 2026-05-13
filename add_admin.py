from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash
import sqlite3
import os
from datetime import datetime

# 使用你刚才生成的密钥
MASTER_KEY = "fLF14QAXfjdWfCVuQOWQdRZV7AJ7Et_LuUky-C8iznk="

# 初始化加密器
cipher = Fernet(MASTER_KEY.encode())

# 管理员信息
ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@example.com"  
ADMIN_PASSWORD = "admin123"

# 加密
encrypted_username = cipher.encrypt(ADMIN_USERNAME.encode()).decode()
encrypted_email = cipher.encrypt(ADMIN_EMAIL.encode()).decode()
password_hash = generate_password_hash(ADMIN_PASSWORD)

print("=" * 50)
print("📝 管理员加密数据：")
print("=" * 50)
print(f"加密后的用户名: {encrypted_username}")
print(f"加密后的邮箱: {encrypted_email}")
print(f"密码哈希: {password_hash}")
print("=" * 50)

# 连接数据库
db_path = "instance/greenlife.db"
if not os.path.exists(db_path):
    print(f"❌ 数据库文件不存在: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查是否已存在
cursor.execute("SELECT id FROM user WHERE username = ?", (encrypted_username,))
existing = cursor.fetchone()

if existing:
    print(f"⚠️  管理员账号已存在 (ID: {existing[0]})")
else:
    # 插入新管理员
    cursor.execute("""
        INSERT INTO user (username, email, password_hash, user_type, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        encrypted_username,
        encrypted_email,
        password_hash,
        'admin',
        datetime.now().isoformat()
    ))
    conn.commit()
    print("\n✅ 管理员账号创建成功！")
    print(f"   用户名: {ADMIN_USERNAME}")
    print(f"   密码: {ADMIN_PASSWORD}")

# 验证一下
cursor.execute("SELECT id, user_type FROM user WHERE username = ?", (encrypted_username,))
row = cursor.fetchone()
if row:
    print(f"\n📋 验证结果:")
    print(f"   ID: {row[0]}")
    print(f"   类型: {row[1]}")

conn.close()

# 提示更新 .env
print("\n" + "=" * 50)
print("⚠️  请确保 .env 文件包含以下配置：")
print(f"ENCRYPTION_MASTER_KEY={MASTER_KEY}")
print("=" * 50)