#!/usr/bin/env python3
# test_encryption.py
# Test database encryption functionality

import sys
import os

# Add project root to Python path (go up two levels: security -> scripts -> project_root)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from blogapp import create_app, db
from blogapp.models import User, Factory
from blogapp.utils.encryption import EncryptionManager

def test_encryption_basic():
    """Test basic encryption/decryption"""
    print("=" * 60)
    print("🧪 Test 1: Basic Encryption/Decryption")
    print("=" * 60)
    
    app = create_app()
    with app.app_context():
        test_data = "test@example.com"
        print(f"Original data: {test_data}")
        
        # Encrypt
        encrypted = EncryptionManager.encrypt(test_data)
        print(f"Encrypted data: {encrypted[:50]}..." if len(encrypted) > 50 else f"Encrypted data: {encrypted}")
        
        # Decrypt
        decrypted = EncryptionManager.decrypt(encrypted)
        print(f"Decrypted data: {decrypted}")
        
        if decrypted == test_data:
            print("✅ Basic encryption test PASSED")
            return True
        else:
            print("❌ Basic encryption test FAILED")
            return False

def test_user_email_encryption():
    """Test User email and username encryption"""
    print("\n" + "=" * 60)
    print("🧪 Test 2: User Email & Username Encryption")
    print("=" * 60)
    
    app = create_app()
    with app.app_context():
        # Create test user
        test_email = "encryption_test@example.com"
        test_username = "encryption_test_user"
        test_user = User(username=test_username, email=test_email)
        test_user.set_password("test123")
        
        print(f"Original username: {test_username}")
        print(f"Encrypted username in DB: {test_user._username[:50]}..." if len(test_user._username) > 50 else f"Encrypted username in DB: {test_user._username}")
        print(f"Decrypted username (via property): {test_user.username}")
        
        print(f"\nOriginal email: {test_email}")
        print(f"Encrypted email in DB: {test_user._email[:50]}..." if len(test_user._email) > 50 else f"Encrypted email in DB: {test_user._email}")
        print(f"Decrypted email (via property): {test_user.email}")
        
        # Verify encryption
        username_encrypted = test_user.username == test_username and test_user._username != test_username
        email_encrypted = test_user.email == test_email and test_user._email != test_email
        
        if username_encrypted and email_encrypted:
            print("\n✅ User email & username encryption test PASSED")
            return True
        else:
            print("\n❌ User email & username encryption test FAILED")
            return False

def test_factory_location_encryption():
    """Test Factory name, location, and industry_type encryption"""
    print("\n" + "=" * 60)
    print("🧪 Test 3: Factory Sensitive Fields Encryption")
    print("=" * 60)
    
    app = create_app()
    with app.app_context():
        # Create test factory
        test_name = "Beijing Aluminum Electrolyzer Factory"
        test_location = "Beijing Chaoyang District, Test Street 123"
        test_industry = "Aluminum Smelting"
        
        test_factory = Factory(
            name=test_name,
            location=test_location,
            industry_type=test_industry,
            voltage_level=110,
            transformer_capacity=5000,
            daily_usage=50000,
            work_periods='[{"start": 8, "end": 18}]',
            user_id=1
        )
        
        print(f"Original name: {test_name}")
        print(f"Encrypted name in DB: {test_factory._name[:50]}..." if len(test_factory._name) > 50 else f"Encrypted name in DB: {test_factory._name}")
        print(f"Decrypted name (via property): {test_factory.name}")
        
        print(f"\nOriginal location: {test_location}")
        print(f"Encrypted location in DB: {test_factory._location[:50]}..." if len(test_factory._location) > 50 else f"Encrypted location in DB: {test_factory._location}")
        print(f"Decrypted location (via property): {test_factory.location}")
        
        print(f"\nOriginal industry: {test_industry}")
        print(f"Encrypted industry in DB: {test_factory._industry_type[:50]}..." if len(test_factory._industry_type) > 50 else f"Encrypted industry in DB: {test_factory._industry_type}")
        print(f"Decrypted industry (via property): {test_factory.industry_type}")
        
        # Verify encryption
        name_encrypted = test_factory.name == test_name and test_factory._name != test_name
        location_encrypted = test_factory.location == test_location and test_factory._location != test_location
        industry_encrypted = test_factory.industry_type == test_industry and test_factory._industry_type != test_industry
        
        if name_encrypted and location_encrypted and industry_encrypted:
            print("\n✅ Factory sensitive fields encryption test PASSED")
            return True
        else:
            print("\n❌ Factory sensitive fields encryption test FAILED")
            return False

def test_database_persistence():
    """Test encryption persistence in database"""
    print("\n" + "=" * 60)
    print("🧪 Test 4: Database Persistence")
    print("=" * 60)
    
    app = create_app()
    with app.app_context():
        db.create_all()
        # Create and save test user
        test_email = "persistence_test@example.com"
        test_username = "persistence_test_user"
        
        # Check if user already exists (username is encrypted, need to check all users)
        existing_user = None
        for u in User.query.all():
            if u.username == test_username:
                existing_user = u
                break
        
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()
        
        # Create new user
        user = User(username=test_username, email=test_email)
        user.set_password("test123")
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        
        print(f"Created user with ID: {user_id}")
        print(f"Email (plaintext): {test_email}")
        
        # Clear session
        db.session.expunge_all()
        
        # Retrieve user from database
        retrieved_user = User.query.get(user_id)
        print(f"Retrieved user email: {retrieved_user.email}")
        print(f"Encrypted email in DB: {retrieved_user._email[:50]}..." if len(retrieved_user._email) > 50 else f"Encrypted email in DB: {retrieved_user._email}")
        
        # Verify
        success = retrieved_user.email == test_email
        
        # Cleanup
        db.session.delete(retrieved_user)
        db.session.commit()
        
        if success:
            print("✅ Database persistence test PASSED")
            return True
        else:
            print("❌ Database persistence test FAILED")
            return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🔐 Database Encryption Test Suite")
    print("=" * 60)
    print()
    
    app = create_app()
    with app.app_context():
        # Check if encryption key is set
        if not app.config.get('ENCRYPTION_MASTER_KEY'):
            print("⚠️  WARNING: ENCRYPTION_MASTER_KEY not set!")
            print("   A fallback key will be generated for testing.")
            print("   For production, please set ENCRYPTION_MASTER_KEY in .env")
            print()
    
    results = []
    
    # Run tests
    try:
        results.append(("Basic Encryption", test_encryption_basic()))
        results.append(("User Email & Username Encryption", test_user_email_encryption()))
        results.append(("Factory Sensitive Fields Encryption", test_factory_location_encryption()))
        results.append(("Database Persistence", test_database_persistence()))
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("✅ All tests passed! Encryption is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the configuration.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
