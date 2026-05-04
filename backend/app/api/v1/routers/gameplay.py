from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.deps.auth import require_student
from app.db.session import get_db
from app.models.classroom import Classroom
from app.models.classroom_membership import ClassroomMembership
from app.models.questions import GameplayQuestion
from app.models.quiz import Quiz, QuizQuestion
from app.models.user import User
from app.schemas.gameplay import GameResultRequest, GameResultResponse, ProblemRequest, SubmitAnswerRequest
from app.services.economy_service import award_game_placement
from app.services.gameplay_service import check_answer, get_random_questions
from app.services.progress_service import award_for_correct

router = APIRouter(prefix="/game", tags=["gameplay"])


def _teacher_ids_for_student_subject(db: Session, student_id: int, grade_level: int, subject: str) -> list[int]:
    rows = (
        db.query(Classroom.teacher_id)
        .join(ClassroomMembership, ClassroomMembership.classroom_id == Classroom.id)
        .filter(
            ClassroomMembership.student_id == student_id,
            Classroom.grade == grade_level,
            Classroom.subject == subject.lower(),
        )
        .distinct()
        .all()
    )
    return [teacher_id for (teacher_id,) in rows]


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
        teacher_ids=_teacher_ids_for_student_subject(db, student.id, student.grade_level, payload.subject),
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


@router.get("/quiz/{quiz_id}")
def get_quiz_for_gameplay(
    quiz_id: int,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    assigned = (
        db.query(ClassroomMembership.id)
        .filter(
            ClassroomMembership.classroom_id == quiz.classroom_id,
            ClassroomMembership.student_id == student.id,
        )
        .first()
    )
    if not assigned:
        raise HTTPException(status_code=403, detail="Quiz is not assigned to this student")

    questions = (
        db.query(QuizQuestion)
        .filter(QuizQuestion.quiz_id == quiz.id)
        .order_by(QuizQuestion.order_index.asc())
        .all()
    )

    return {
        "id": quiz.id,
        "title": quiz.title,
        "grade": quiz.grade,
        "subject": quiz.subject,
        "questions": [
            {
                "id": q.id,
                "order_index": q.order_index,
                "prompt": q.prompt,
                "answers": [q.answer_a, q.answer_b, q.answer_c, q.answer_d],
            }
            for q in questions
        ],
    }


@router.post("/quiz-answer")
def submit_single_quiz_answer(
    payload: dict,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    quiz_id = int(payload.get("quiz_id", 0))
    question_id = int(payload.get("question_id", 0))
    selected_index = int(payload.get("selected_index", -1))
    if quiz_id < 1 or question_id < 1:
        raise HTTPException(status_code=400, detail="Invalid quiz answer payload")

    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    assigned = (
        db.query(ClassroomMembership.id)
        .filter(
            ClassroomMembership.classroom_id == quiz.classroom_id,
            ClassroomMembership.student_id == student.id,
        )
        .first()
    )
    if not assigned:
        raise HTTPException(status_code=403, detail="Quiz is not assigned to this student")

    question = (
        db.query(QuizQuestion)
        .filter(QuizQuestion.id == question_id, QuizQuestion.quiz_id == quiz.id)
        .first()
    )
    if not question:
        raise HTTPException(status_code=404, detail="Quiz question not found")

    return {"correct": selected_index == int(question.correct_index or -1)}


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
