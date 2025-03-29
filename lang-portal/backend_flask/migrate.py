from lib.db import Db
import sqlite3
import os

def run_migrations():
    # Connect to the database
    db_path = os.path.join(os.path.dirname(__file__), 'word_bank.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    try:
        # Get list of migration files
        migrations_dir = os.path.join(os.path.dirname(__file__), 'sql', 'migrations')
        migration_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith('.sql')])
        
        # Run each migration
        for migration_file in migration_files:
            print(f"Running migration: {migration_file}")
            with open(os.path.join(migrations_dir, migration_file)) as f:
                migration_sql = f.read()
                conn.executescript(migration_sql)
                conn.commit()
        
        # Add study_activities table if it doesn't exist
        conn.execute('''
            CREATE TABLE IF NOT EXISTS study_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                preview_url TEXT
            )
        ''')
        
        # Update study_sessions table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                study_activity_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES groups(id),
                FOREIGN KEY (study_activity_id) REFERENCES study_activities(id)
            )
        ''')
        
        # Create word_review_items table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS word_review_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word_id INTEGER NOT NULL,
                study_session_id INTEGER NOT NULL,
                correct BOOLEAN NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (word_id) REFERENCES words(id),
                FOREIGN KEY (study_session_id) REFERENCES study_sessions(id)
            )
        ''')
        
        conn.commit()
        print("Migrations completed successfully")
    except Exception as e:
        print(f"Error running migrations: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    run_migrations()
