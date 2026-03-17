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

def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _run_sqlite_migrations()


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
