"""Create a demo document and task, then print its SSE progress events."""

import httpx

BASE_URL = "http://127.0.0.1:8000"


def main() -> None:
    with httpx.Client(base_url=BASE_URL, timeout=30) as client:
        document_response = client.post(
            "/api/v1/documents",
            files={"file": ("demo.md", b"# Robot manual\n\nDemo content.", "text/markdown")},
            data={"title": "SSE demo"},
        )
        document_response.raise_for_status()
        document_id = document_response.json()["id"]

        task_response = client.post(
            "/api/v1/tasks",
            json={"document_id": document_id, "task_type": "parse"},
        )
        task_response.raise_for_status()
        task_id = task_response.json()["id"]
        print(f"Task created: {task_id}")

        with client.stream("GET", f"/api/v1/tasks/{task_id}/events") as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    print(line)


if __name__ == "__main__":
    main()
