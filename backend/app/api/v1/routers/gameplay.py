from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps.auth import require_student
from app.db.session import get_db
from app.models.user import User
from app.schemas.gameplay import GameResultRequest, GameResultResponse, ProblemRequest, SubmitAnswerRequest
from app.services.economy_service import award_game_placement
from app.services.gameplay_service import generate_problem, check_answer
from app.services.progress_service import award_for_correct

router = APIRouter(prefix="/game", tags=["gameplay"])

_PROBLEM_TTL_MINUTES = 10
# {student_id: {problem_id: (answer, expires_at)}}
_problem_answers: dict[int, dict[str, tuple[int, datetime]]] = {}
_LOCAL_QUIZ = {
    "quiz_id": "local-math-1",
    "title": "Local Math Warmup",
    "questions": [
        {
            "id": 1,
            "prompt": "What is 2 + 2?",
            "answers": ["1", "4", "5", "12"],
            "correct_index": 1,
        },
        {
            "id": 2,
            "prompt": "What is 5 x 3?",
            "answers": ["8", "12", "15", "20"],
            "correct_index": 2,
        },
        {
            "id": 3,
            "prompt": "What is 10 - 7?",
            "answers": ["2", "3", "4", "5"],
            "correct_index": 1,
        },
        {
            "id": 4,
            "prompt": "What is 9 / 3?",
            "answers": ["2", "3", "6", "1"],
            "correct_index": 1,
        },
        {
            "id": 5,
            "prompt": "What is 6 + 7?",
            "answers": ["11", "14", "13", "12"],
            "correct_index": 2,
        },
    ],
}


def _purge_expired(student_id: int) -> None:
    now = datetime.now(timezone.utc)
    student_map = _problem_answers.get(student_id)
    if not student_map:
        return
    expired = [pid for pid, (_, exp) in student_map.items() if exp <= now]
    for pid in expired:
        student_map.pop(pid, None)
    if not student_map:
        _problem_answers.pop(student_id, None)


@router.get("/local-quiz")
def get_local_quiz():
    return _LOCAL_QUIZ


@router.post("/problems")
def get_problems(payload: ProblemRequest, student: User = Depends(require_student)):
    _purge_expired(student.id)
    student_map = _problem_answers.setdefault(student.id, {})

    problems = []
    for _ in range(max(1, min(payload.count, 20))):
        p = generate_problem(payload.grade, payload.difficulty)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=_PROBLEM_TTL_MINUTES)
        student_map[p["problem_id"]] = (p["answer"], expires_at)
        problems.append({"problem_id": p["problem_id"], "prompt": p["prompt"]})
    return {"problems": problems}


@router.post("/submit")
def submit_answer(
    payload: SubmitAnswerRequest,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    _purge_expired(student.id)
    student_map = _problem_answers.get(student.id, {})
    record = student_map.get(payload.problem_id)
    if not record:
        return {"correct": False, "reason": "Unknown or expired problem_id"}

    correct_answer, _expires_at = record
    ok = check_answer(correct_answer, payload.answer)

    if ok:
        student_map.pop(payload.problem_id, None)
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
