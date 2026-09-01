from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from robot_doc_rag.config import settings
from robot_doc_rag.schemas.document import DocumentResponse
from robot_doc_rag.services.memory_store import documents

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".md"}
READ_CHUNK_SIZE = 1024 * 1024


def safe_filename(filename: str | None) -> str:
    if not filename:
        return "upload"
    return filename.replace("\\", "/").rsplit("/", maxsplit=1)[-1]


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: Annotated[UploadFile, File(description="PDF or Markdown document")],
    title: Annotated[str | None, Form()] = None,
) -> DocumentResponse:
    original_filename = safe_filename(file.filename)
    extension = Path(original_filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        await file.close()
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only .pdf and .md files are supported",
        )

    document_id = uuid4()
    upload_dir = settings.upload_dir.resolve()
    upload_dir.mkdir(parents=True, exist_ok=True)
    destination = upload_dir / f"{document_id}{extension}"
    maximum_bytes = settings.max_upload_size_mb * 1024 * 1024
    total_size = 0

    try:
        with destination.open("wb") as output:
            while chunk := await file.read(READ_CHUNK_SIZE):
                total_size += len(chunk)
                if total_size > maximum_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                        detail=f"File size exceeds {settings.max_upload_size_mb} MB",
                    )
                output.write(chunk)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await file.close()

    record = DocumentResponse(
        id=document_id,
        filename=original_filename,
        title=title,
        size=total_size,
        status="uploaded",
    )
    documents[document_id] = record
    return record
