from sqlalchemy.orm import Session
from app.models.progress import StudentProgress

def get_or_create_progress(db: Session, student_id: int) -> StudentProgress:
    p = db.query(StudentProgress).filter(StudentProgress.student_id == student_id).first()
    if not p:
        p = StudentProgress(student_id=student_id, xp=0, level=1, problems_solved=0)
        db.add(p)
        db.commit()
        db.refresh(p)
    return p

def award_for_correct(db: Session, student_id: int, xp_gain: int = 5) -> StudentProgress:
    p = get_or_create_progress(db, student_id)
    p.xp += max(0, xp_gain)
    p.problems_solved += 1
    p.level = max(1, (p.xp // 25) + 1)  # example: 25 XP per level
    db.commit()
    db.refresh(p)
    return p
