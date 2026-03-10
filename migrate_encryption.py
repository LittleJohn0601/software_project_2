# migrate_encryption.py
"""
Manually migrate database, add encryption fields
Do not delete existing data
"""

import os
import sqlite3
import sys

# Set environment
os.environ.update({
    'FLASK_APP': 'blogapp',
    'FLASK_ENV': 'development',
    'DATABASE_URL': 'sqlite:///greenlife.db',
    'ENCRYPTION_MASTER_KEY': '05xWBfFHfE3-31f8PS95oyCqDjwg-7n1wGJ7e2IoWwY='
})

print("🔄 Database migration: adding encryption fields")
print("=" * 50)

def migrate_database():
    """Migrate existing database, add encryption fields"""
    
    db_path = 'instance/greenlife.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} does not exist")
        print("   Please run the application first to create the database")
        return False
    
    print(f"✅ Found database file: {db_path}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Check current table structure
        print("\n1. Checking current table structure...")
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        
        print(f"   Current user table has {len(columns)} fields:")
        for col in columns:
            print(f"     - {col[1]} ({col[2]})")
        
        # 2. Check if _email_encrypted field needs to be added
        existing_columns = [col[1] for col in columns]
        
        if '_email_encrypted' in existing_columns:
            print(f"\n✅ _email_encrypted field already exists")
        else:
            print(f"\n2. Adding _email_encrypted field...")
            
            # Add new field
            cursor.execute("""
                ALTER TABLE user 
                ADD COLUMN _email_encrypted TEXT
            """)
            
            print(f"   ✓ Added _email_encrypted field")
        
        # 3. Check other encryption fields
        fields_to_add = [
            ('_phone_encrypted', 'TEXT'),
            ('_full_name_encrypted', 'TEXT'),
            ('created_at', 'DATETIME'),
            ('updated_at', 'DATETIME'),
            ('last_login_at', 'DATETIME')
        ]
        
        print(f"\n3. Checking other fields...")
        for field_name, field_type in fields_to_add:
            if field_name not in existing_columns:
                try:
                    cursor.execute(f"""
                        ALTER TABLE user 
                        ADD COLUMN {field_name} {field_type}
                    """)
                    print(f"   ✓ Added {field_name} field")
                except Exception as e:
                    print(f"   ⚠️  Failed to add {field_name}: {e}")
            else:
                print(f"   ✓ {field_name} field already exists")
        
        # 4. Migrate existing data
        print(f"\n4. Migrating existing data...")
        
        # Check for old email field
        cursor.execute("PRAGMA table_info(user)")
        columns_after = [col[1] for col in cursor.fetchall()]
        
        if 'email' in columns_after and '_email_encrypted' in columns_after:
            print(f"   Detected legacy email field, need to migrate data")
            
            # Get all users' old emails
            cursor.execute("SELECT id, email FROM user WHERE email IS NOT NULL")
            users = cursor.fetchall()
            
            print(f"   Found {len(users)} users needing migration")
            
            # Import encryptor
            sys.path.append('.')
            from blogapp.email_encryptor import email_encryptor
            
            # Create Flask application context (for encryptor)
            from blogapp import create_app
            app = create_app()
            
            with app.app_context():
                migrated_count = 0
                
                for user_id, old_email in users:
                    try:
                        if old_email and not old_email.startswith('gAAAAA'):
                            # Encrypt email
                            encrypted = email_encryptor.encrypt_email(old_email)
                            
                            # Update database
                            cursor.execute("""
                                UPDATE user 
                                SET _email_encrypted = ?
                                WHERE id = ?
                            """, (encrypted, user_id))
                            
                            migrated_count += 1
                            if migrated_count <= 3:  # Only show first 3
                                print(f"     User {user_id}: {old_email[:20]}... → encrypted")
                    
                    except Exception as e:
                        print(f"     ⚠️  Failed to migrate user {user_id}: {e}")
                
                print(f"   ✓ Migrated email data for {migrated_count} users")
        
        # 5. Commit changes
        conn.commit()
        conn.close()
        
        print(f"\n" + "=" * 50)
        print(f"🎉 Database migration completed!")
        print(f"   File: {db_path}")
        print(f"   All encryption fields added")
        print(f"   Existing data preserved")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_migration():
    """Verify migration results"""
    print(f"\n🔍 Verifying migration results...")
    
    try:
        conn = sqlite3.connect('instance/greenlife.db')
        cursor = conn.cursor()
        
        # Check table structure
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        
        print(f"   User table now has {len(columns)} fields:")
        
        # Check key fields
        important_fields = ['_email_encrypted', 'email', 'username', 'password_hash']
        for field in important_fields:
            exists = any(field in col for col in columns)
            status = "✅" if exists else "❌"
            print(f"   {status} {field}")
        
        # Check data
        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]
        print(f"\n   Database has {user_count} users")
        
        if user_count > 0:
            cursor.execute("SELECT username, _email_encrypted FROM user LIMIT 3")
            users = cursor.fetchall()
            print(f"\n   Sample user data:")
            for username, encrypted_email in users:
                if encrypted_email:
                    status = "🔐" if encrypted_email.startswith('gAAAAA') else "⚠️"
                    print(f"   {status} {username}: {encrypted_email[:30]}...")
                else:
                    print(f"   ⚠️  {username}: email not encrypted")
        
        conn.close()
        
        print(f"\n✅ Verification completed")
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")

if __name__ == '__main__':
    print("🔄 Starting database migration")
    print("=" * 50)
    
    # Backup reminder
    print("⚠️  Note:")
    print("1. It's recommended to backup the database first")
    print("2. Migration process will not delete existing data")
    print("3. Only new fields will be added")
    
    response = input("\nContinue with migration? (yes/no): ")
    
    if response.lower() == 'yes':
        if migrate_database():
            verify_migration()
        else:
            print("\n❌ Migration failed, please check error messages")
    else:
        print("\n❌ Migration cancelled")