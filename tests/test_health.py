from fastapi.testclient import TestClient

from robot_doc_rag.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "robot-doc-rag",
        "version": "0.1.0",
    }
