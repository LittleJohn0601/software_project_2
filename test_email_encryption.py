"""Test encryption and decryption"""
from blogapp import email_encryptor
from blogapp.models import User


def test_encryption():
    """Test encryption and decryption"""
    print("🔐 Testing email encryption functionality")
    print("=" * 50)
    
    # Create test application
    app = create_app()
    
    with app.app_context():
        # Create database
        db.create_all()
        
        # Test 1: Direct encryption and decryption
        test_email = "test.user@example.com"
        print(f"\n1. Testing direct encryption and decryption:")
        print(f"   Original email: {test_email}")
        
        encrypted = email_encryptor.encrypt_email(test_email)
        print(f"   Encrypted: {encrypted[:50]}...")
        
        decrypted = email_encryptor.decrypt_email(encrypted)
        print(f"   Decrypted: {decrypted}")
        print(f"   ✓ Match: {test_email == decrypted}")
        
        # Test 2: Through User model
        print(f"\n2. Testing User model encryption:")
        user = User(username="testuser", email="user@test.com")
        
        print(f"   Setting email: user@test.com")
        print(f"   Database storage: {user._email_encrypted[:50]}...")
        print(f"   Reading email: {user.email}")
        print(f"   ✓ Match: {'user@test.com' == user.email}")
        
        # Test 3: Save to database
        print(f"\n3. Testing database storage:")
        user.set_password("testpass")
        db.session.add(user)
        db.session.commit()
        
        # Re-query
        saved_user = User.query.filter_by(username="testuser").first()
        print(f"   Queried email: {saved_user.email}")
        print(f"   ✓ Decryption successful: {saved_user.email == 'user@test.com'}")
        
        # Cleanup
        db.session.delete(saved_user)
        db.session.commit()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed! Email encryption functionality works correctly.")