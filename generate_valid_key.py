# generate_valid_key.py
"""
Generate valid Fernet key
"""

import base64
import secrets
from cryptography.fernet import Fernet

print("🔐 Generating valid encryption key")
print("=" * 50)

# Method 1: Directly generate Fernet key (simplest)
fernet_key = Fernet.generate_key()
key_str = fernet_key.decode()

print(f"✅ Generated Fernet key:")
print(f"ENCRYPTION_MASTER_KEY={key_str}")
print(f"Length: {len(key_str)} characters")

# Test key
try:
    cipher = Fernet(fernet_key)
    test_email = "test@example.com"
    encrypted = cipher.encrypt(test_email.encode())
    decrypted = cipher.decrypt(encrypted).decode()
    
    print(f"\n✅ Key test passed:")
    print(f"Test email: {test_email}")
    print(f"Encryption: ✓")
    print(f"Decryption: ✓")
    
    # Update .env.test file
    with open('.env.test', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace key
    import re
    if 'ENCRYPTION_MASTER_KEY=' in content:
        # Replace existing
        new_content = re.sub(
            r'ENCRYPTION_MASTER_KEY=.*',
            f'ENCRYPTION_MASTER_KEY={key_str}',
            content
        )
    else:
        # Add new
        new_content = content + f'\nENCRYPTION_MASTER_KEY={key_str}'
    
    with open('.env.test', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"\n✅ Updated .env.test file")
    
except Exception as e:
    print(f"❌ Key test failed: {e}")

print("\n📋 Usage instructions:")
print(f"1. New key has been saved to .env.test")
print(f"2. Rerun tests: python test_email_encryption.py")