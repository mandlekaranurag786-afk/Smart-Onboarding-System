"""
Database initialization script with sample data
"""
import sys
sys.path.insert(0, '.')

from app.database import engine, SessionLocal
from app.models.base import Base
from app.models.stakeholder import Stakeholder
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Create all tables"""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("✓ Database tables created")

def seed_stakeholders():
    """Seed stakeholder data"""
    logger.info("Seeding stakeholder data...")
    
    db = SessionLocal()
    try:
        # Check if already seeded
        existing = db.query(Stakeholder).first()
        if existing:
            logger.info("Stakeholders already exist, skipping seed")
            return
        
        stakeholders = [
            # HR
            Stakeholder(
                name="Mohini",
                email="mohini@konverge.ai",
                role="HR",
                department="Human Resources",
                is_available=True
            ),
            
            # IT
            Stakeholder(
                name="Sagar",
                email="sagar@konverge.ai",
                role="IT",
                department="IT",
                is_available=True
            ),
            
            # Delivery Heads
            Stakeholder(
                name="Sajal",
                email="sajal@konverge.ai",
                role="Delivery Head",
                department="Artificial Intelligence",
                is_available=False,
                on_leave_until="2026-03-25",
                fallback_stakeholder_id="5"  # Jane Smith
            ),
            Stakeholder(
                name="Prathamesh",
                email="prathamesh@konverge.ai",
                role="Delivery Head",
                department="Cloud",
                is_available=True
            ),
            
            # Fallback Managers
            Stakeholder(
                name="Jane Smith",
                email="jane@konverge.ai",
                role="Senior Delivery Manager",
                department="Artificial Intelligence",
                is_available=True
            ),
            Stakeholder(
                name="Cloud Manager",
                email="cloudmgr@konverge.ai",
                role="Senior Delivery Manager",
                department="Cloud",
                is_available=True
            ),
            
            # Admin
            Stakeholder(
                name="Admin",
                email="admin@konverge.ai",
                role="Admin",
                department="Administration",
                is_available=True
            )
        ]
        
        db.add_all(stakeholders)
        db.commit()
        
        logger.info(f"✓ Seeded {len(stakeholders)} stakeholders")
        
        # Display seeded data
        for s in stakeholders:
            status = "ON LEAVE" if not s.is_available else "AVAILABLE"
            logger.info(f"  - {s.name} ({s.role}, {s.department}): {status}")
        
    except Exception as e:
        logger.error(f"Error seeding stakeholders: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Main initialization"""
    logger.info("=" * 60)
    logger.info("DATABASE INITIALIZATION")
    logger.info("=" * 60)
    
    try:
        # Create tables
        init_database()
        
        # Seed data
        seed_stakeholders()
        
        logger.info("=" * 60)
        logger.info("✓ Database initialization complete!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
