"""Main cleanup function"""
import datetime
import shutil
import sqlite3


def cleanup_unused_fields():
    """Main cleanup function"""
    print("🧹 Cleaning up unused database fields")
    print("=" * 60)

    DB_PATH = 'instance/greenlife.db'
    BACKUP_PATH = f'{DB_PATH}.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'

    if not os.path.exists(DB_PATH):
        print(f"❌ Database does not exist: {DB_PATH}")
        exit(1)

    # 1. Backup database
    print("1. Backing up database...")
    shutil.copy2(DB_PATH, BACKUP_PATH)
    print(f"   ✅ Backed up to: {BACKUP_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 2. Check current status
    print("\n2. Analyzing current table structure...")
    cursor.execute("PRAGMA table_info(user)")
    columns = cursor.fetchall()

    print(f"   Currently has {len(columns)} fields:")

    # Fields actually used by your model
    YOUR_MODEL_FIELDS = {
        'id', 'username', '_email_encrypted', 'password_hash',
        'user_type', 'ban_reason', 'ban_until', 
        'created_at', 'updated_at'
    }

    unused_fields = []
    used_fields = []

    for col in columns:
        name = col[1]
        col_type = col[2]
        not_null = "NOT NULL" if col[3] else "NULL"
        
        if name in YOUR_MODEL_FIELDS:
            used_fields.append((name, col_type, not_null))
            print(f"     ✅ {name:20} {col_type:15} {not_null:10} (used by model)")

        else:
            unused_fields.append((name, col_type, not_null))
            print(f"     ❌ {name:20} {col_type:15} {not_null:10} (unused)")

    print(f"\n   Summary:")
    print(f"     Used fields: {len(used_fields)}")
    print(f"     Unused fields: {len(unused_fields)}")

    if not unused_fields:
        print("\n🎉 No unused fields, no cleanup needed")
        conn.close()
        exit(0)

    # 3. Display unused fields details
    print(f"\n3. Unused fields details:")
    for name, col_type, not_null in unused_fields:
        # Check if there's data
        if name == 'email':
            cursor.execute(f"SELECT COUNT(*) FROM user WHERE {name} IS NOT NULL AND {name} != ''")
        else:
            cursor.execute(f"SELECT COUNT(*) FROM user WHERE {name} IS NOT NULL")
        
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"     ⚠️  {name}: has {count} records")
            # Show some sample data
            cursor.execute(f"SELECT {name} FROM user WHERE {name} IS NOT NULL LIMIT 2")
            samples = cursor.fetchall()
            for sample in samples:
                if sample[0]:
                    display = str(sample[0])[:30] + "..." if len(str(sample[0])) > 30 else str(sample[0])
                    print(f"        Sample: {display}")
        else:
            print(f"     📭 {name}: empty field")

    # 4. Ask for processing method
    print(f"\n4. Please select processing method:")

    print(f"   1. Delete all unused fields (cleanest)")
    print(f"   2. Delete only empty fields (safe)")
    print(f"   3. Add these field definitions to the model")
    print(f"   4. Ignore, do nothing")

    choice = input("\nPlease enter your choice (1/2/3/4): ").strip()

    if choice == '1':
        print(f"\n🗑️  Deleting all unused fields...")
        rebuild_table(conn, unused_fields, delete_all=True)
        
    elif choice == '2':
        print(f"\n🧹 Deleting only empty fields...")
        empty_fields = [f for f in unused_fields if is_field_empty(cursor, f[0])]
        if empty_fields:
            print(f"   Found {len(empty_fields)} empty fields:")
            for name, _, _ in empty_fields:
                print(f"     - {name}")
            rebuild_table(conn, empty_fields, delete_all=False)
        else:
            print(f"   ✅ No empty fields to delete")
        
    elif choice == '3':
        print(f"\n📝 Adding field definitions to the model:")
        print(f"\nIn the User class in blogapp/models.py, add:")
        for name, col_type, not_null in unused_fields:
            # Convert to SQLAlchemy type
            if 'VARCHAR' in col_type or 'TEXT' in col_type:
                length = ''
                if 'VARCHAR' in col_type:
                    length = col_type.replace('VARCHAR', '').replace('(', '').replace(')', '').strip()

                if length and length.isdigit():
                    py_type = f"db.String({length})"
                else:
                    py_type = "db.Text"
            elif 'INTEGER' in col_type:
                py_type = "db.Integer"
            elif 'DATETIME' in col_type:
                py_type = "db.DateTime"
            elif 'BOOLEAN' in col_type or 'BOOL' in col_type:
                py_type = "db.Boolean"
            else:
                py_type = "db.Column"  # Generic
            
            nullable = "True" if not_null == "NULL" else "False"
            
            print(f"    {name} = db.Column({py_type}, nullable={nullable})")
        
        print(f"\nThen restart the application")

    else:
        print(f"\n✅ Choosing to do nothing")
        print(f"   Unused fields will remain in the database")

    conn.close()

    print(f"\n" + "=" * 60)
    print(f"📋 Operation completed")
    print(f"   Database: {DB_PATH}")
    print(f"   Backup: {BACKUP_PATH}")