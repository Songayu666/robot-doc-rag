import asyncio
import json
from uuid import uuid4

from fastapi.testclient import TestClient

from robot_doc_rag.main import app
from robot_doc_rag.schemas.task import TaskResponse
from robot_doc_rag.services.memory_store import tasks
from robot_doc_rag.services.task_processing import simulate_processing, task_event_stream

client = TestClient(app)


def upload_document() -> str:
    response = client.post(
        "/api/v1/documents",
        files={"file": ("manual.pdf", b"%PDF robot manual", "application/pdf")},
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_create_and_get_task() -> None:
    document_id = upload_document()
    create_response = client.post(
        "/api/v1/tasks",
        json={"document_id": document_id, "task_type": "parse"},
    )

    assert create_response.status_code == 201
    task = create_response.json()
    assert task["document_id"] == document_id
    assert task["status"] == "pending"
    assert task["progress"] == 0

    get_response = client.get(f"/api/v1/tasks/{task['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["status"] == "completed"
    assert get_response.json()["progress"] == 100


def test_create_task_for_missing_document_returns_404() -> None:
    response = client.post(
        "/api/v1/tasks",
        json={"document_id": str(uuid4()), "task_type": "parse"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"


def test_get_missing_task_returns_404() -> None:
    response = client.get(f"/api/v1/tasks/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_openapi_contains_day_two_endpoints() -> None:
    schema = client.get("/openapi.json").json()

    assert "/health" in schema["paths"]
    assert "/api/v1/documents" in schema["paths"]
    assert "/api/v1/tasks" in schema["paths"]
    assert "/api/v1/tasks/{task_id}" in schema["paths"]
    assert "/api/v1/tasks/{task_id}/events" in schema["paths"]


def test_completed_task_sse_closes_normally() -> None:
    document_id = upload_document()
    create_response = client.post(
        "/api/v1/tasks",
        json={"document_id": document_id, "task_type": "parse"},
    )
    task_id = create_response.json()["id"]

    response = client.get(f"/api/v1/tasks/{task_id}/events")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "event: progress" in response.text
    assert '"status":"completed"' in response.text
    assert '"progress":100' in response.text


def test_missing_task_sse_returns_404() -> None:
    response = client.get(f"/api/v1/tasks/{uuid4()}/events")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


async def test_event_stream_yields_progress_in_order() -> None:
    task_id = uuid4()
    document_id = uuid4()
    tasks[task_id] = TaskResponse(
        id=task_id,
        document_id=document_id,
        task_type="parse",
        status="pending",
        progress=0,
    )

    async def connected() -> bool:
        return False

    async def collect_progress() -> list[int]:
        observed: list[int] = []
        async for event in task_event_stream(task_id, connected):
            if event.startswith("event: progress"):
                data_line = event.splitlines()[1].removeprefix("data: ")
                observed.append(json.loads(data_line)["progress"])
        return observed

    processor = asyncio.create_task(simulate_processing(task_id))
    first_client = asyncio.create_task(collect_progress())
    second_client = asyncio.create_task(collect_progress())
    first_progress, second_progress = await asyncio.gather(first_client, second_client)
    await processor

    assert first_progress == [0, 10, 30, 50, 70, 100]
    assert second_progress == [0, 10, 30, 50, 70, 100]


async def test_event_stream_stops_when_client_disconnects() -> None:
    task_id = uuid4()
    tasks[task_id] = TaskResponse(
        id=task_id,
        document_id=uuid4(),
        task_type="parse",
        status="pending",
        progress=0,
    )

    async def disconnected() -> bool:
        return True

    events = [event async for event in task_event_stream(task_id, disconnected)]

    assert events == []
