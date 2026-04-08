"""
Seed script to add initial IT team members
"""
import logging
from app.database import create_db_session
from app.models import ITTeamMember
from app.config import IT_EMAIL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_it_team_members():
    """
    Seed initial IT team members from configuration
    """
    db = create_db_session()
    
    try:
        # Check if IT team members already exist
        existing_count = db.query(ITTeamMember).count()
        if existing_count > 0:
            logger.info(f"IT team members already seeded ({existing_count} members exist)")
            return
        
        # Add IT team member from config
        if IT_EMAIL:
            # Check if already exists
            existing = db.query(ITTeamMember).filter(ITTeamMember.email == IT_EMAIL).first()
            if not existing:
                it_member = ITTeamMember(
                    name="IT Team",
                    email=IT_EMAIL,
                    is_active=1,
                    notification_enabled=1
                )
                db.add(it_member)
                db.commit()
                logger.info(f"Added IT team member: {IT_EMAIL}")
            else:
                logger.info(f"IT team member already exists: {IT_EMAIL}")
        else:
            logger.warning("IT_EMAIL not configured in environment variables")
        
        logger.info("IT team seeding completed")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding IT team members: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_it_team_members()
