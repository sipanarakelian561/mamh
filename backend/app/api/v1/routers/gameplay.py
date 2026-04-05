from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps.auth import require_student
from app.db.session import get_db
from app.models.user import User
from app.schemas.gameplay import ProblemRequest, SubmitAnswerRequest
from app.services.gameplay_service import generate_problem, check_answer
from app.services.progress_service import award_for_correct

router = APIRouter(prefix="/game", tags=["gameplay"])

_PROBLEM_TTL_MINUTES = 10
# {student_id: {problem_id: (answer, expires_at)}}
_problem_answers: dict[int, dict[str, tuple[int, datetime]]] = {}


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
        return {"correct": True, "xp": p.xp, "level": p.level, "problems_solved": p.problems_solved}

    return {"correct": False}
