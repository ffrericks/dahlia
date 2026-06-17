from collections.abc import Iterator
from datetime import date

from sqlmodel import Session, SQLModel, create_engine, select

from .config import settings

# check_same_thread=False: SQLite + FastAPI's threaded request handling need this.
engine = create_engine(
    settings.database_url,
    echo=False,
    connect_args={"check_same_thread": False},
)


# Columns added to existing tables after their first release. SQLite can ADD COLUMN
# in place, so existing databases upgrade without losing data.
_ADDED_COLUMNS = {
    "logentry": [("fertilized", "BOOLEAN NOT NULL DEFAULT 0")],
    "plant": [("created_on", "DATE")],
}


def _ensure_columns() -> None:
    """Add any missing columns to existing tables (additive, non-destructive)."""
    with engine.begin() as conn:
        for table, columns in _ADDED_COLUMNS.items():
            info = list(conn.exec_driver_sql(f"PRAGMA table_info({table})"))
            if not info:
                continue  # fresh DB: create_all already made the table with all columns
            existing = {row[1] for row in info}
            for name, ddl in columns:
                if name not in existing:
                    conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}")


def _backfill_created_on() -> None:
    """Give existing plants a created_on from their earliest event (or today)."""
    from .models import LogEntry, Plant, Planting

    with Session(engine) as session:
        plants = session.exec(select(Plant).where(Plant.created_on.is_(None))).all()
        if not plants:
            return
        for plant in plants:
            dates = list(
                session.exec(
                    select(Planting.planted_on).where(Planting.plant_id == plant.id)
                ).all()
            ) + list(
                session.exec(
                    select(LogEntry.entry_date).where(LogEntry.plant_id == plant.id)
                ).all()
            )
            plant.created_on = min(dates) if dates else date.today()
            session.add(plant)
        session.commit()


def init_db() -> None:
    """Create the data folders and any tables defined by SQLModel models."""
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.photos_dir.mkdir(parents=True, exist_ok=True)
    # Import models so their tables are registered on SQLModel.metadata before create_all.
    from . import models  # noqa: F401

    SQLModel.metadata.create_all(engine)
    _ensure_columns()
    _backfill_created_on()


def get_session() -> Iterator[Session]:
    """FastAPI dependency that yields a database session per request."""
    with Session(engine) as session:
        yield session
