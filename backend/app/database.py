"""
Database bootstrap for the Dentist Voice Agent.

This module wires up:
- a SQLAlchemy engine (SQLite file DB: ./patients.db),
- a Session factory (`SessionLocal`) used to create short-lived sessions,
- two helpers:
* `init_db()` – create tables from ORM metadata (idempotent).
* `get_db()` – FastAPI dependency that yields a session per request and
guarantees it is closed after the request finishes.

SQLite note:
- `check_same_thread=False` is required when the same connection can be used
across different threads (e.g., FastAPI’s default Uvicorn workers). Without it,
SQLite raises "ProgrammingError: SQLite objects created in a thread can only
be used in that same thread".
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

from typing import Optional

from sqlalchemy.engine import Engine

DATABASE_URL = "sqlite:///./patients.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Session factory: autocommit/flush are OFF so you control when data is persisted.
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def _ensure_constraints(target_engine: Engine) -> None:
    """Ensure runtime database constraints that aren't handled by metadata."""

    with target_engine.begin() as connection:
        # SQLite's CREATE UNIQUE INDEX IF NOT EXISTS is idempotent and keeps
        # migrations simple for this prototype environment.
        connection.exec_driver_sql(
            "CREATE UNIQUE INDEX IF NOT EXISTS ix_patients_phone_number ON patients (phone_number)"
        )


def init_db(engine_override: Optional[Engine] = None) -> None:
    """Create database tables if they don't exist and enforce constraints."""

    target_engine = engine_override or engine
    Base.metadata.create_all(bind=target_engine)
    _ensure_constraints(target_engine)


def get_db():
    """FastAPI dependency that provides a database session and ensures it closes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
