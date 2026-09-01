# robot-doc-rag

A deployable retrieval-augmented generation service for robot manuals and technical documents.

## Current milestone

Day 2 provides a tested FastAPI foundation with:

- health check
- PDF and Markdown uploads
- 20 MB upload limit
- UUID-based stored filenames
- in-memory task creation and lookup
- generated OpenAPI documentation

PostgreSQL persistence will replace the in-memory store in a later milestone.

## Local setup

```powershell
uv sync --locked
Copy-Item .env.example .env
uv run uvicorn robot_doc_rag.main:app --reload
```

Open <http://127.0.0.1:8000/docs> to use the interactive API documentation.

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
