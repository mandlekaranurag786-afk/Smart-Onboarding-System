"""
Database connection and session management
"""
from sqlalchemy import create_engine
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

def init_db():
    """
    Initialize database - create all tables
    
    Call this once at application startup
    """
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")

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
