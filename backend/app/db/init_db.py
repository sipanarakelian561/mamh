from sqlalchemy import text

from app.db.session import engine
from app.db.base import Base

from app.models.user import User  # noqa
from app.models.progress import StudentProgress  # noqa
from app.models.inventory import InventoryItem  # noqa
from app.models.classroom import Classroom  # noqa
from app.models.classroom_membership import ClassroomMembership  # noqa
from app.models.assignment import Assignment  # noqa
from app.models.assignment_completion import AssignmentCompletion  # noqa
from app.models.quiz import Quiz, QuizQuestion  # noqa
from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal

def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _run_sqlite_migrations()
    _ensure_admin_user()


def _ensure_admin_user() -> None:
    if not settings.ADMIN_EMAIL or not settings.ADMIN_PASSWORD:
        return

    with SessionLocal() as db:
        existing = db.query(User).filter(User.email == settings.ADMIN_EMAIL.lower()).first()
        if existing:
            return
        user = User(
            email=settings.ADMIN_EMAIL.lower(),
            password_hash=hash_password(settings.ADMIN_PASSWORD),
            role="admin",
            is_admin=True,
        )
        db.add(user)
        db.commit()


def _column_exists(conn, table_name: str, column_name: str) -> bool:
    rows = conn.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
    return any(row[1] == column_name for row in rows)


def _run_sqlite_migrations() -> None:
    if not str(engine.url).startswith("sqlite"):
        return

    with engine.begin() as conn:
        if _column_exists(conn, "assignments", "classroom_id") is False:
            conn.execute(text("ALTER TABLE assignments ADD COLUMN classroom_id INTEGER"))

        if _column_exists(conn, "quizzes", "classroom_id") is False:
            conn.execute(text("ALTER TABLE quizzes ADD COLUMN classroom_id INTEGER"))

        if _column_exists(conn, "users", "must_change_password") is False:
            conn.execute(text("ALTER TABLE users ADD COLUMN must_change_password BOOLEAN DEFAULT 0"))
