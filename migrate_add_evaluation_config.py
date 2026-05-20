"""
Migration: Add Evaluation Configuration Support
- Add collection_id to evaluations
- Add config_snapshot to evaluations
- Add performance tracking fields to evaluations
- Add performance tracking fields to test_example_results
"""
import sqlite3
import sys

def migrate():
    """Add evaluation configuration and performance tracking"""
    conn = sqlite3.connect('pdf2gpu.db')
    cursor = conn.cursor()
    
    try:
        print("Starting migration: Add Evaluation Configuration...")
        
        # 1. Add collection_id to evaluations
        print("Adding collection_id to evaluations...")
        try:
            cursor.execute("""
                ALTER TABLE evaluations 
                ADD COLUMN collection_id INTEGER
            """)
            print("  - collection_id added")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("  - collection_id already exists, skipping")
            else:
                raise
        
        # 2. Add config_snapshot to evaluations
        print("Adding config_snapshot to evaluations...")
        try:
            cursor.execute("""
                ALTER TABLE evaluations 
                ADD COLUMN config_snapshot TEXT
            """)
            print("  - config_snapshot added")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("  - config_snapshot already exists, skipping")
            else:
                raise
        
        # 3. Add performance fields to evaluations
        print("Adding performance fields to evaluations...")
        performance_fields = [
            ("avg_query_processing_ms", "INTEGER"),
            ("avg_search_ms", "INTEGER"),
            ("avg_reranking_ms", "INTEGER"),
            ("avg_llm_generation_ms", "INTEGER"),
            ("avg_total_latency_ms", "INTEGER"),
            ("total_evaluation_time_seconds", "INTEGER")
        ]
        
        for field_name, field_type in performance_fields:
            try:
                cursor.execute(f"""
                    ALTER TABLE evaluations 
                    ADD COLUMN {field_name} {field_type}
                """)
                print(f"  - {field_name} added")
            except sqlite3.OperationalError as e:
                if "duplicate column" in str(e).lower():
                    print(f"  - {field_name} already exists, skipping")
                else:
                    raise
        
        # 4. Add performance fields to test_example_results
        print("Adding performance fields to test_example_results...")
        result_performance_fields = [
            ("query_processing_ms", "INTEGER"),
            ("search_ms", "INTEGER"),
            ("reranking_ms", "INTEGER"),
            ("llm_generation_ms", "INTEGER"),
            ("total_latency_ms", "INTEGER")
        ]
        
        for field_name, field_type in result_performance_fields:
            try:
                cursor.execute(f"""
                    ALTER TABLE test_example_results 
                    ADD COLUMN {field_name} {field_type}
                """)
                print(f"  - {field_name} added")
            except sqlite3.OperationalError as e:
                if "duplicate column" in str(e).lower():
                    print(f"  - {field_name} already exists, skipping")
                else:
                    raise
        
        # 5. Create index on collection_id
        print("Creating index on collection_id...")
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_evaluations_collection_id 
                ON evaluations(collection_id)
            """)
            print("  - Index created")
        except sqlite3.OperationalError as e:
            print(f"  - Index creation skipped: {e}")
        
        conn.commit()
        print("\nMigration completed successfully!")
        print("\nSummary:")
        print("  - Added collection_id to evaluations")
        print("  - Added config_snapshot to evaluations")
        print("  - Added 6 performance fields to evaluations")
        print("  - Added 5 performance fields to test_example_results")
        print("  - Created index on collection_id")
        
    except Exception as e:
        print(f"\nX Migration failed: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()

# Made with Bob
