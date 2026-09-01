from fastapi.testclient import TestClient

from robot_doc_rag.config import settings
from robot_doc_rag.main import app

client = TestClient(app)


def test_upload_pdf_success() -> None:
    content = b"%PDF-1.7\nrobot manual"
    response = client.post(
        "/api/v1/documents",
        files={"file": ("x1_manual.pdf", content, "application/pdf")},
        data={"title": "X1 Manual"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["filename"] == "x1_manual.pdf"
    assert body["title"] == "X1 Manual"
    assert body["size"] == len(content)
    assert body["status"] == "uploaded"
    assert len(list(settings.upload_dir.iterdir())) == 1


def test_upload_markdown_success() -> None:
    response = client.post(
        "/api/v1/documents",
        files={"file": ("notes.md", b"# Robot Notes", "text/markdown")},
    )

    assert response.status_code == 201
    assert response.json()["filename"] == "notes.md"


def test_upload_unsupported_type_returns_415() -> None:
    response = client.post(
        "/api/v1/documents",
        files={"file": ("notes.txt", b"not allowed", "text/plain")},
    )

    assert response.status_code == 415
    assert response.json()["detail"] == "Only .pdf and .md files are supported"
    assert not settings.upload_dir.exists()


def test_upload_too_large_returns_413() -> None:
    content = b"x" * (1024 * 1024 + 1)
    response = client.post(
        "/api/v1/documents",
        files={"file": ("large.pdf", content, "application/pdf")},
    )

    assert response.status_code == 413
    assert list(settings.upload_dir.iterdir()) == []


def test_upload_without_file_returns_422() -> None:
    response = client.post("/api/v1/documents")

    assert response.status_code == 422
