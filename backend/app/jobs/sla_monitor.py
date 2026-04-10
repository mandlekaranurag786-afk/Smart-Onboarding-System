"""
Lightweight SLA monitor runner.
"""
from __future__ import annotations

from threading import Event, Thread
import logging

from app.config import (
    SLA_ESCALATION_AFTER_HOURS,
    SLA_MONITOR_ENABLED,
    SLA_MONITOR_INTERVAL_SECONDS,
    SLA_WARNING_WINDOW_HOURS,
)
from app.database import create_db_session
from app.services.sla_service import SLAService

logger = logging.getLogger(__name__)

_stop_event = Event()
_monitor_thread: Thread | None = None


def run_sla_monitor_once() -> None:
    db = create_db_session()
    try:
        summary = SLAService.run_monitor(
            db,
            warning_window_hours=SLA_WARNING_WINDOW_HOURS,
            escalation_after_hours=SLA_ESCALATION_AFTER_HOURS,
        )
        logger.info("[SLA Monitor] Summary: %s", summary)
    except Exception as exc:  # noqa: BLE001
        logger.error("[SLA Monitor] Run failed: %s", exc)
    finally:
        db.close()


def _monitor_loop() -> None:
    while not _stop_event.is_set():
        run_sla_monitor_once()
        _stop_event.wait(SLA_MONITOR_INTERVAL_SECONDS)


def start_sla_monitor() -> None:
    global _monitor_thread

    if not SLA_MONITOR_ENABLED:
        logger.info("[SLA Monitor] Disabled by configuration")
        return

    if _monitor_thread and _monitor_thread.is_alive():
        return

    _stop_event.clear()
    _monitor_thread = Thread(target=_monitor_loop, name="sla-monitor", daemon=True)
    _monitor_thread.start()
    logger.info("[SLA Monitor] Started with interval=%ss", SLA_MONITOR_INTERVAL_SECONDS)


def stop_sla_monitor() -> None:
    _stop_event.set()
