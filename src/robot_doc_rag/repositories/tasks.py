from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from robot_doc_rag.models.task import Task


async def create_task(session: AsyncSession, *, document_id: UUID, task_type: str) -> Task:
    task = Task(document_id=document_id, task_type=task_type, status="pending", progress=0)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def get_task(session: AsyncSession, task_id: UUID) -> Task | None:
    return await session.get(Task, task_id)


async def update_task_status(
    session: AsyncSession,
    task_id: UUID,
    status: str,
    *,
    error_message: str | None = None,
) -> Task | None:
    task = await get_task(session, task_id)
    if task is None:
        return None
    task.status = status
    task.error_message = error_message
    await session.commit()
    await session.refresh(task)
    return task


async def update_task_progress(
    session: AsyncSession, task_id: UUID, progress: int, *, status: str
) -> Task | None:
    task = await get_task(session, task_id)
    if task is None:
        return None
    task.progress = progress
    task.status = status
    await session.commit()
    await session.refresh(task)
    return task
