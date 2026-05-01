from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.questions import GameplayQuestion


def get_random_questions(
    db: Session,
    *,
    grade: int,
    subject: str,
    count: int,
) -> list[GameplayQuestion]:
    return (
        db.query(GameplayQuestion)
        .filter(
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
