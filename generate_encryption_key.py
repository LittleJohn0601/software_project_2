#!/usr/bin/env python3
# generate_encryption_key.py
# Generate a secure encryption key for database field encryption

from cryptography.fernet import Fernet

def generate_key():
    """Generate a new Fernet encryption key"""
    key = Fernet.generate_key()
    return key.decode()

if __name__ == '__main__':
    print("=" * 60)
    print("🔐 Database Encryption Key Generator")
    print("=" * 60)
    print()
    print("Generated encryption key:")
    print()
    key = generate_key()
    print(f"  {key}")
    print()
    print("=" * 60)
    print("📝 Instructions:")
    print("=" * 60)
    print()
    print("1. Copy the key above")
    print("2. Create a .env file in the project root (if not exists)")
    print("3. Add this line to your .env file:")
    print()
    print(f"   ENCRYPTION_MASTER_KEY={key}")
    print()
    print("4. Keep this key SECRET and SECURE!")
    print("5. NEVER commit the .env file to version control")
    print("6. Backup this key - if lost, encrypted data cannot be recovered")
    print()
    print("⚠️  WARNING: Changing this key will make existing encrypted")
    print("   data unreadable. Only change it if you're starting fresh.")
    print()
    print("=" * 60)
