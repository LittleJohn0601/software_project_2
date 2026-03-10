import sqlite3

# connect to database
db_path = 'instance/greenlife.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"=== database: {db_path} ===")
    print("=" * 50)
    
    # 1. check all of the tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    if not tables:
        print("nothing in tha db")
    else:
        print(f"found {len(tables)} tables:")
        for i, table in enumerate(tables, 1):
            print(f"  {i}. {table[0]}")
    
    # 2. check data of every table
    for table in tables:
        table_name = table[0]
        print(f"\n{'='*50}")
        print(f"表名: {table_name}")
        print(f"{'='*50}")
        
        # check structure
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print("structure:")
        print("-" * 30)
        for col in columns:
            col_id, col_name, col_type, notnull, default_val, pk = col
            pk_flag = " (key)" if pk else ""
            print(f"  {col_id}. {col_name}: {col_type}{pk_flag}")
        
        # check data
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        print(f"\ndata length: {row_count}")
        
        if row_count > 0:
            print("\nshows data(top 10):")
            print("-" * 40)
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 10")
            rows = cursor.fetchall()
            
            # shows names
            col_names = [col[1] for col in columns]
            print(" | ".join(col_names))
            print("-" * 40)
            
            for row in rows:
                formatted_row = []
                for value in row:
                    if value is None:
                        formatted_row.append("NULL")
                    elif isinstance(value, str):
                        formatted_row.append(f"'{value[:20]}...'" if len(value) > 20 else f"'{value}'")
                    else:
                        formatted_row.append(str(value))
                print(" | ".join(formatted_row))
        
        # ask whether to check all data
        if row_count > 10:
            show_all = input(f"\nshows {row_count} rows of data，sure to show all？(y/n): ")
            if show_all.lower() == 'y':
                cursor.execute(f"SELECT * FROM {table_name}")
                all_rows = cursor.fetchall()
                print("\nall data:")
                print("-" * 40)
                for row in all_rows:
                    print(row)
    
    conn.close()
    
except FileNotFoundError:
    print(f"error: cannot find file '{db_path}'")
   
except Exception as e:
    print(f"error: {e}")