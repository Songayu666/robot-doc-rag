from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from robot_doc_rag.db.session import get_session
from robot_doc_rag.repositories.documents import get_document
from robot_doc_rag.repositories.tasks import create_task as create_task_record
from robot_doc_rag.repositories.tasks import get_task as get_task_record
from robot_doc_rag.schemas.task import TaskCreate, TaskResponse, task_response
from robot_doc_rag.services.task_processing import simulate_processing, task_event_stream

router = APIRouter()
SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: TaskCreate,
    background_tasks: BackgroundTasks,
    session: SessionDep,
) -> TaskResponse:
    if await get_document(session, request.document_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    task = await create_task_record(
        session, document_id=request.document_id, task_type=request.task_type
    )
    factory = async_sessionmaker(session.bind, expire_on_commit=False)
    background_tasks.add_task(simulate_processing, task.id, factory)
    return task_response(task)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: UUID, session: SessionDep) -> TaskResponse:
    task = await get_task_record(session, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task_response(task)


@router.get(
    "/{task_id}/events",
    response_class=StreamingResponse,
    responses={404: {"description": "Task not found"}},
)
async def stream_task_events(
    task_id: UUID,
    request: Request,
    session: SessionDep,
) -> StreamingResponse:
    if await get_task_record(session, task_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return StreamingResponse(
        task_event_stream(
            task_id,
            request.is_disconnected,
            async_sessionmaker(session.bind, expire_on_commit=False),
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
