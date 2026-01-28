from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.v1.deps.auth import require_student
from app.models.user import User
from app.schemas.gameplay import ProblemRequest, SubmitAnswerRequest
from app.services.gameplay_service import generate_problem, check_answer
from app.services.progress_service import award_for_correct

router = APIRouter(prefix="/game", tags=["gameplay"])

# For local testing: store answers in memory (resets when server restarts)
_problem_answers: dict[str, int] = {}

@router.post("/problems")
def get_problems(payload: ProblemRequest, student: User = Depends(require_student)):
    problems = []
    for _ in range(max(1, min(payload.count, 20))):
        p = generate_problem(payload.grade, payload.difficulty)
        _problem_answers[p["problem_id"]] = p["answer"]
        # send prompt + problem_id only (don’t send correct answer)
        problems.append({"problem_id": p["problem_id"], "prompt": p["prompt"]})
    return {"problems": problems}

@router.post("/submit")
def submit_answer(payload: SubmitAnswerRequest, db: Session = Depends(get_db), student: User = Depends(require_student)):
    if payload.problem_id not in _problem_answers:
        return {"correct": False, "reason": "Unknown problem_id"}

    correct_answer = _problem_answers[payload.problem_id]
    ok = check_answer(correct_answer, payload.answer)

    if ok:
        p = award_for_correct(db, student.id, xp_gain=5)
        return {"correct": True, "xp": p.xp, "level": p.level, "problems_solved": p.problems_solved}

    return {"correct": False}
