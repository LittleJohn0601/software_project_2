# blogapp/routes/public.py
"""
Public routes (no login required)
公共路由
"""

from flask import Blueprint, redirect, url_for

# 创建蓝图
bp = Blueprint("public", __name__)


@bp.get("/")
def index():
    """首页 - 重定向到统一认证页面"""
    return redirect(url_for("auth.auth_page"))
