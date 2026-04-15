"""
Database initialization script with sample data
"""
import sys
sys.path.insert(0, '.')

from app.database import engine, SessionLocal
from app.models.base import Base
from app.models.stakeholder import Stakeholder
from app.models.candidate import CandidateAccountStatus
from app.security import hash_password
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

def seed_candidates():
    """Seed candidate data"""
    from app.models.candidate import Candidate, CandidateStatus
    from app.models.checklist import Checklist
    from app.models.task import Task, TaskStatus, TaskOwner
    
    logger.info("Seeding candidate data...")
    db = SessionLocal()
    try:
        # Check if already seeded
        existing = db.query(Candidate).first()
        if existing:
            logger.info("Candidates already exist, skipping seed")
            return
        
        # Create a default candidate for testing
        tejas = Candidate(
            name="Tejas Ninanwe",
            email="tejas@konverge.ai",
            role="SDE - Artificial Intelligence",
            department="Delivery and Practices > Artificial Intelligence",
            joining_date=datetime(2026, 3, 25).date(),
            reporting_manager="Kaustubh Vartak",
            status=CandidateStatus.ONBOARDED,
            password_hash=hash_password("Tejas@123"),
            account_status=CandidateAccountStatus.ACTIVE,
            password_reset_required=0
        )
        db.add(tejas)
        db.flush() # Get ID
        
        # Create a checklist for him
        checklist = Checklist(candidate_id=tejas.id)
        db.add(checklist)
        db.flush()
        
        # Add a few completed and pending tasks
        tasks = [
            Task(checklist_id=checklist.id, name="Document Signing", owner=TaskOwner.HR, status=TaskStatus.COMPLETED, completed_date=datetime(2026, 3, 20)),
            Task(checklist_id=checklist.id, name="Work Profile Builder", owner=TaskOwner.CANDIDATE, status=TaskStatus.COMPLETED, completed_date=datetime(2026, 3, 21)),
            Task(checklist_id=checklist.id, name="Asset Assignment", owner=TaskOwner.IT, status=TaskStatus.COMPLETED, completed_date=datetime(2026, 3, 22)),
            Task(checklist_id=checklist.id, name="Account and Assets Provisioning", owner=TaskOwner.SYSTEM, status=TaskStatus.PENDING),
            Task(checklist_id=checklist.id, name="Meeting: HR Walkthrough", owner=TaskOwner.HR, status=TaskStatus.PENDING),
            Task(checklist_id=checklist.id, name="Meeting: Reporting Manager", owner=TaskOwner.MANAGER, status=TaskStatus.PENDING),
        ]
        db.add_all(tasks)
        db.commit()
        logger.info("✓ Seeded candidate: Tejas Ninanwe (tejas@konverge.ai) with 6 tasks")
        
    except Exception as e:
        logger.error(f"Error seeding candidates: {e}")
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
        seed_candidates()
        
        logger.info("=" * 60)
        logger.info("✓ Database initialization complete!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
