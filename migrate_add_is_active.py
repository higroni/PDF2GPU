"""
Migration script to add is_active column to test_examples table
"""
import sqlite3
from pathlib import Path

def migrate_database():
    """Add is_active column to test_examples table"""
    db_path = Path("pdf2gpu.db")
    
    if not db_path.exists():
        print(f"Database {db_path} does not exist. Will be created on first run.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(test_examples)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'is_active' in columns:
            print("Column 'is_active' already exists in test_examples table.")
        else:
            # Add the column
            cursor.execute("""
                ALTER TABLE test_examples 
                ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1
            """)
            conn.commit()
            print("Successfully added 'is_active' column to test_examples table.")
        
        # Create evaluations table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR NOT NULL,
                description TEXT,
                status VARCHAR NOT NULL DEFAULT 'pending',
                created_at DATETIME NOT NULL,
                started_at DATETIME,
                completed_at DATETIME,
                total_examples INTEGER,
                completed_examples INTEGER,
                avg_bleu_score FLOAT,
                avg_rouge_1 FLOAT,
                avg_rouge_2 FLOAT,
                avg_rouge_l FLOAT,
                avg_bert_score FLOAT,
                exact_match_percentage FLOAT
            )
        """)
        
        # Create test_example_results table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_example_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evaluation_id INTEGER NOT NULL,
                test_example_id INTEGER NOT NULL,
                generated_answer TEXT NOT NULL,
                bleu_score FLOAT,
                rouge_1 FLOAT,
                rouge_2 FLOAT,
                rouge_l FLOAT,
                bert_score FLOAT,
                exact_match BOOLEAN,
                execution_time FLOAT,
                created_at DATETIME NOT NULL,
                FOREIGN KEY (evaluation_id) REFERENCES evaluations(id) ON DELETE CASCADE,
                FOREIGN KEY (test_example_id) REFERENCES test_examples(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        print("Successfully created evaluations and test_example_results tables.")
        
        # Create indexes - check if they exist first
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_test_examples_is_active ON test_examples(is_active)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_evaluations_status ON evaluations(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_evaluations_created_at ON evaluations(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_test_example_results_evaluation_id ON test_example_results(evaluation_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_test_example_results_test_example_id ON test_example_results(test_example_id)")
            conn.commit()
            print("Successfully created indexes.")
        except sqlite3.Error as idx_error:
            print(f"Index creation warning (may already exist): {idx_error}")
            conn.rollback()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()

# Made with Bob
