#!/usr/bin/env python3
"""
创建管理员账号脚本
用于创建或更新管理员账号（密码使用哈希加密）
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from microblog import app
from blogapp import db
from blogapp.models import User
import sys


def create_admin(username, email, password):
    """创建或更新管理员账号"""
    with app.app_context():
        # Check if user already exists (username is encrypted, need to check all users)
        existing_user = None
        for user in User.query.all():
            if user.username == username:
                existing_user = user
                break
        
        if existing_user:
            print(f"⚠️  用户 '{username}' 已存在")
            response = input("是否更新密码？(y/n): ").strip().lower()
            
            if response == 'y':
                existing_user.set_password(password)
                existing_user.user_type = 'admin'
                existing_user.email = email
                db.session.commit()
                print(f"✅ 管理员账号 '{username}' 密码已更新")
            else:
                print("❌ 操作已取消")
            return
        
        # 创建新管理员
        admin = User(
            username=username,
            email=email,
            user_type='admin'
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"✅ 管理员账号创建成功！")
        print(f"   用户名: {username}")
        print(f"   邮箱: {email}")
        print(f"   类型: 管理员")


def main():
    """主函数"""
    print("=" * 50)
    print("PeakShift 管理员账号创建工具")
    print("=" * 50)
    print()
    
    # 获取用户输入
    username = input("请输入管理员用户名: ").strip()
    if not username:
        print("❌ 用户名不能为空")
        sys.exit(1)
    
    email = input("请输入管理员邮箱: ").strip()
    if not email:
        print("❌ 邮箱不能为空")
        sys.exit(1)
    
    password = input("请输入管理员密码: ").strip()
    if not password:
        print("❌ 密码不能为空")
        sys.exit(1)
    
    confirm_password = input("请再次输入密码: ").strip()
    if password != confirm_password:
        print("❌ 两次输入的密码不一致")
        sys.exit(1)
    
    print()
    print("=" * 50)
    print("确认信息:")
    print(f"  用户名: {username}")
    print(f"  邮箱: {email}")
    print(f"  密码: {'*' * len(password)}")
    print("=" * 50)
    
    confirm = input("确认创建？(y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ 操作已取消")
        sys.exit(0)
    
    # 创建管理员
    create_admin(username, email, password)


if __name__ == '__main__':
    main()
