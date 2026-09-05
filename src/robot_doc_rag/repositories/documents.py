from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from robot_doc_rag.models.document import Document


async def create_document(
    session: AsyncSession,
    *,
    document_id: UUID,
    original_filename: str,
    title: str | None,
    stored_filename: str,
    content_type: str,
    size_bytes: int,
) -> Document:
    document = Document(
        id=document_id,
        original_filename=original_filename,
        title=title,
        stored_filename=stored_filename,
        content_type=content_type,
        size_bytes=size_bytes,
        status="uploaded",
    )
    session.add(document)
    await session.commit()
    await session.refresh(document)
    return document


async def get_document(session: AsyncSession, document_id: UUID) -> Document | None:
    return await session.get(Document, document_id)
