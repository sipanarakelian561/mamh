from sqlalchemy import inspect, text

from app.db.session import engine
from app.db.base import Base

from app.models.user import User  # noqa
from app.models.school import School  # noqa
from app.models.progress import StudentProgress  # noqa
from app.models.inventory import InventoryItem  # noqa
from app.models.classroom import Classroom  # noqa
from app.models.classroom_membership import ClassroomMembership  # noqa
from app.models.assignment import Assignment  # noqa
from app.models.assignment_completion import AssignmentCompletion  # noqa
from app.models.quiz import Quiz, QuizQuestion  # noqa
from app.models.quiz_completion import QuizCompletion  # noqa
from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal

def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _run_migrations()
    _ensure_default_school()
    _ensure_admin_user()
    _backfill_school_ids()
    _backfill_total_xp()


def _ensure_admin_user() -> None:
    if not settings.ADMIN_EMAIL or not settings.ADMIN_PASSWORD:
        return

    with SessionLocal() as db:
        existing = db.query(User).filter(User.email == settings.ADMIN_EMAIL.lower()).first()
        if existing:
            if existing.role != "super_admin" or not existing.is_admin or existing.school_id is not None:
                existing.role = "super_admin"
                existing.is_admin = True
                existing.school_id = None
                db.commit()
            return
        user = User(
            email=settings.ADMIN_EMAIL.lower(),
            password_hash=hash_password(settings.ADMIN_PASSWORD),
            role="super_admin",
            is_admin=True,
            must_change_password=True,
            school_id=None,
        )
        db.add(user)
        db.commit()


def _ensure_default_school() -> int:
    with SessionLocal() as db:
        school = db.query(School).order_by(School.id.asc()).first()
        if school:
            return school.id
        school = School(name="Default School")
        db.add(school)
        db.commit()
        db.refresh(school)
        return school.id


def _backfill_school_ids() -> None:
    default_school_id = _ensure_default_school()

    with SessionLocal() as db:
        users = (
            db.query(User)
            .filter(User.role != "super_admin", User.school_id.is_(None))
            .all()
        )
        for user in users:
            user.school_id = default_school_id

        classrooms = db.query(Classroom).filter(Classroom.school_id.is_(None)).all()
        for classroom in classrooms:
            teacher = db.get(User, classroom.teacher_id)
            classroom.school_id = teacher.school_id if teacher and teacher.school_id else default_school_id

        db.commit()


def _column_exists(conn, table_name: str, column_name: str) -> bool:
    return column_name in {column["name"] for column in inspect(conn).get_columns(table_name)}


def _run_migrations() -> None:
    with engine.begin() as conn:
        if _column_exists(conn, "assignments", "classroom_id") is False:
            conn.execute(text("ALTER TABLE assignments ADD COLUMN classroom_id INTEGER"))

        if _column_exists(conn, "quizzes", "classroom_id") is False:
            conn.execute(text("ALTER TABLE quizzes ADD COLUMN classroom_id INTEGER"))

        if _column_exists(conn, "users", "must_change_password") is False:
            conn.execute(text("ALTER TABLE users ADD COLUMN must_change_password BOOLEAN DEFAULT 0"))

        if _column_exists(conn, "users", "school_id") is False:
            conn.execute(text("ALTER TABLE users ADD COLUMN school_id INTEGER"))

        if _column_exists(conn, "classrooms", "school_id") is False:
            conn.execute(text("ALTER TABLE classrooms ADD COLUMN school_id INTEGER"))

        if _column_exists(conn, "users", "total_xp") is False:
            conn.execute(text("ALTER TABLE users ADD COLUMN total_xp INTEGER DEFAULT 0"))

        if _column_exists(conn, "users", "currency_balance") is False:
            conn.execute(text("ALTER TABLE users ADD COLUMN currency_balance INTEGER DEFAULT 0"))


def _backfill_total_xp() -> None:
    with SessionLocal() as db:
        rows = db.execute(
            text(
                """
                SELECT users.id AS user_id, users.total_xp AS total_xp, student_progress.xp AS progress_xp
                FROM users
                LEFT JOIN student_progress ON student_progress.student_id = users.id
                WHERE users.role = 'student'
                """
            )
        ).all()

        for row in rows:
            inferred_total_xp = max(0, row.progress_xp or 0)
            if (row.total_xp or 0) == 0 and inferred_total_xp > 0:
                user = db.get(User, row.user_id)
                if user:
                    user.total_xp = inferred_total_xp

        db.commit()
