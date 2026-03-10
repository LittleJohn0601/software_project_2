import sqlite3

def fix_database():
    # Connect to the database
    conn = sqlite3.connect('instance/greenlife.db')
    cursor = conn.cursor()
    
    try:
        # Check the structure of the user table
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        print("Current columns of the user table:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Check if the ban_reason column exists
        column_names = [col[1] for col in columns]
        
        if 'ban_reason' not in column_names:
            print("\nAdding missing columns...")
            # Add the ban_reason column
            cursor.execute("ALTER TABLE user ADD COLUMN ban_reason TEXT")
            print("Added ban_reason column")
        
        if 'ban_until' not in column_names:
            # Add the ban_until column
            cursor.execute("ALTER TABLE user ADD COLUMN ban_until DATETIME")
            print("Added ban_until column")
        
        conn.commit()
        print("\nDatabase repair completed!")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_database()