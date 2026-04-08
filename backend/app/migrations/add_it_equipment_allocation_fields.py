"""
Database migration script for IT Equipment Allocation Workflow
Adds new fields to tasks table and creates it_team_members table
"""
import sqlite3
import logging
from app.config import DATABASE_URL

logger = logging.getLogger(__name__)


def get_db_path():
    """Extract database path from DATABASE_URL"""
    if DATABASE_URL.startswith("sqlite:///"):
        return DATABASE_URL.replace("sqlite:///", "")
    raise ValueError("Only SQLite databases are supported for this migration")


def run_migration():
    """
    Run the migration to add IT equipment allocation fields
    """
    db_path = get_db_path()
    logger.info(f"Running IT Equipment Allocation migration on database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if tasks table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
        if not cursor.fetchone():
            logger.error("Tasks table does not exist. Please run init_db first.")
            return False
        
        # Get existing columns in tasks table
        cursor.execute("PRAGMA table_info(tasks)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        
        # Add new columns to tasks table if they don't exist
        new_columns = {
            "it_response_token": "ALTER TABLE tasks ADD COLUMN it_response_token VARCHAR(255)",
            "it_response_received_at": "ALTER TABLE tasks ADD COLUMN it_response_received_at DATETIME",
            "it_response_type": "ALTER TABLE tasks ADD COLUMN it_response_type VARCHAR(50)",
            "it_responder_email": "ALTER TABLE tasks ADD COLUMN it_responder_email VARCHAR(255)",
            "it_responder_name": "ALTER TABLE tasks ADD COLUMN it_responder_name VARCHAR(255)",
            "it_response_message": "ALTER TABLE tasks ADD COLUMN it_response_message TEXT",
            "it_reminder_sent_count": "ALTER TABLE tasks ADD COLUMN it_reminder_sent_count INTEGER DEFAULT 0",
            "it_last_reminder_sent_at": "ALTER TABLE tasks ADD COLUMN it_last_reminder_sent_at DATETIME",
        }
        
        for column_name, ddl in new_columns.items():
            if column_name not in existing_columns:
                logger.info(f"Adding column: {column_name}")
                cursor.execute(ddl)
            else:
                logger.info(f"Column {column_name} already exists, skipping")
        
        # Create indexes for tasks table (including unique index for it_response_token)
        logger.info("Creating indexes for tasks table")
        try:
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_tasks_it_response_token ON tasks(it_response_token)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at)")
        except Exception as e:
            logger.warning(f"Index creation warning (may already exist): {e}")
        
        # Check if it_team_members table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='it_team_members'")
        if not cursor.fetchone():
            logger.info("Creating it_team_members table")
            cursor.execute("""
                CREATE TABLE it_team_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    is_active INTEGER DEFAULT 1 NOT NULL,
                    notification_enabled INTEGER DEFAULT 1 NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
            """)
            
            # Create index for it_team_members
            cursor.execute("CREATE INDEX idx_it_team_members_email ON it_team_members(email)")
            logger.info("it_team_members table created successfully")
        else:
            logger.info("it_team_members table already exists, skipping")
        
        conn.commit()
        logger.info("Migration completed successfully")
        return True
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Migration failed: {e}")
        raise
    finally:
        conn.close()


def rollback_migration():
    """
    Rollback the migration (remove added fields and table)
    Note: SQLite doesn't support DROP COLUMN, so this is limited
    """
    db_path = get_db_path()
    logger.info(f"Rolling back IT Equipment Allocation migration on database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Drop it_team_members table
        cursor.execute("DROP TABLE IF EXISTS it_team_members")
        logger.info("Dropped it_team_members table")
        
        # Note: SQLite doesn't support DROP COLUMN
        # To remove columns from tasks table, you would need to:
        # 1. Create a new table without those columns
        # 2. Copy data from old table to new table
        # 3. Drop old table
        # 4. Rename new table
        # This is complex and risky, so we'll just log a warning
        logger.warning("SQLite does not support DROP COLUMN. Task table columns cannot be removed automatically.")
        logger.warning("If you need to remove the columns, you'll need to manually recreate the table.")
        
        conn.commit()
        logger.info("Rollback completed (partial - see warnings)")
        return True
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Rollback failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run migration
    run_migration()
