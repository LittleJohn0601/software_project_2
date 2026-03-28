# test_imports.py
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

print("="*60)
print("测试各个模块导入")
print("="*60)

# 检查 Python 路径
print(f"\n当前工作目录: {os.getcwd()}")
print(f"Python路径前3个: {sys.path[:3]}")

# 测试1: 导入 blogapp
print("\n1. 测试导入 blogapp...")
try:
    import blogapp
    print(f"   ✅ blogapp 导入成功，位置: {blogapp.__file__}")
except Exception as e:
    print(f"   ❌ blogapp 导入失败: {e}")
    import traceback
    traceback.print_exc()

# 测试2: 导入 blogapp.models
print("\n2. 测试导入 blogapp.models...")
try:
    from blogapp import models
    print(f"   ✅ blogapp.models 导入成功")
except Exception as e:
    print(f"   ❌ blogapp.models 导入失败: {e}")

# 测试3: 导入 blogapp.routes
print("\n3. 测试导入 blogapp.routes...")
try:
    from blogapp import routes
    print(f"   ✅ blogapp.routes 导入成功")
except Exception as e:
    print(f"   ❌ blogapp.routes 导入失败: {e}")

# 测试4: 导入 auth 模块
print("\n4. 测试导入 blogapp.routes.auth...")
try:
    from blogapp.routes import auth
    print(f"   ✅ blogapp.routes.auth 导入成功")
except Exception as e:
    print(f"   ❌ blogapp.routes.auth 导入失败: {e}")

# 测试5: 导入 main 模块
print("\n5. 测试导入 blogapp.routes.main...")
try:
    from blogapp.routes import main
    print(f"   ✅ blogapp.routes.main 导入成功")
except Exception as e:
    print(f"   ❌ blogapp.routes.main 导入失败: {e}")

# 测试6: 导入 public 模块
print("\n6. 测试导入 blogapp.routes.public...")
try:
    from blogapp.routes import public
    print(f"   ✅ blogapp.routes.public 导入成功")
except Exception as e:
    print(f"   ❌ blogapp.routes.public 导入失败: {e}")

# 测试7: 导入 visualization 模块
print("\n7. 测试导入 blogapp.routes.visualization...")
try:
    from blogapp.routes import visualization
    print(f"   ✅ blogapp.routes.visualization 导入成功")
except Exception as e:
    print(f"   ❌ blogapp.routes.visualization 导入失败: {e}")

# 测试8: 创建应用
print("\n8. 测试创建应用...")
try:
    from blogapp import create_app
    app = create_app()
    print(f"   ✅ 应用创建成功")
except Exception as e:
    print(f"   ❌ 应用创建失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)