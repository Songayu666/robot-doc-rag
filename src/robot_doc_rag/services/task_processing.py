import asyncio
import json
from collections.abc import AsyncIterator, Awaitable, Callable
from time import monotonic
from uuid import UUID

from robot_doc_rag.config import settings
from robot_doc_rag.services.memory_store import tasks, update_task

DisconnectChecker = Callable[[], Awaitable[bool]]
TERMINAL_STATUSES = {"completed", "failed"}


async def simulate_processing(task_id: UUID) -> None:
    """Simulate a lightweight I/O-bound document-processing task."""
    try:
        for progress in (10, 30, 50, 70, 100):
            await asyncio.sleep(settings.task_step_delay_seconds)
            task_status = "completed" if progress == 100 else "running"
            if update_task(task_id, status=task_status, progress=progress) is None:
                return
    except asyncio.CancelledError:
        current = tasks.get(task_id)
        if current is not None:
            update_task(task_id, status="failed", progress=current.progress)
        raise


def format_progress_event(task_id: UUID) -> str:
    task = tasks[task_id]
    payload = {
        "task_id": str(task.id),
        "status": task.status,
        "progress": task.progress,
    }
    return f"event: progress\ndata: {json.dumps(payload, separators=(',', ':'))}\n\n"


async def task_event_stream(
    task_id: UUID,
    is_disconnected: DisconnectChecker,
) -> AsyncIterator[str]:
    """Yield changed task states and periodic SSE heartbeat comments."""
    previous_state: tuple[str, int] | None = None
    last_output_at = monotonic()

    while True:
        if await is_disconnected():
            return

        task = tasks.get(task_id)
        if task is None:
            return

        current_state = (task.status, task.progress)
        now = monotonic()

        if current_state != previous_state:
            yield format_progress_event(task_id)
            previous_state = current_state
            last_output_at = now
            if task.status in TERMINAL_STATUSES:
                return
        elif now - last_output_at >= settings.sse_heartbeat_seconds:
            yield ": heartbeat\n\n"
            last_output_at = now

        await asyncio.sleep(settings.task_poll_interval_seconds)
