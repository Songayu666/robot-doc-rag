from fastapi import FastAPI

from robot_doc_rag.api.routes import documents, health, tasks
from robot_doc_rag.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="0.1.0")
    app.include_router(health.router)
    app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
    app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
    return app


app = create_app()
