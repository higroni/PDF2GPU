"""
Migration script to fix evaluations table structure
"""
import sqlite3
from pathlib import Path

def migrate_database():
    """Drop old evaluations table and create new one"""
    db_path = Path("pdf2gpu.db")
    
    if not db_path.exists():
        print(f"Database {db_path} does not exist. Will be created on first run.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Drop old evaluations table
        cursor.execute("DROP TABLE IF EXISTS evaluations")
        print("Dropped old evaluations table.")
        
        # Drop old test_example_results table if exists
        cursor.execute("DROP TABLE IF EXISTS test_example_results")
        print("Dropped old test_example_results table.")
        
        # Create new evaluations table
        cursor.execute("""
            CREATE TABLE evaluations (
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
        print("Created new evaluations table.")
        
        # Create test_example_results table
        cursor.execute("""
            CREATE TABLE test_example_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evaluation_id INTEGER NOT NULL,
                test_example_id INTEGER NOT NULL,
                generated_answer TEXT NOT NULL,
                bleu_score FLOAT,
                rouge_1_score FLOAT,
                rouge_2_score FLOAT,
                rouge_l_score FLOAT,
                bert_score_precision FLOAT,
                bert_score_recall FLOAT,
                bert_score_f1 FLOAT,
                execution_time_ms INTEGER,
                context_used TEXT,
                created_at DATETIME NOT NULL,
                FOREIGN KEY (evaluation_id) REFERENCES evaluations(id) ON DELETE CASCADE,
                FOREIGN KEY (test_example_id) REFERENCES test_examples(id) ON DELETE CASCADE
            )
        """)
        print("Created test_example_results table.")
        
        # Create indexes
        cursor.execute("CREATE INDEX idx_evaluations_status ON evaluations(status)")
        cursor.execute("CREATE INDEX idx_evaluations_created_at ON evaluations(created_at)")
        cursor.execute("CREATE INDEX idx_test_example_results_evaluation_id ON test_example_results(evaluation_id)")
        cursor.execute("CREATE INDEX idx_test_example_results_test_example_id ON test_example_results(test_example_id)")
        print("Created indexes.")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()

# Made with Bob
