from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    document_id: UUID
    task_type: Literal["parse"]


class TaskResponse(BaseModel):
    id: UUID
    document_id: UUID
    task_type: Literal["parse"]
    status: Literal["pending", "running", "completed", "failed"]
    progress: int = Field(ge=0, le=100)


def task_response(task: object) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        document_id=task.document_id,
        task_type=task.task_type,
        status=task.status,
        progress=task.progress,
    )
