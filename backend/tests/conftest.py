from collections.abc import Generator
from pathlib import Path
import sys
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["ALLOW_PUBLIC_REGISTRATION"] = "true"
os.environ["DEBUG"] = "true"

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import main
from app.db.base import Base
from app.db.session import get_db

# Import models so SQLAlchemy metadata includes every table used by routers.
from app.models.assignment import Assignment  # noqa: F401
from app.models.assignment_completion import AssignmentCompletion  # noqa: F401
from app.models.classroom import Classroom  # noqa: F401
from app.models.classroom_membership import ClassroomMembership  # noqa: F401
from app.models.inventory import InventoryItem  # noqa: F401
from app.models.progress import StudentProgress  # noqa: F401
from app.models.quiz import Quiz, QuizQuestion  # noqa: F401
from app.models.user import User  # noqa: F401


@pytest.fixture
def session_factory() -> sessionmaker:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(bind=engine)
    testing_session_factory = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        future=True,
    )

    yield testing_session_factory

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def db_session(session_factory: sessionmaker) -> Generator[Session, None, None]:
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(session_factory: sessionmaker) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    main.app.dependency_overrides[get_db] = override_get_db

    with TestClient(main.app) as test_client:
        yield test_client

    main.app.dependency_overrides.clear()
