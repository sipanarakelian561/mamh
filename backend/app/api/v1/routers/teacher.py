import secrets
import string

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.deps.auth import require_teacher
from app.db.session import get_db
from app.models.assignment import Assignment
from app.models.assignment_completion import AssignmentCompletion
from app.models.quiz_completion import QuizCompletion
from app.models.classroom import Classroom
from app.models.classroom_membership import ClassroomMembership
from app.models.progress import StudentProgress
from app.models.quiz import Quiz, QuizQuestion
from app.models.user import User
from app.schemas.assignment import AssignmentCreate
from app.schemas.classroom import ClassroomCreate
from app.schemas.quiz import QuizCreate

router = APIRouter(prefix="/teacher", tags=["teacher"])


def _generate_join_code(db: Session) -> str:
    alphabet = string.ascii_uppercase + string.digits
    for _ in range(10):
        code = "".join(secrets.choice(alphabet) for _ in range(8))
        if not db.query(Classroom).filter(Classroom.join_code == code).first():
            return code
    raise RuntimeError("Could not generate a unique classroom code")


def _get_teacher_classroom(db: Session, teacher_id: int, classroom_id: int) -> Classroom:
    classroom = (
        db.query(Classroom)
        .filter(Classroom.id == classroom_id, Classroom.teacher_id == teacher_id)
        .first()
    )
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    return classroom


@router.get("/students/progress")
def all_student_progress(
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    rows = (
        db.query(StudentProgress)
        .join(ClassroomMembership, ClassroomMembership.student_id == StudentProgress.student_id)
        .join(Classroom, Classroom.id == ClassroomMembership.classroom_id)
        .filter(Classroom.teacher_id == teacher.id)
        .distinct()
        .all()
    )
    return [
        {
            "student_id": r.student_id,
            "xp": r.xp,
            "level": r.level,
            "problems_solved": r.problems_solved,
        }
        for r in rows
    ]


@router.post("/classrooms")
def create_classroom(
    payload: ClassroomCreate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    classroom = Classroom(
        teacher_id=teacher.id,
        name=payload.name,
        grade=payload.grade,
        subject=payload.subject,
        join_code=_generate_join_code(db),
    )
    db.add(classroom)
    db.commit()
    db.refresh(classroom)
    return {
        "id": classroom.id,
        "name": classroom.name,
        "grade": classroom.grade,
        "subject": classroom.subject,
        "join_code": classroom.join_code,
        "created_at": classroom.created_at,
        "members": [],
    }


@router.get("/classrooms")
def list_classrooms(
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    classrooms = (
        db.query(Classroom)
        .filter(Classroom.teacher_id == teacher.id)
        .order_by(Classroom.created_at.desc())
        .all()
    )

    out = []
    for classroom in classrooms:
        memberships = (
            db.query(ClassroomMembership)
            .filter(ClassroomMembership.classroom_id == classroom.id)
            .order_by(ClassroomMembership.joined_at.desc())
            .all()
        )

        members = []
        for m in memberships:
            progress = (
                db.query(StudentProgress)
                .filter(StudentProgress.student_id == m.student_id)
                .first()
            )

            completed_assignments = (
                db.query(Assignment)
                .join(AssignmentCompletion, AssignmentCompletion.assignment_id == Assignment.id)
                .filter(
                    AssignmentCompletion.student_id == m.student_id,
                    Assignment.classroom_id == classroom.id,
                )
                .order_by(AssignmentCompletion.completed_at.desc())
                .all()
            )

            completed_quizzes = (
                db.query(Quiz, QuizCompletion)
                .join(QuizCompletion, QuizCompletion.quiz_id == Quiz.id)
                .filter(
                    QuizCompletion.student_id == m.student_id,
                    Quiz.classroom_id == classroom.id,
                )
                .order_by(QuizCompletion.completed_at.desc())
                .all()
            )

            members.append(
                {
                    "student_id": m.student_id,
                    "first_name": m.first_name,
                    "last_name": m.last_name,
                    "email": m.email,
                    "joined_at": m.joined_at,
                    "progress": {
                        "xp": progress.xp if progress else 0,
                        "level": progress.level if progress else 1,
                        "problems_solved": progress.problems_solved if progress else 0,
                    },
                    "completed_assignments_count": len(completed_assignments),
                    "completed_assignments": [
                        {
                            "id": assignment.id,
                            "title": assignment.title,
                        }
                        for assignment in completed_assignments
                    ],
                    "completed_quizzes_count": len(completed_quizzes),
                    "completed_quizzes": [
                        {
                            "id": quiz.id,
                            "title": quiz.title,
                            "correct_count": completion.correct_count,
                            "total_questions": completion.total_questions,
                            "completed_at": completion.completed_at,
                        }
                        for quiz, completion in completed_quizzes
                    ],
                }
            )

        out.append(
            {
                "id": classroom.id,
                "name": classroom.name,
                "grade": classroom.grade,
                "subject": classroom.subject,
                "join_code": classroom.join_code,
                "created_at": classroom.created_at,
                "members": members,
            }
        )

    return out


@router.post("/assignments")
def create_assignment(
    payload: AssignmentCreate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    classroom = _get_teacher_classroom(db, teacher.id, payload.classroom_id)

    assignment = Assignment(
        teacher_id=teacher.id,
        classroom_id=classroom.id,
        grade=classroom.grade,
        subject=classroom.subject,
        title=payload.title,
        content=payload.content,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return {
        "id": assignment.id,
        "classroom_id": assignment.classroom_id,
        "classroom_name": classroom.name,
        "grade": assignment.grade,
        "subject": assignment.subject,
        "title": assignment.title,
        "content": assignment.content,
        "created_at": assignment.created_at,
    }


@router.get("/assignments")
def list_teacher_assignments(
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    assignments = (
        db.query(Assignment)
        .filter(Assignment.teacher_id == teacher.id)
        .order_by(Assignment.created_at.desc())
        .all()
    )

    classroom_names = {
        c.id: c.name
        for c in db.query(Classroom).filter(Classroom.teacher_id == teacher.id).all()
    }

    return [
        {
            "id": a.id,
            "classroom_id": a.classroom_id,
            "classroom_name": classroom_names.get(a.classroom_id, "Unknown Classroom"),
            "grade": a.grade,
            "subject": a.subject,
            "title": a.title,
            "content": a.content,
            "created_at": a.created_at,
        }
        for a in assignments
    ]


@router.post("/quizzes")
def create_quiz(
    payload: QuizCreate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    classroom = _get_teacher_classroom(db, teacher.id, payload.classroom_id)

    quiz = Quiz(
        teacher_id=teacher.id,
        classroom_id=classroom.id,
        grade=classroom.grade,
        subject=classroom.subject,
        title=payload.title,
    )
    db.add(quiz)
    db.flush()

    for idx, question in enumerate(payload.questions, start=1):
        db.add(
            QuizQuestion(
                quiz_id=quiz.id,
                order_index=idx,
                prompt=question.prompt,
                answer=(question.answer or "").strip(),
            )
        )

    db.commit()
    db.refresh(quiz)

    questions = (
        db.query(QuizQuestion)
        .filter(QuizQuestion.quiz_id == quiz.id)
        .order_by(QuizQuestion.order_index.asc())
        .all()
    )

    return {
        "id": quiz.id,
        "classroom_id": quiz.classroom_id,
        "classroom_name": classroom.name,
        "grade": quiz.grade,
        "subject": quiz.subject,
        "title": quiz.title,
        "created_at": quiz.created_at,
        "questions": [
            {
                "id": q.id,
                "order_index": q.order_index,
                "prompt": q.prompt,
                "answer": q.answer,
            }
            for q in questions
        ],
    }


@router.get("/quizzes")
def list_teacher_quizzes(
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    quizzes = (
        db.query(Quiz)
        .filter(Quiz.teacher_id == teacher.id)
        .order_by(Quiz.created_at.desc())
        .all()
    )

    classroom_names = {
        c.id: c.name
        for c in db.query(Classroom).filter(Classroom.teacher_id == teacher.id).all()
    }

    out = []
    for quiz in quizzes:
        questions = (
            db.query(QuizQuestion)
            .filter(QuizQuestion.quiz_id == quiz.id)
            .order_by(QuizQuestion.order_index.asc())
            .all()
        )
        out.append(
            {
                "id": quiz.id,
                "classroom_id": quiz.classroom_id,
                "classroom_name": classroom_names.get(quiz.classroom_id, "Unknown Classroom"),
                "grade": quiz.grade,
                "subject": quiz.subject,
                "title": quiz.title,
                "created_at": quiz.created_at,
                "questions": [
                    {
                        "id": q.id,
                        "order_index": q.order_index,
                        "prompt": q.prompt,
                        "answer": q.answer,
                    }
                    for q in questions
                ],
            }
        )

    return out
