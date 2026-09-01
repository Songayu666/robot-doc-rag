from uuid import UUID

from robot_doc_rag.schemas.document import DocumentResponse
from robot_doc_rag.schemas.task import TaskResponse

documents: dict[UUID, DocumentResponse] = {}
tasks: dict[UUID, TaskResponse] = {}


def clear_memory_store() -> None:
    documents.clear()
    tasks.clear()
