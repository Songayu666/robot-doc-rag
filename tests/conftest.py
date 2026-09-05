import asyncio
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from robot_doc_rag import models  # noqa: F401
from robot_doc_rag.config import settings
from robot_doc_rag.db.base import Base
from robot_doc_rag.db.session import get_session
from robot_doc_rag.main import app


@pytest.fixture(autouse=True)
def isolated_state(tmp_path: Path) -> Iterator[async_sessionmaker[AsyncSession]]:
    original_upload_dir = settings.upload_dir
    original_limit = settings.max_upload_size_mb
    original_step_delay = settings.task_step_delay_seconds
    original_poll_interval = settings.task_poll_interval_seconds
    original_heartbeat = settings.sse_heartbeat_seconds
    settings.upload_dir = tmp_path / "uploads"
    settings.max_upload_size_mb = 1
    settings.task_step_delay_seconds = 0.05
    settings.task_poll_interval_seconds = 0.001
    settings.sse_heartbeat_seconds = 0.01

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'test.db'}")
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def create_schema() -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def override_session() -> AsyncIterator[AsyncSession]:
        async with factory() as session:
            yield session

    asyncio.run(create_schema())
    app.dependency_overrides[get_session] = override_session

    yield factory

    app.dependency_overrides.clear()
    asyncio.run(engine.dispose())
    settings.upload_dir = original_upload_dir
    settings.max_upload_size_mb = original_limit
    settings.task_step_delay_seconds = original_step_delay
    settings.task_poll_interval_seconds = original_poll_interval
    settings.sse_heartbeat_seconds = original_heartbeat
