from uuid import UUID, uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from robot_doc_rag.schemas.task import TaskCreate, TaskResponse
from robot_doc_rag.services.memory_store import documents, tasks
from robot_doc_rag.services.task_processing import simulate_processing, task_event_stream

router = APIRouter()


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(request: TaskCreate, background_tasks: BackgroundTasks) -> TaskResponse:
    if request.document_id not in documents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    task = TaskResponse(
        id=uuid4(),
        document_id=request.document_id,
        task_type=request.task_type,
        status="pending",
        progress=0,
    )
    tasks[task.id] = task
    background_tasks.add_task(simulate_processing, task.id)
    return task


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: UUID) -> TaskResponse:
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@router.get(
    "/{task_id}/events",
    response_class=StreamingResponse,
    responses={404: {"description": "Task not found"}},
)
async def stream_task_events(task_id: UUID, request: Request) -> StreamingResponse:
    if task_id not in tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return StreamingResponse(
        task_event_stream(task_id, request.is_disconnected),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
