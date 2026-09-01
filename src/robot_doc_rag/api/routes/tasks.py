from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status

from robot_doc_rag.schemas.task import TaskCreate, TaskResponse
from robot_doc_rag.services.memory_store import documents, tasks

router = APIRouter()


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(request: TaskCreate) -> TaskResponse:
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
