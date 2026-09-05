import asyncio
import json
from collections.abc import AsyncIterator, Awaitable, Callable
from time import monotonic
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from robot_doc_rag.config import settings
from robot_doc_rag.repositories.tasks import (
    get_task,
    update_task_progress,
    update_task_status,
)

DisconnectChecker = Callable[[], Awaitable[bool]]
SessionFactory = async_sessionmaker[AsyncSession]
TERMINAL_STATUSES = {"completed", "failed"}


async def simulate_processing(task_id: UUID, factory: SessionFactory) -> None:
    """Simulate lightweight work, opening a fresh session for every update."""
    try:
        for progress in (10, 30, 50, 70, 100):
            await asyncio.sleep(settings.task_step_delay_seconds)
            task_status = "completed" if progress == 100 else "running"
            async with factory() as session:
                updated = await update_task_progress(session, task_id, progress, status=task_status)
                if updated is None:
                    return
    except asyncio.CancelledError:
        async with factory() as session:
            await update_task_status(session, task_id, "failed", error_message="Task cancelled")
        raise


def format_progress_event(task_id: UUID, status: str, progress: int) -> str:
    payload = {"task_id": str(task_id), "status": status, "progress": progress}
    return f"event: progress\ndata: {json.dumps(payload, separators=(',', ':'))}\n\n"


async def task_event_stream(
    task_id: UUID,
    is_disconnected: DisconnectChecker,
    factory: SessionFactory,
) -> AsyncIterator[str]:
    """Poll persisted state and yield changed states plus heartbeat comments."""
    previous_state: tuple[str, int] | None = None
    last_output_at = monotonic()

    while True:
        if await is_disconnected():
            return

        async with factory() as session:
            task = await get_task(session, task_id)
        if task is None:
            return

        current_state = (task.status, task.progress)
        now = monotonic()
        if current_state != previous_state:
            yield format_progress_event(task.id, task.status, task.progress)
            previous_state = current_state
            last_output_at = now
            if task.status in TERMINAL_STATUSES:
                return
        elif now - last_output_at >= settings.sse_heartbeat_seconds:
            yield ": heartbeat\n\n"
            last_output_at = now

        await asyncio.sleep(settings.task_poll_interval_seconds)
