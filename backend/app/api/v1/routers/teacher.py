from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.v1.deps.auth import require_teacher
from app.models.user import User
from app.models.progress import StudentProgress

router = APIRouter(prefix="/teacher", tags=["teacher"])

@router.get("/students/progress")
def all_student_progress(db: Session = Depends(get_db), teacher: User = Depends(require_teacher)):
    rows = db.query(StudentProgress).all()
    return [{"student_id": r.student_id, "xp": r.xp, "level": r.level, "problems_solved": r.problems_solved} for r in rows]
