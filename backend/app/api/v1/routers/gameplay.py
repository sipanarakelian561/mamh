from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.deps.auth import require_student
from app.db.session import get_db
from app.models.questions import GameplayQuestion
from app.models.user import User
from app.schemas.gameplay import GameResultRequest, GameResultResponse, ProblemRequest, SubmitAnswerRequest
from app.services.economy_service import award_game_placement
from app.services.gameplay_service import check_answer, get_random_questions
from app.services.progress_service import award_for_correct

router = APIRouter(prefix="/game", tags=["gameplay"])


@router.post("/questions")
def get_questions(
    payload: ProblemRequest,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    if student.grade_level is None:
        raise HTTPException(status_code=400, detail="Student grade not assigned")

    questions = get_random_questions(
        db,
        grade=student.grade_level,
        subject=payload.subject,
        count=payload.count,
    )
    if not questions:
        raise HTTPException(status_code=404, detail="No active questions found for this grade and subject")

    return {
        "grade_level": student.grade_level,
        "subject": payload.subject.lower(),
        "questions": [question.to_public_dict() for question in questions],
    }


@router.post("/submit")
def submit_answer(
    payload: SubmitAnswerRequest,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    if student.grade_level is None:
        raise HTTPException(status_code=400, detail="Student grade not assigned")

    question = (
        db.query(GameplayQuestion)
        .filter(
            GameplayQuestion.id == payload.question_id,
            GameplayQuestion.grade == student.grade_level,
            GameplayQuestion.active.is_(True),
        )
        .first()
    )
    if not question:
        raise HTTPException(status_code=404, detail="Question not found for this student")

    ok = check_answer(question.correct_index, payload.selected_index)

    if ok:
        p = award_for_correct(db, student.id, xp_gain=5)
        return {
            "correct": True,
            "xp": p.total_xp,
            "level": p.current_level,
            "total_xp": p.total_xp,
            "currency_balance": p.currency_balance,
            "current_level": p.current_level,
            "xp_to_next_level": p.xp_to_next_level,
            "xp_progress_percentage": p.xp_progress_percentage,
            "problems_solved": p.problems_solved,
            "level_up": p.level_up,
        }

    return {"correct": False}


@router.post("/complete-run", response_model=GameResultResponse)
def complete_run(
    payload: GameResultRequest,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    result = award_game_placement(db, student.id, payload.placement)
    return GameResultResponse(
        student_id=result.student_id,
        placement=result.placement,
        xp_awarded=result.xp_awarded,
        money_awarded=result.money_awarded,
        total_xp=result.total_xp,
        currency_balance=result.currency_balance,
        current_level=result.current_level,
        xp_to_next_level=result.xp_to_next_level,
        xp_progress_percentage=result.xp_progress_percentage,
        level_up=result.level_up,
        problems_solved=result.problems_solved,
    )
