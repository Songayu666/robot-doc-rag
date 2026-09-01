from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    title: str | None = None
    size: int = Field(ge=0)
    status: Literal["uploaded"]
