from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

from .config import settings

# check_same_thread=False: SQLite + FastAPI's threaded request handling need this.
engine = create_engine(
    settings.database_url,
    echo=False,
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    """Create the data folders and any tables defined by SQLModel models."""
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.photos_dir.mkdir(parents=True, exist_ok=True)
    # Import models so their tables are registered on SQLModel.metadata before create_all.
    from . import models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    """FastAPI dependency that yields a database session per request."""
    with Session(engine) as session:
        yield session
