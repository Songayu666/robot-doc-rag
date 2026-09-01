from uuid import uuid4

from fastapi.testclient import TestClient

from robot_doc_rag.main import app

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
    assert get_response.json() == task


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
