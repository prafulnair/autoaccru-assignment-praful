from __future__ import annotations

from collections.abc import Generator
import os
import sys
import types

import pytest
from fastapi.testclient import TestClient
from fastapi.dependencies import utils as deps_utils
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("GEMINI_API_KEY", "test-key")

if "google.generativeai" not in sys.modules:
    google_module = types.ModuleType("google")
    genai_module = types.ModuleType("google.generativeai")

    class _StubModel:
        def __init__(self, *args, **kwargs):
            pass

        def generate_content(self, *args, **kwargs):
            raise RuntimeError("Gemini model is stubbed for tests")

    def _configure(**kwargs):
        return None

    genai_module.GenerativeModel = _StubModel
    genai_module.configure = _configure
    google_module.generativeai = genai_module

    sys.modules["google"] = google_module
    sys.modules["google.generativeai"] = genai_module

deps_utils.ensure_multipart_is_installed = lambda: None  # type: ignore

from app.database import Base, get_db, init_db
from app.main import app


@pytest.fixture(scope="session")
def engine() -> Generator:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    init_db(engine_override=engine)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture(scope="session")
def session_factory(engine) -> sessionmaker:
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture()
def db_session(session_factory) -> Generator[Session, None, None]:
    session = session_factory()
    try:
        yield session
    finally:
        session.rollback()
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
        session.close()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_db, None)
