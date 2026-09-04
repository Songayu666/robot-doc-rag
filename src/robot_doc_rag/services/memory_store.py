from uuid import UUID

from robot_doc_rag.schemas.document import DocumentResponse
from robot_doc_rag.schemas.task import TaskResponse

documents: dict[UUID, DocumentResponse] = {}
tasks: dict[UUID, TaskResponse] = {}


def update_task(task_id: UUID, *, status: str, progress: int) -> TaskResponse | None:
    current = tasks.get(task_id)
    if current is None:
        return None

    updated = current.model_copy(update={"status": status, "progress": progress})
    tasks[task_id] = updated
    return updated


def clear_memory_store() -> None:
    documents.clear()
    tasks.clear()
