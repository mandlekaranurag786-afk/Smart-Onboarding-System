from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.candidate import Candidate
from app.models.checklist import Checklist
from app.models.task import Task

router = APIRouter(tags=["analytics"])


def _parse_datetime(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        normalized = value.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(normalized)
        except ValueError:
            return None
    return None


@router.get("/analytics/dashboard")
def get_analytics_dashboard(db: Session = Depends(get_db)):
    try:
        owner_values = [
            row[0]
            for row in db.execute(
                text("SELECT DISTINCT owner FROM tasks WHERE owner IS NOT NULL")
            ).fetchall()
        ]

        onboarded_total = (
            db.query(func.count(Candidate.id))
            .join(Checklist, Checklist.candidate_id == Candidate.id)
            .filter(Checklist.completion_percentage == 100.0)
            .scalar()
            or 0
        )

        in_progress_total = (
            db.query(func.count(Candidate.id))
            .join(Checklist, Checklist.candidate_id == Candidate.id)
            .filter(Checklist.completion_percentage < 100.0)
            .scalar()
            or 0
        )

        it_owners = [owner for owner in owner_values if owner in {"IT", "SYSTEM"}]
        hr_owners = [owner for owner in owner_values if owner in {"HR", "MANAGER", "DELIVERY_HEAD"}]
        candidate_owners = [owner for owner in owner_values if owner == "CANDIDATE"]

        def count_pending_by_owners(owners):
            if not owners:
                return 0

            count = 0
            for owner in owners:
                count += (
                    db.execute(
                        text(
                            """
                            SELECT COUNT(t.id)
                            FROM tasks t
                            JOIN checklists cl ON t.checklist_id = cl.id
                            JOIN candidates c ON cl.candidate_id = c.id
                            WHERE t.owner = :owner_value
                              AND t.status = 'PENDING'
                            """
                        ),
                        {"owner_value": owner},
                    ).scalar()
                    or 0
                )
            return count

        it_pending = count_pending_by_owners(it_owners)
        hr_pending = count_pending_by_owners(hr_owners)
        candidate_pending = count_pending_by_owners(candidate_owners)
        total_pending = it_pending + hr_pending + candidate_pending

        completed_rows = (
            db.query(Candidate.created_at, Candidate.updated_at)
            .join(Checklist, Checklist.candidate_id == Candidate.id)
            .filter(Checklist.completion_percentage == 100.0)
            .all()
        )

        durations = []
        for created_at, updated_at in completed_rows:
            created = _parse_datetime(created_at)
            updated = _parse_datetime(updated_at)
            if created and updated:
                durations.append((updated - created).total_seconds() / 86400)

        avg_days = round(sum(durations) / len(durations), 1) if durations else 0.0

        return {
            "onboarded": {"total": onboarded_total},
            "in_progress": {"total": in_progress_total},
            "pending_tasks": {
                "total": total_pending,
                "it": it_pending,
                "hr": hr_pending,
                "candidate": candidate_pending,
            },
            "avg_onboarding_time": {"avg_days": avg_days},
        }

    except Exception:
        return {
            "onboarded": {"total": 0},
            "in_progress": {"total": 0},
            "pending_tasks": {"total": 0, "it": 0, "hr": 0, "candidate": 0},
            "avg_onboarding_time": {"avg_days": 0.0},
        }
