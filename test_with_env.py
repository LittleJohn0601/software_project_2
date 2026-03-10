# test_with_env.py
"""
Test script for using .env file
"""

import os
import sys

print("🔧 Testing configuration with .env file")
print("=" * 50)

# Check for .env file
if not os.path.exists('.env'):
    print("❌ .env file not found")
    print("Please run first: Rename-Item .env.test .env")
    sys.exit(1)

# Load .env file
from dotenv import load_dotenv
load_dotenv('.env')

print(f"✅ Loaded .env file successfully")
print(f"   Current environment: {os.environ.get('FLASK_ENV', 'Not set')}")
print(f"   Database: {os.environ.get('DATABASE_URL', 'Not set')}")
print(f"   Encryption key: {os.environ.get('ENCRYPTION_MASTER_KEY', 'Not set')[:20]}...")

# Test encryption functionality
try:
    from blogapp import create_app, db
    from blogapp.models import User
    
    app = create_app()
    
    with app.app_context():
        db.create_all()
        
        # Test user creation
        user = User(
            username="env_test_user",
            email="env.test@example.com"
        )
        user.set_password("test123")
        
        db.session.add(user)
        db.session.commit()
        
        print(f"\n✅ Successfully created user with .env configuration")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Encrypted storage: {user._email_encrypted[:30]}...")
        
        # Clean up
        db.session.delete(user)
        db.session.commit()
        
        print(f"\n✅ Test completed, configuration works properly")
        
except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()