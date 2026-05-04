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
from app.models.questions import GameplayQuestion
from app.models.quiz import Quiz, QuizQuestion
from app.models.user import User
from app.schemas.assignment import AssignmentCreate
from app.schemas.classroom import ClassroomCreate
from app.schemas.question_bank import QuestionBankCreate, QuestionBankUpdate
from app.schemas.quiz import QuizCreate
from app.services.progress_service import build_progress_snapshot

router = APIRouter(prefix="/teacher", tags=["teacher"])


def _question_bank_out(question: GameplayQuestion) -> dict:
    return {
        "id": question.id,
        "teacher_id": question.teacher_id,
        "grade": question.grade,
        "subject": question.subject,
        "difficulty": question.difficulty,
        "prompt": question.prompt,
        "answers": [
            question.answer_a,
            question.answer_b,
            question.answer_c,
            question.answer_d,
        ],
        "correct_index": question.correct_index,
        "active": question.active,
    }


def _quiz_question_out(question: QuizQuestion) -> dict:
    answers = [question.answer_a, question.answer_b, question.answer_c, question.answer_d]
    return {
        "id": question.id,
        "order_index": question.order_index,
        "prompt": question.prompt,
        "answers": answers,
        "correct_index": question.correct_index,
    }


def _bootstrap_teacher_question_bank(db: Session, teacher: User) -> None:
    taught_pairs = {
        (classroom.grade, classroom.subject.lower())
        for classroom in db.query(Classroom).filter(Classroom.teacher_id == teacher.id).all()
    }
    if not taught_pairs:
        return

    for grade, subject in taught_pairs:
        existing = (
            db.query(GameplayQuestion.id)
            .filter(
                GameplayQuestion.teacher_id == teacher.id,
                GameplayQuestion.grade == grade,
                GameplayQuestion.subject == subject,
            )
            .first()
        )
        if existing:
            continue

        defaults = (
            db.query(GameplayQuestion)
            .filter(
                GameplayQuestion.teacher_id.is_(None),
                GameplayQuestion.grade == grade,
                GameplayQuestion.subject == subject,
            )
            .all()
        )
        for default in defaults:
            db.add(
                GameplayQuestion(
                    teacher_id=teacher.id,
                    grade=default.grade,
                    subject=default.subject,
                    difficulty=default.difficulty,
                    prompt=default.prompt,
                    answer_a=default.answer_a,
                    answer_b=default.answer_b,
                    answer_c=default.answer_c,
                    answer_d=default.answer_d,
                    correct_index=default.correct_index,
                    active=default.active,
                )
            )
    db.commit()


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
        db.query(User)
        .join(ClassroomMembership, ClassroomMembership.student_id == User.id)
        .join(Classroom, Classroom.id == ClassroomMembership.classroom_id)
        .filter(Classroom.teacher_id == teacher.id, User.role == "student")
        .distinct()
        .all()
    )
    return [
        {
            "student_id": snapshot.student_id,
            "xp": snapshot.total_xp,
            "level": snapshot.current_level,
            "total_xp": snapshot.total_xp,
            "currency_balance": snapshot.currency_balance,
            "current_level": snapshot.current_level,
            "xp_to_next_level": snapshot.xp_to_next_level,
            "xp_progress_percentage": snapshot.xp_progress_percentage,
            "problems_solved": snapshot.problems_solved,
            "grade_level": snapshot.student_grade_level,
        }
        for snapshot in (build_progress_snapshot(db, student.id) for student in rows)
    ]


@router.post("/classrooms")
def create_classroom(
    payload: ClassroomCreate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    if teacher.school_id is None:
        raise HTTPException(status_code=400, detail="Teacher is not assigned to a school")

    classroom = Classroom(
        teacher_id=teacher.id,
        school_id=teacher.school_id,
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
            progress = build_progress_snapshot(db, m.student_id)

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
                    "grade_level": progress.student_grade_level,
                    "joined_at": m.joined_at,
                    "progress": {
                        "xp": progress.total_xp,
                        "total_xp": progress.total_xp,
                        "currency_balance": progress.currency_balance,
                        "level": progress.current_level,
                        "current_level": progress.current_level,
                        "xp_to_next_level": progress.xp_to_next_level,
                        "xp_progress_percentage": progress.xp_progress_percentage,
                        "problems_solved": progress.problems_solved,
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
                answer_a=question.answers[0].strip(),
                answer_b=question.answers[1].strip(),
                answer_c=question.answers[2].strip(),
                answer_d=question.answers[3].strip(),
                correct_index=question.correct_index,
                answer=question.answers[question.correct_index].strip(),
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
            _quiz_question_out(q) for q in questions
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
                    _quiz_question_out(q) for q in questions
                ],
            }
        )

    return out


@router.patch("/quizzes/{quiz_id}")
def update_quiz(
    quiz_id: int,
    payload: QuizCreate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.teacher_id == teacher.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    classroom = _get_teacher_classroom(db, teacher.id, payload.classroom_id)
    quiz.classroom_id = classroom.id
    quiz.grade = classroom.grade
    quiz.subject = classroom.subject
    quiz.title = payload.title

    db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz.id).delete()
    db.flush()

    for idx, question in enumerate(payload.questions, start=1):
        db.add(
            QuizQuestion(
                quiz_id=quiz.id,
                order_index=idx,
                prompt=question.prompt,
                answer_a=question.answers[0].strip(),
                answer_b=question.answers[1].strip(),
                answer_c=question.answers[2].strip(),
                answer_d=question.answers[3].strip(),
                correct_index=question.correct_index,
                answer=question.answers[question.correct_index].strip(),
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
        "questions": [_quiz_question_out(q) for q in questions],
    }


@router.get("/question-bank")
def list_question_bank(
    grade: int | None = None,
    subject: str | None = None,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    _bootstrap_teacher_question_bank(db, teacher)
    query = db.query(GameplayQuestion).filter(GameplayQuestion.teacher_id == teacher.id)
    if grade is not None:
        query = query.filter(GameplayQuestion.grade == grade)
    if subject:
        query = query.filter(GameplayQuestion.subject == subject.lower())
    rows = (
        query.order_by(
            GameplayQuestion.grade.asc(),
            GameplayQuestion.subject.asc(),
            GameplayQuestion.id.desc(),
        ).all()
    )
    return [_question_bank_out(row) for row in rows]


@router.post("/question-bank")
def create_question_bank_question(
    payload: QuestionBankCreate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    question = GameplayQuestion(
        teacher_id=teacher.id,
        grade=payload.grade,
        subject=payload.subject.lower(),
        difficulty=payload.difficulty.lower(),
        prompt=payload.prompt,
        answer_a=payload.answers[0],
        answer_b=payload.answers[1],
        answer_c=payload.answers[2],
        answer_d=payload.answers[3],
        correct_index=payload.correct_index,
        active=payload.active,
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return _question_bank_out(question)


@router.patch("/question-bank/{question_id}")
def update_question_bank_question(
    question_id: int,
    payload: QuestionBankUpdate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    question = (
        db.query(GameplayQuestion)
        .filter(GameplayQuestion.id == question_id, GameplayQuestion.teacher_id == teacher.id)
        .first()
    )
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    if payload.grade is not None:
        question.grade = payload.grade
    if payload.subject is not None:
        question.subject = payload.subject.lower()
    if payload.difficulty is not None:
        question.difficulty = payload.difficulty.lower()
    if payload.prompt is not None:
        question.prompt = payload.prompt
    if payload.answers is not None:
        question.answer_a = payload.answers[0]
        question.answer_b = payload.answers[1]
        question.answer_c = payload.answers[2]
        question.answer_d = payload.answers[3]
    if payload.correct_index is not None:
        question.correct_index = payload.correct_index
    if payload.active is not None:
        question.active = payload.active

    db.commit()
    db.refresh(question)
    return _question_bank_out(question)


@router.delete("/question-bank/{question_id}")
def delete_question_bank_question(
    question_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    question = (
        db.query(GameplayQuestion)
        .filter(GameplayQuestion.id == question_id, GameplayQuestion.teacher_id == teacher.id)
        .first()
    )
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    db.delete(question)
    db.commit()
    return {"deleted": True, "id": question_id}
