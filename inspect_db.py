import sqlite3

def inspect_table():
    # Connect to the database
    conn = sqlite3.connect('sql_app.db')
    cursor = conn.cursor()
    
    # Get column info from user_profiles table
    cursor.execute('PRAGMA table_info(user_profiles)')
    columns = cursor.fetchall()
    
    print("\nColumns in user_profiles table:")
    print("-" * 50)
    for col in columns:
        print(f"Column {col[0]}: {col[1]} ({col[2]})")
    
    conn.close()

if __name__ == "__main__":
    inspect_table()
