import sqlite3
import os

db_path = 'backend/data/calibr.db'

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE session ADD COLUMN chat_history TEXT")
        conn.commit()
        print("Successfully added chat_history column to session table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column chat_history already exists.")
        else:
            print(f"Error: {e}")
    finally:
        conn.close()
else:
    print(f"Database file not found at {db_path}")
