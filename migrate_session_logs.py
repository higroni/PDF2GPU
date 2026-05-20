"""
Migration script to add started_at column to session_logs table
"""
import sqlite3
from datetime import datetime

def migrate():
    conn = sqlite3.connect('pdf2gpu.db')
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(session_logs)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'started_at' not in columns:
            print("Adding started_at column to session_logs table...")
            cursor.execute("""
                ALTER TABLE session_logs 
                ADD COLUMN started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """)
            conn.commit()
            print("✅ Column added successfully!")
        else:
            print("✅ Column already exists!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()

# Made with Bob
