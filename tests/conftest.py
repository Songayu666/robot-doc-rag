from collections.abc import Iterator
from pathlib import Path

import pytest

from robot_doc_rag.config import settings
from robot_doc_rag.services.memory_store import clear_memory_store


@pytest.fixture(autouse=True)
def isolated_state(tmp_path: Path) -> Iterator[None]:
    original_upload_dir = settings.upload_dir
    original_limit = settings.max_upload_size_mb
    settings.upload_dir = tmp_path / "uploads"
    settings.max_upload_size_mb = 1
    clear_memory_store()

    yield

    clear_memory_store()
    settings.upload_dir = original_upload_dir
    settings.max_upload_size_mb = original_limit
