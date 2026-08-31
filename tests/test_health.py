from fastapi.testclient import TestClient

from robot_doc_rag.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Robot Document RAG",
        "version": "0.1.0",
    }
