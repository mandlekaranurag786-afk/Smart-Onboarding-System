"""
Query database to see stored data
"""
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models.candidate import Candidate
from app.models.checklist import Checklist
from app.models.task import Task
from app.models.stakeholder import Stakeholder
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def query_candidates():
    """Query all candidates"""
    db = SessionLocal()
    try:
        candidates = db.query(Candidate).all()
        
        logger.info("=" * 60)
        logger.info(f"CANDIDATES ({len(candidates)} total)")
        logger.info("=" * 60)
        
        for candidate in candidates:
            logger.info(f"\nID: {candidate.id}")
            logger.info(f"Name: {candidate.name}")
            logger.info(f"Email: {candidate.email}")
            logger.info(f"Department: {candidate.department}")
            logger.info(f"Status: {candidate.status.value}")
            logger.info(f"Joining Date: {candidate.joining_date}")
            
            # Get checklist
            if candidate.checklist:
                checklist = candidate.checklist
                logger.info(f"\nChecklist ID: {checklist.id}")
                logger.info(f"Completion: {checklist.completion_percentage}%")
                logger.info(f"Tasks: {len(checklist.tasks)}")
                
                # Show tasks
                for task in checklist.tasks:
                    logger.info(f"  - {task.name} ({task.owner.value}): {task.status.value}")
            
            logger.info("-" * 60)
        
    finally:
        db.close()

def query_stakeholders():
    """Query all stakeholders"""
    db = SessionLocal()
    try:
        stakeholders = db.query(Stakeholder).all()
        
        logger.info("\n" + "=" * 60)
        logger.info(f"STAKEHOLDERS ({len(stakeholders)} total)")
        logger.info("=" * 60)
        
        for s in stakeholders:
            status = "ON LEAVE" if not s.is_available else "AVAILABLE"
            logger.info(f"{s.id}. {s.name} ({s.role}, {s.department}): {status}")
            if not s.is_available:
                logger.info(f"   Until: {s.on_leave_until}")
        
    finally:
        db.close()

def main():
    logger.info("\n" + "=" * 60)
    logger.info("DATABASE QUERY")
    logger.info("=" * 60)
    
    query_candidates()
    query_stakeholders()
    
    logger.info("\n" + "=" * 60)
    logger.info("✓ Query complete!")
    logger.info("=" * 60 + "\n")

if __name__ == "__main__":
    main()
