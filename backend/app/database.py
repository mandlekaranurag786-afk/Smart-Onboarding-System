"""
Database connection and session management
"""
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from app.config import DATABASE_URL
from app.models.base import Base
import logging

logger = logging.getLogger(__name__)

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,
    max_overflow=20
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _ensure_candidate_auth_columns():
    """
    Add candidate auth columns for existing SQLite databases without migrations.
    """
    try:
        inspector = inspect(engine)
        if "candidates" not in inspector.get_table_names():
            return

        existing_columns = {column["name"] for column in inspector.get_columns("candidates")}
        required_columns = {
            "password_hash": "ALTER TABLE candidates ADD COLUMN password_hash VARCHAR(255)",
            "account_status": "ALTER TABLE candidates ADD COLUMN account_status VARCHAR(50) DEFAULT 'INVITED' NOT NULL",
            "password_reset_required": "ALTER TABLE candidates ADD COLUMN password_reset_required INTEGER DEFAULT 1 NOT NULL",
        }

        with engine.begin() as connection:
            for column_name, ddl in required_columns.items():
                if column_name not in existing_columns:
                    logger.info(f"Adding missing candidates.{column_name} column")
                    connection.execute(text(ddl))
    except Exception as exc:
        logger.error(f"Failed to ensure candidate auth columns: {exc}")
        raise

def init_db():
    """
    Initialize database - create all tables and ensure path existence
    """
    import os
    from app.config import DATABASE_URL
    
    # Extract path from sqlite:/// URL
    if DATABASE_URL.startswith("sqlite:///"):
        db_path = DATABASE_URL.replace("sqlite:///", "")
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            logger.info(f"Creating database directory: {db_dir}")
            os.makedirs(db_dir, exist_ok=True)

    logger.info(f"Initializing database at: {DATABASE_URL}")
    Base.metadata.create_all(bind=engine)
    _ensure_candidate_auth_columns()
    
    # Run IT Equipment Allocation migration
    try:
        from app.migrations.add_it_equipment_allocation_fields import run_migration
        run_migration()
    except Exception as e:
        logger.warning(f"IT Equipment Allocation migration warning: {e}")
    
    logger.info("Database initialized successfully")
    
    # Check if seeding is needed
    try:
        from app.init_db import seed_stakeholders
        seed_stakeholders()
    except Exception as e:
        logger.error(f"Post-initialization seeding failed: {e}")

def get_db() -> Session:
    """
    Get database session
    
    Usage in FastAPI:
        @app.get("/candidates")
        def get_candidates(db: Session = Depends(get_db)):
            return db.query(Candidate).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """
    Get database session as context manager
    
    Usage in agents:
        with get_db_context() as db:
            candidate = db.query(Candidate).filter_by(id=1).first()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()

def create_db_session() -> Session:
    """
    Create a new database session
    
    Usage in agents (manual management):
        db = create_db_session()
        try:
            candidate = db.query(Candidate).filter_by(id=1).first()
            db.commit()
        finally:
            db.close()
    """
    return SessionLocal()
