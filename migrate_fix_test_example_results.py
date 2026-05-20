"""
Migration: Fix test_example_results table columns
- Rename rouge_1_score -> rouge_1
- Rename rouge_2_score -> rouge_2  
- Rename rouge_l_score -> rouge_l
- Add exact_match column
- Add word_overlap column
- Make execution_time_ms nullable
"""
import sqlite3
import sys

def migrate():
    """Migrate test_example_results table"""
    conn = sqlite3.connect('pdf2gpu.db')
    cursor = conn.cursor()
    
    try:
        print("Starting migration...")
        
        # 1. Create new table with correct schema
        print("Creating new test_example_results table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_example_results_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_example_id INTEGER NOT NULL,
                evaluation_id INTEGER,
                generated_answer TEXT NOT NULL,
                bleu_score REAL,
                rouge_1 REAL,
                rouge_2 REAL,
                rouge_l REAL,
                bert_score_precision REAL,
                bert_score_recall REAL,
                bert_score_f1 REAL,
                exact_match INTEGER NOT NULL DEFAULT 0,
                word_overlap REAL,
                execution_time_ms INTEGER,
                context_used TEXT,
                created_at TIMESTAMP NOT NULL,
                FOREIGN KEY (test_example_id) REFERENCES test_examples(id),
                FOREIGN KEY (evaluation_id) REFERENCES evaluations(id)
            )
        """)
        
        # 2. Check if old table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='test_example_results'
        """)
        
        if cursor.fetchone():
            print("Copying data from old table...")
            # Copy data from old table (if it exists and has data)
            cursor.execute("""
                INSERT INTO test_example_results_new
                (id, test_example_id, evaluation_id, generated_answer,
                 bleu_score, rouge_1, rouge_2, rouge_l,
                 bert_score_precision, bert_score_recall, bert_score_f1,
                 exact_match, word_overlap, execution_time_ms, context_used, created_at)
                SELECT
                    id, test_example_id, evaluation_id, generated_answer,
                    bleu_score,
                    rouge_1_score as rouge_1,
                    rouge_2_score as rouge_2,
                    rouge_l_score as rouge_l,
                    bert_score_precision, bert_score_recall, bert_score_f1,
                    0 as exact_match,
                    NULL as word_overlap,
                    execution_time_ms, context_used, created_at
                FROM test_example_results
            """)
            
            # Drop old table
            print("Dropping old table...")
            cursor.execute("DROP TABLE test_example_results")
        
        # 3. Rename new table
        print("Renaming new table...")
        cursor.execute("ALTER TABLE test_example_results_new RENAME TO test_example_results")
        
        # 4. Create indexes
        print("Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_test_example_results_test_example_id ON test_example_results(test_example_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_test_example_results_evaluation_id ON test_example_results(evaluation_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_test_example_results_created_at ON test_example_results(created_at)")
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"X Migration failed: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()

# Made with Bob
