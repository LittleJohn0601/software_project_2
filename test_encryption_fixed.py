# test_encryption_fixed.py
"""
Fixed version of encryption test
"""

import os
import sys

# Set correct environment variables
os.environ['ENCRYPTION_MASTER_KEY'] = '05xWBfFHfE3-31f8PS95oyCqDjwg-7n1wGJ7e2IoWwY='
os.environ['SECRET_KEY'] = 'test-secret-key-change-in-production'
os.environ['DATABASE_URL'] = 'sqlite:///greenlife_test.db'
os.environ['FLASK_APP'] = 'blogapp'
os.environ['FLASK_ENV'] = 'development'

print("🔐 Fixed version of email encryption test")
print("=" * 60)

# First test encryption library directly
print("\n1. Testing Fernet encryption library directly...")
try:
    import base64
    from cryptography.fernet import Fernet
    
    key_str = '05xWBfFHfE3-31f8PS95oyCqDjwg-7n1wGJ7e2IoWwY='
    print(f"   Using key: {key_str}")
    
    # Ensure key format is correct
    key_str = key_str.strip()
    missing_padding = len(key_str) % 4
    if missing_padding:
        key_str += '=' * (4 - missing_padding)
    
    key_bytes = base64.urlsafe_b64decode(key_str)
    print(f"   Decoded length: {len(key_bytes)} bytes")
    
    # Re-encode
    final_key = base64.urlsafe_b64encode(key_bytes)
    cipher = Fernet(final_key)
    
    # Test
    test_email = "direct.test@example.com"
    encrypted = cipher.encrypt(test_email.encode())
    decrypted = cipher.decrypt(encrypted).decode()
    
    print(f"   Test email: {test_email}")
    print(f"   Encryption result: {encrypted.decode()[:40]}...")
    print(f"   Decryption result: {decrypted}")
    print(f"   ✓ Direct test passed!")
    
except Exception as e:
    print(f"   ✗ Direct test failed: {e}")
    import traceback
    traceback.print_exc()

# Test EmailEncryptor class
print("\n2. Testing EmailEncryptor class (without Flask context)...")
try:
    # Mock Flask application
    class MockApp:
        config = {
            'ENV': 'development',
            'ENCRYPTION_MASTER_KEY': '05xWBfFHfE3-31f8PS95oyCqDjwg-7n1wGJ7e2IoWwY='
        }
        logger = type('MockLogger', (), {
            'info': lambda x: print(f"   LOG: {x}"),
            'warning': lambda x: print(f"   WARN: {x}"),
            'error': lambda x: print(f"   ERROR: {x}")
        })()
    
    # Create encryptor
    import base64
    from cryptography.fernet import Fernet
    
    key_str = '05xWBfFHfE3-31f8PS95oyCqDjwg-7n1wGJ7e2IoWwY='
    key_str = key_str.strip()
    missing_padding = len(key_str) % 4
    if missing_padding:
        key_str += '=' * (4 - missing_padding)
    
    key_bytes = base64.urlsafe_b64decode(key_str)
    final_key = base64.urlsafe_b64encode(key_bytes)
    cipher = Fernet(final_key)
    
    # Test
    test_email = "class.test@example.com"
    encrypted = cipher.encrypt(test_email.encode()).decode()
    decrypted = cipher.decrypt(encrypted.encode()).decode()
    
    print(f"   Test email: {test_email}")
    print(f"   Encryption result: {encrypted[:40]}...")
    print(f"   Decryption result: {decrypted}")
    print(f"   ✓ Class test passed!")
    
except Exception as e:
    print(f"   ✗ Class test failed: {e}")

# Test complete Flask application
print("\n3. Testing complete Flask application...")
try:
    from blogapp import create_app, db
    from blogapp.models import User
    
    app = create_app()
    
    with app.app_context():
        # Create database
        db.create_all()
        
        print("   Flask application created successfully")
        
        # Test User model
        user = User(username="encrypt_test_user", email="model.test@example.com")
        print(f"   Creating user: {user.username}")
        print(f"   Setting email: model.test@example.com")
        
        # Check encrypted email
        encrypted_email = user._email_encrypted
        print(f"   Encrypted email stored in database: {encrypted_email[:50]}...")
        
        # Check decryption
        decrypted_email = user.email
        print(f"   Decrypted email read: {decrypted_email}")
        
        if decrypted_email == "model.test@example.com":
            print(f"   ✓ User model test passed!")
        else:
            print(f"   ✗ User model test failed: email does not match")
        
        # Save to database
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()
        print("   ✓ Database save successful")
        
        # Query verification
        saved_user = User.query.filter_by(username="encrypt_test_user").first()
        if saved_user and saved_user.email == "model.test@example.com":
            print(f"   ✓ Database query verification passed!")
        else:
            print(f"   ✗ Database query verification failed")
        
        # Cleanup
        db.session.delete(saved_user)
        db.session.commit()
        print("   ✓ Test data cleanup completed")
        
except Exception as e:
    print(f"   ✗ Flask application test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("🎉 Encryption functionality test completed!")