# robot-doc-rag

A deployable retrieval-augmented generation service for robot manuals and technical documents.

## Current milestone

Day 3 provides a tested FastAPI foundation with:

- health check
- PDF and Markdown uploads
- 20 MB upload limit
- UUID-based stored filenames
- in-memory task creation and lookup
- simulated asynchronous task progress
- Server-Sent Events (SSE) progress streaming
- disconnect detection and heartbeat support
- generated OpenAPI documentation

PostgreSQL persistence will replace the in-memory store in a later milestone.

## Local setup

```powershell
uv sync --locked
Copy-Item .env.example .env
uv run uvicorn robot_doc_rag.main:app --reload
```

Open <http://127.0.0.1:8000/docs> to use the interactive API documentation.

For the easiest end-to-end demo, keep the server running and use a second terminal:

```powershell
uv run python scripts/demo_sse.py
```

The script uploads a small Markdown document, creates a task, and immediately prints each SSE
event. You can also connect manually (replace `<TASK_ID>`):

```powershell
curl.exe -N http://127.0.0.1:8000/api/v1/tasks/<TASK_ID>/events
```

## Quality checks

```powershell
uv run ruff check .
uv run ruff format --check .
uv run pytest -v
```

## Planned stack

- Python 3.12
- FastAPI and Pydantic
- PostgreSQL and pgvector
- Redis
- Docker Compose
- pytest

## License

MIT
