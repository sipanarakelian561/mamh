from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.questions import GameplayQuestion


def get_random_questions(
    db: Session,
    *,
    grade: int,
    subject: str,
    count: int,
    teacher_ids: list[int] | None = None,
) -> list[GameplayQuestion]:
    teacher_ids = [teacher_id for teacher_id in (teacher_ids or []) if teacher_id is not None]

    if teacher_ids:
        teacher_owned = (
            db.query(GameplayQuestion)
            .filter(
                GameplayQuestion.teacher_id.in_(teacher_ids),
                GameplayQuestion.grade == grade,
                GameplayQuestion.subject == subject.lower(),
                GameplayQuestion.active.is_(True),
            )
            .order_by(func.random())
            .limit(max(1, min(count, 20)))
            .all()
        )
        if teacher_owned:
            return teacher_owned

    return (
        db.query(GameplayQuestion)
        .filter(
            GameplayQuestion.teacher_id.is_(None),
            GameplayQuestion.grade == grade,
            GameplayQuestion.subject == subject.lower(),
            GameplayQuestion.active.is_(True),
        )
        .order_by(func.random())
        .limit(max(1, min(count, 20)))
        .all()
    )


def check_answer(correct_index: int, selected_index: int) -> bool:
    return int(selected_index) == int(correct_index)
