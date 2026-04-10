"""
SLA service - assigns deadlines, evaluates breaches, and emits alerts.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
import logging
from typing import Dict, Optional

from sqlalchemy.orm import Session

from app.api.activities import log_activity
from app.api.notifications import Notification
from app.models.candidate import Candidate
from app.models.sla_event import SLAEvent
from app.models.task import Task, TaskStatus

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SLAWindow:
    amount: int
    unit: str  # "hours" or "days"


class SLAService:
    """Utility methods for task SLA assignment and monitoring."""

    TASK_RULES: Dict[str, tuple[str, int]] = {
        "document_signing": ("days", 3),
        "profile_building": ("days", 5),
        "it_equipment_allocation": ("days", 2),
        "account_provisioning": ("days", 2),
        "meeting_scheduling": ("hours", 48),
        "portal_acknowledgment": ("days", 2),
        "final_review": ("days", 2),
    }
    WARNING_WINDOW_HOURS = 12
    ESCALATION_AFTER_HOURS = 24

    @classmethod
    def get_rule_for_task(cls, task_type: str, settings: Optional[Dict[str, int]] = None) -> SLAWindow:
        settings = settings or {}

        if task_type == "meeting_scheduling":
            return SLAWindow(amount=int(settings.get("meeting_scheduling_hours", 48)), unit="hours")
        if task_type == "document_signing":
            return SLAWindow(amount=int(settings.get("document_signing_days", 3)), unit="days")
        if task_type in {"it_equipment_allocation", "account_provisioning"}:
            return SLAWindow(amount=int(settings.get("it_setup_days", 2)), unit="days")

        unit, amount = cls.TASK_RULES.get(task_type, ("days", int(settings.get("task_completion_days", 7))))
        return SLAWindow(amount=int(amount), unit=unit)

    @classmethod
    def compute_due_at(
        cls,
        task: Task,
        candidate: Optional[Candidate] = None,
        settings: Optional[Dict[str, int]] = None,
    ) -> datetime:
        base_time = task.created_at or datetime.utcnow()
        rule = cls.get_rule_for_task(task.task_type, settings)

        if task.task_type in {"it_equipment_allocation", "account_provisioning"} and candidate and candidate.joining_date:
            join_dt = datetime.combine(candidate.joining_date, time(hour=9))
            due_at = join_dt - timedelta(days=1)
            return due_at if due_at > base_time else base_time + timedelta(hours=rule.amount if rule.unit == "hours" else rule.amount * 24)

        if rule.unit == "hours":
            return base_time + timedelta(hours=rule.amount)
        return base_time + timedelta(days=rule.amount)

    @classmethod
    def apply_task_sla(
        cls,
        task: Task,
        candidate: Optional[Candidate] = None,
        settings: Optional[Dict[str, int]] = None,
    ) -> Task:
        if not task.sla_due_at:
            task.sla_due_at = cls.compute_due_at(task, candidate, settings)

        if not task.due_date:
            task.due_date = task.sla_due_at.date()

        if task.status == TaskStatus.COMPLETED:
            task.sla_status = "resolved"
        elif task.status == TaskStatus.OVERDUE:
            task.sla_status = "breached"
        else:
            task.sla_status = task.sla_status or "within_sla"

        return task

    @classmethod
    def sync_task_resolution(cls, task: Task) -> None:
        if task.status == TaskStatus.COMPLETED:
            task.sla_status = "resolved"
            task.sla_breached_at = None
            task.sla_escalation_level = 0
        elif task.status == TaskStatus.OVERDUE:
            task.sla_status = "breached"
            task.sla_breached_at = task.sla_breached_at or datetime.utcnow()
        elif task.status == TaskStatus.BLOCKED:
            task.sla_status = "blocked"
        else:
            if task.sla_due_at and task.sla_due_at <= datetime.utcnow():
                task.sla_status = "breached"
            else:
                task.sla_status = "within_sla"

    @classmethod
    def run_monitor(
        cls,
        db: Session,
        *,
        warning_window_hours: Optional[int] = None,
        escalation_after_hours: Optional[int] = None,
    ) -> Dict[str, int]:
        now = datetime.utcnow()
        warning_window = timedelta(hours=warning_window_hours or cls.WARNING_WINDOW_HOURS)
        escalation_after = timedelta(hours=escalation_after_hours or cls.ESCALATION_AFTER_HOURS)
        summary = {"warnings": 0, "breaches": 0, "escalations": 0, "resolved": 0}

        open_tasks = (
            db.query(Task)
            .filter(Task.status != TaskStatus.COMPLETED)
            .all()
        )

        for task in open_tasks:
            candidate = task.checklist.candidate if task.checklist else None
            if not task.sla_due_at:
                cls.apply_task_sla(task, candidate)

            if not task.sla_due_at:
                continue

            remaining = task.sla_due_at - now
            previous_status = task.sla_status or "within_sla"

            if remaining <= timedelta(0):
                task.status = TaskStatus.OVERDUE
                task.sla_status = "breached"
                task.sla_breached_at = task.sla_breached_at or now

                if previous_status != "breached":
                    summary["breaches"] += 1
                    cls._record_event(
                        db,
                        task,
                        candidate,
                        event_type="breach",
                        severity="high",
                        title="SLA breached",
                        message=f"{task.name} breached its SLA and is now overdue.",
                    )

                breach_age = now - (task.sla_breached_at or now)
                if breach_age >= escalation_after and task.sla_escalation_level < 1:
                    task.sla_escalation_level = 1
                    summary["escalations"] += 1
                    cls._record_event(
                        db,
                        task,
                        candidate,
                        event_type="escalated",
                        severity="critical",
                        title="SLA escalated",
                        message=f"{task.name} has remained overdue for more than {int(escalation_after.total_seconds() // 3600)} hours.",
                    )
            elif remaining <= warning_window:
                if previous_status != "at_risk":
                    summary["warnings"] += 1
                    task.sla_status = "at_risk"
                    cls._record_event(
                        db,
                        task,
                        candidate,
                        event_type="warning",
                        severity="medium",
                        title="SLA at risk",
                        message=f"{task.name} is approaching its SLA deadline.",
                    )
            else:
                if previous_status in {"at_risk", "breached", "escalated", "blocked"}:
                    summary["resolved"] += 1
                task.sla_status = "within_sla"
                task.sla_breached_at = None
                task.sla_escalation_level = 0

        db.commit()
        return summary

    @classmethod
    def get_metrics(cls, db: Session) -> Dict[str, object]:
        now = datetime.utcnow()
        warning_cutoff = now + timedelta(hours=cls.WARNING_WINDOW_HOURS)

        overdue_tasks = db.query(Task).filter(Task.status == TaskStatus.OVERDUE).count()
        at_risk_tasks = (
            db.query(Task)
            .filter(
                Task.status != TaskStatus.COMPLETED,
                Task.sla_due_at.is_not(None),
                Task.sla_due_at > now,
                Task.sla_due_at <= warning_cutoff,
            )
            .count()
        )
        escalated_tasks = (
            db.query(Task)
            .filter(Task.sla_escalation_level > 0, Task.status != TaskStatus.COMPLETED)
            .count()
        )

        bottlenecks: Dict[str, int] = {}
        rows = (
            db.query(Task.owner, Task.id)
            .filter(Task.status.in_([TaskStatus.OVERDUE, TaskStatus.BLOCKED]))
            .all()
        )
        for owner, _task_id in rows:
            owner_key = owner.value if hasattr(owner, "value") else str(owner)
            bottlenecks[owner_key] = bottlenecks.get(owner_key, 0) + 1

        top_bottlenecks = [
            {"owner": owner, "count": count}
            for owner, count in sorted(bottlenecks.items(), key=lambda item: item[1], reverse=True)
        ][:5]

        return {
            "sla_summary": {
                "overdue": overdue_tasks,
                "at_risk": at_risk_tasks,
                "escalated": escalated_tasks,
            },
            "bottlenecks": top_bottlenecks,
        }

    @classmethod
    def _record_event(
        cls,
        db: Session,
        task: Task,
        candidate: Optional[Candidate],
        *,
        event_type: str,
        severity: str,
        title: str,
        message: str,
    ) -> None:
        existing = (
            db.query(SLAEvent)
            .filter(
                SLAEvent.task_id == task.id,
                SLAEvent.event_type == event_type,
                SLAEvent.message == message,
            )
            .first()
        )
        if existing:
            return

        event = SLAEvent(
            task_id=task.id,
            candidate_id=candidate.id if candidate else None,
            event_type=event_type,
            severity=severity,
            title=title,
            message=message,
            triggered_at=datetime.utcnow(),
            owner=task.owner.value if hasattr(task.owner, "value") else str(task.owner),
        )
        db.add(event)

        if candidate:
            notification = Notification(
                user_id=candidate.id,
                user_type="candidate",
                title=title,
                message=message,
                notification_type="alert",
                related_id=task.id,
            )
            db.add(notification)

        log_activity(
            db,
            user_name="SLA Monitor",
            user_role="System",
            action_text=message,
            target_object=task.name,
            activity_type="system",
            icon_type="alert",
        )
        logger.info("[SLA] %s for task %s", event_type, task.id)
