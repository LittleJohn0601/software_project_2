#!/usr/bin/env python3
# migrate_to_encrypted_db.py
# Migrate existing unencrypted data to encrypted format

from blogapp import create_app, db
from blogapp.models import User, Factory
from blogapp.utils.encryption import encrypt_field

def migrate_users():
    """Migrate user emails and usernames to encrypted format"""
    print("🔄 Migrating user data to encrypted format...")
    
    users = User.query.all()
    migrated = 0
    
    for user in users:
        try:
            # Check if username is already encrypted
            if len(user._username) < 200:  # Unencrypted usernames are typically < 200 chars
                plaintext_username = user._username
                user.username = plaintext_username
                print(f"  ✅ Migrated username for user: {plaintext_username}")
                migrated += 1
            
            # Check if email is already encrypted
            if len(user._email) < 200:  # Unencrypted emails are typically < 200 chars
                plaintext_email = user._email
                user.email = plaintext_email
                print(f"  ✅ Migrated email for user: {user.username}")
                migrated += 1
        except Exception as e:
            print(f"  ⚠️  Failed to migrate user {user.id}: {e}")
    
    if migrated > 0:
        db.session.commit()
        print(f"✅ Successfully migrated {migrated} user field(s)")
    else:
        print("ℹ️  No user fields needed migration (already encrypted or no users found)")

def migrate_factories():
    """Migrate factory names, locations, and industry types to encrypted format"""
    print("\n🔄 Migrating factory data to encrypted format...")
    
    factories = Factory.query.all()
    migrated = 0
    
    for factory in factories:
        try:
            # Migrate name
            if factory._name and len(factory._name) < 200:  # Unencrypted
                plaintext_name = factory._name
                factory.name = plaintext_name
                print(f"  ✅ Migrated name for factory: {plaintext_name}")
                migrated += 1
            
            # Migrate location
            if factory._location and len(factory._location) < 200:  # Unencrypted
                plaintext_location = factory._location
                factory.location = plaintext_location
                print(f"  ✅ Migrated location for factory: {factory.name}")
                migrated += 1
            
            # Migrate industry_type
            if factory._industry_type and len(factory._industry_type) < 200:  # Unencrypted
                plaintext_industry = factory._industry_type
                factory.industry_type = plaintext_industry
                print(f"  ✅ Migrated industry type for factory: {factory.name}")
                migrated += 1
        except Exception as e:
            print(f"  ⚠️  Failed to migrate factory {factory.id}: {e}")
    
    if migrated > 0:
        db.session.commit()
        print(f"✅ Successfully migrated {migrated} factory field(s)")
    else:
        print("ℹ️  No factory fields needed migration (already encrypted or no factories found)")

def main():
    """Main migration function"""
    print("=" * 60)
    print("🔐 Database Encryption Migration Tool")
    print("=" * 60)
    print()
    print("This script will encrypt existing unencrypted data in your database.")
    print()
    print("⚠️  WARNING: Make sure you have:")
    print("   1. Set ENCRYPTION_MASTER_KEY in your .env file")
    print("   2. Backed up your database (instance/greenlife.db)")
    print()
    
    response = input("Do you want to continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("❌ Migration cancelled")
        return
    
    print()
    print("Starting migration...")
    print()
    
    app = create_app()
    with app.app_context():
        try:
            # Check if encryption key is set
            if not app.config.get('ENCRYPTION_MASTER_KEY'):
                print("❌ ERROR: ENCRYPTION_MASTER_KEY not set in .env file!")
                print("   Please run: python generate_encryption_key.py")
                return
            
            # Migrate users
            migrate_users()
            
            # Migrate factories
            migrate_factories()
            
            print()
            print("=" * 60)
            print("✅ Migration completed successfully!")
            print("=" * 60)
            print()
            print("Next steps:")
            print("1. Verify the migration by checking your data")
            print("2. Test login and factory operations")
            print("3. Keep your encryption key safe!")
            print()
            
        except Exception as e:
            print()
            print("=" * 60)
            print(f"❌ Migration failed: {e}")
            print("=" * 60)
            print()
            print("Please check:")
            print("1. Database connection is working")
            print("2. ENCRYPTION_MASTER_KEY is valid")
            print("3. Database backup exists")
            print()
            db.session.rollback()

if __name__ == '__main__':
    main()
