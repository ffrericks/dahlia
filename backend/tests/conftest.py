import os
import tempfile

# Point the app at a throwaway data dir BEFORE app/config is imported, so tests
# never touch real data. Must run at import time (pytest loads conftest first).
os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="dahlia-test-")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import SQLModel  # noqa: E402

from app.db import engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def reset_db():
    """Give every test a clean schema."""
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    yield


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client
