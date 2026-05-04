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
    exclude_question_ids: list[int] | None = None,
) -> list[GameplayQuestion]:
    teacher_ids = [teacher_id for teacher_id in (teacher_ids or []) if teacher_id is not None]
    exclude_question_ids = [question_id for question_id in (exclude_question_ids or []) if question_id > 0]
    normalized_subject = subject.lower()
    limit = max(1, min(count, 20))

    def _pick(base_query):
        query = base_query
        if exclude_question_ids:
            unseen = query.filter(~GameplayQuestion.id.in_(exclude_question_ids)).order_by(func.random()).limit(limit).all()
            if unseen:
                return unseen
        return query.order_by(func.random()).limit(limit).all()

    if teacher_ids:
        teacher_owned = _pick(
            db.query(GameplayQuestion).filter(
                GameplayQuestion.teacher_id.in_(teacher_ids),
                GameplayQuestion.grade == grade,
                GameplayQuestion.subject == normalized_subject,
                GameplayQuestion.active.is_(True),
            )
        )
        if teacher_owned:
            return teacher_owned

    return _pick(
        db.query(GameplayQuestion)
        .filter(
            GameplayQuestion.teacher_id.is_(None),
            GameplayQuestion.grade == grade,
            GameplayQuestion.subject == normalized_subject,
            GameplayQuestion.active.is_(True),
        )
    )


def check_answer(correct_index: int, selected_index: int) -> bool:
    return int(selected_index) == int(correct_index)
