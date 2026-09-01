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
