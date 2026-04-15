"""
In-memory event stream for IT task status updates.
"""
import asyncio
import json
import logging
from collections import defaultdict
from typing import Any, AsyncIterator, Dict

logger = logging.getLogger(__name__)


class ITTaskEventBus:
    """Broadcasts task update events to active SSE subscribers."""

    def __init__(self) -> None:
        self._subscribers: dict[int, set[asyncio.Queue[str]]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def subscribe(self, task_id: int) -> AsyncIterator[str]:
        queue: asyncio.Queue[str] = asyncio.Queue()

        async with self._lock:
            self._subscribers[task_id].add(queue)

        try:
            yield "event: connected\ndata: {}\n\n"

            while True:
                try:
                    payload = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield payload
                except asyncio.TimeoutError:
                    yield ": keep-alive\n\n"
        finally:
            async with self._lock:
                subscribers = self._subscribers.get(task_id)
                if subscribers and queue in subscribers:
                    subscribers.remove(queue)
                if subscribers == set():
                    self._subscribers.pop(task_id, None)

    def publish_task_update(self, task_id: int, payload: Dict[str, Any]) -> None:
        subscribers = list(self._subscribers.get(task_id, set()))
        if not subscribers:
            return

        message = f"event: task_update\ndata: {json.dumps(payload)}\n\n"
        stale_queues: list[asyncio.Queue[str]] = []

        for queue in subscribers:
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                stale_queues.append(queue)
            except Exception as exc:
                logger.warning(f"Failed to push IT task event for task {task_id}: {exc}")
                stale_queues.append(queue)

        if stale_queues:
            active = self._subscribers.get(task_id, set())
            for queue in stale_queues:
                active.discard(queue)


it_task_event_bus = ITTaskEventBus()
