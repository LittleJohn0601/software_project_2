# test_imports.py
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

print("="*60)
print("Test module imports")
print("="*60)

# Check Python path
print(f"\nCurrent working directory: {os.getcwd()}")
print(f"First 3 Python paths: {sys.path[:3]}")

# Test 1: Import blogapp
print("\n1. Test importing blogapp...")
try:
    import blogapp
    print(f"   ✅ blogapp Import successful, location: {blogapp.__file__}")
except Exception as e:
    print(f"   ❌ blogapp Import failed: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Import blogapp.models
print("\n2. Test importing blogapp.models...")
try:
    from blogapp import models
    print(f"   ✅ blogapp.models imported successfully")
except Exception as e:
    print(f"   ❌ blogapp.models Import failed: {e}")

# Test 3: Import blogapp.routes
print("\n3. Test importing blogapp.routes...")
try:
    from blogapp import routes
    print(f"   ✅ blogapp.routes imported successfully")
except Exception as e:
    print(f"   ❌ blogapp.routes Import failed: {e}")

# Test 4: Import auth module
print("\n4. Test importing blogapp.routes.auth...")
try:
    from blogapp.routes import auth
    print(f"   ✅ blogapp.routes.auth imported successfully")
except Exception as e:
    print(f"   ❌ blogapp.routes.auth Import failed: {e}")

# Test 5: Import main module
print("\n5. Test importing blogapp.routes.main...")
try:
    from blogapp.routes import main
    print(f"   ✅ blogapp.routes.main imported successfully")
except Exception as e:
    print(f"   ❌ blogapp.routes.main Import failed: {e}")

# Test 6: Import public module
print("\n6. Test importing blogapp.routes.public...")
try:
    from blogapp.routes import public
    print(f"   ✅ blogapp.routes.public imported successfully")
except Exception as e:
    print(f"   ❌ blogapp.routes.public Import failed: {e}")

# Test 7: Import visualization module
print("\n7. Test importing blogapp.routes.visualization...")
try:
    from blogapp.routes import visualization
    print(f"   ✅ blogapp.routes.visualization imported successfully")
except Exception as e:
    print(f"   ❌ blogapp.routes.visualization Import failed: {e}")

# Test 8: Create application
print("\n8. Test creating application...")
try:
    from blogapp import create_app
    app = create_app()
    print(f"   ✅ Application created successfully")
except Exception as e:
    print(f"   ❌ Application creation failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)