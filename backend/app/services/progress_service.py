from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.progress import StudentProgress
from app.models.user import User

FIRST_PLACE_XP = 15
SECOND_PLACE_XP = 5
THIRD_PLACE_XP = 1
QUIZ_COMPLETION_XP = 15


@dataclass
class XPUpdateResult:
    student_id: int
    student_grade_level: int | None
    total_xp: int
    currency_balance: int
    current_level: int
    xp_to_next_level: int
    xp_progress_percentage: float
    level_up: bool
    problems_solved: int


def get_or_create_progress(db: Session, student_id: int) -> StudentProgress:
    progress = db.query(StudentProgress).filter(StudentProgress.student_id == student_id).first()
    if not progress:
        progress = StudentProgress(student_id=student_id, xp=0, level=1, problems_solved=0)
        db.add(progress)
        db.flush()
    return progress


def get_student_or_404(db: Session, student_id: int) -> User:
    student = db.get(User, student_id)
    if not student or student.role != "student":
        raise ValueError("Student not found")
    return student


def build_progress_snapshot(db: Session, student_id: int) -> XPUpdateResult:
    student = get_student_or_404(db, student_id)
    progress = get_or_create_progress(db, student_id)
    return XPUpdateResult(
        student_id=student.id,
        student_grade_level=student.grade_level,
        total_xp=max(0, student.total_xp),
        currency_balance=max(0, student.currency_balance),
        current_level=student.current_level,
        xp_to_next_level=student.xp_to_next_level,
        xp_progress_percentage=student.xp_progress_percentage,
        level_up=False,
        problems_solved=progress.problems_solved,
    )


def add_xp(
    db: Session,
    student_id: int,
    amount: int,
    *,
    increment_problems_solved: bool = False,
    money_amount: int = 0,
) -> XPUpdateResult:
    if amount < 0:
        raise ValueError("XP amount must be non-negative")
    if money_amount < 0:
        raise ValueError("Money amount must be non-negative")

    student = get_student_or_404(db, student_id)
    progress = get_or_create_progress(db, student_id)
    previous_level = student.current_level

    student.total_xp = max(0, student.total_xp) + amount
    student.currency_balance = max(0, student.currency_balance) + money_amount
    progress.xp = student.total_xp
    progress.level = student.current_level
    if increment_problems_solved:
        progress.problems_solved += 1

    db.add(student)
    db.add(progress)
    db.commit()
    db.refresh(student)
    db.refresh(progress)

    return XPUpdateResult(
        student_id=student.id,
        student_grade_level=student.grade_level,
        total_xp=student.total_xp,
        currency_balance=student.currency_balance,
        current_level=student.current_level,
        xp_to_next_level=student.xp_to_next_level,
        xp_progress_percentage=student.xp_progress_percentage,
        level_up=student.current_level > previous_level,
        problems_solved=progress.problems_solved,
    )


def award_for_correct(db: Session, student_id: int, xp_gain: int = 5) -> XPUpdateResult:
    return add_xp(db, student_id, max(0, xp_gain), increment_problems_solved=True)
