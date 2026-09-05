from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    title: str | None = None
    size: int = Field(ge=0)
    status: Literal["uploaded"]


def document_response(document: object) -> DocumentResponse:
    return DocumentResponse(
        id=document.id,
        filename=document.original_filename,
        title=document.title,
        size=document.size_bytes,
        status=document.status,
    )
