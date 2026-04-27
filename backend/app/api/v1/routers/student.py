from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.deps.auth import require_student
from app.db.session import get_db
from app.models.assignment import Assignment
from app.models.assignment_completion import AssignmentCompletion
from app.models.quiz_completion import QuizCompletion
from app.models.classroom import Classroom
from app.models.classroom_membership import ClassroomMembership
from app.models.quiz import Quiz, QuizQuestion
from app.models.user import User
from app.schemas.classroom import ClassroomJoinRequest
from app.schemas.inventory import ItemAdd, ItemEquip, ItemPurchase, ItemPurchaseOut, ShopItemOut
from app.schemas.progress import ProgressOut
from app.schemas.quiz import QuizSubmitRequest
from app.services.inventory_service import get_shop_catalog, list_items, purchase_item, set_equipped
from app.services.progress_service import QUIZ_COMPLETION_XP, add_xp, build_progress_snapshot

router = APIRouter(prefix="/student", tags=["student"])


def _student_memberships(db: Session, student_id: int) -> list[ClassroomMembership]:
    return (
        db.query(ClassroomMembership)
        .join(Classroom, Classroom.id == ClassroomMembership.classroom_id)
        .filter(ClassroomMembership.student_id == student_id)
        .all()
    )


def _student_classroom_ids(db: Session, student_id: int) -> set[int]:
    return {m.classroom_id for m in _student_memberships(db, student_id)}


@router.get("/progress")
def student_progress(
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    snapshot = build_progress_snapshot(db, student.id)
    return ProgressOut(
        student_id=snapshot.student_id,
        xp=snapshot.total_xp,
        level=snapshot.current_level,
        total_xp=snapshot.total_xp,
        currency_balance=snapshot.currency_balance,
        current_level=snapshot.current_level,
        xp_to_next_level=snapshot.xp_to_next_level,
        xp_progress_percentage=snapshot.xp_progress_percentage,
        problems_solved=snapshot.problems_solved,
    )


@router.post("/classrooms/join")
def join_classroom(
    payload: ClassroomJoinRequest,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    normalized_email = payload.email.strip().lower()
    if normalized_email != student.email.lower():
        raise HTTPException(
            status_code=400,
            detail="Email must match the student account email used to log in",
        )

    classroom = (
        db.query(Classroom)
        .filter(Classroom.join_code == payload.class_code.strip().upper())
        .first()
    )
    if not classroom:
        raise HTTPException(status_code=404, detail="Invalid classroom code")
    if student.school_id is None:
        raise HTTPException(status_code=400, detail="Student is not assigned to a school")
    if classroom.school_id != student.school_id:
        raise HTTPException(status_code=403, detail="Classroom belongs to another school")

    existing = (
        db.query(ClassroomMembership)
        .filter(
            ClassroomMembership.classroom_id == classroom.id,
            ClassroomMembership.student_id == student.id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Student already joined this classroom")

    membership = ClassroomMembership(
        classroom_id=classroom.id,
        student_id=student.id,
        first_name=payload.first_name.strip(),
        last_name=payload.last_name.strip(),
        email=normalized_email,
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)

    return {
        "id": membership.id,
        "classroom_id": classroom.id,
        "classroom_name": classroom.name,
        "grade": classroom.grade,
        "subject": classroom.subject,
    }


@router.get("/classrooms")
def list_joined_classrooms(
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    memberships = (
        db.query(ClassroomMembership)
        .join(Classroom, Classroom.id == ClassroomMembership.classroom_id)
        .filter(ClassroomMembership.student_id == student.id)
        .order_by(ClassroomMembership.joined_at.desc())
        .all()
    )

    return [
        {
            "classroom_id": m.classroom.id,
            "name": m.classroom.name,
            "grade": m.classroom.grade,
            "subject": m.classroom.subject,
            "teacher_id": m.classroom.teacher_id,
            "joined_at": m.joined_at,
            "first_name": m.first_name,
            "last_name": m.last_name,
            "email": m.email,
        }
        for m in memberships
    ]


@router.post("/inventory/add")
def student_add_item(
    payload: ItemAdd,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    raise HTTPException(status_code=403, detail="Direct item grants are disabled. Use the purchase endpoint.")


@router.get("/shop/items", response_model=list[ShopItemOut])
def student_shop_items(
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    return get_shop_catalog(db, student.id)


@router.post("/inventory/purchase", response_model=ItemPurchaseOut)
def student_purchase_item(
    payload: ItemPurchase,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    item, currency_balance = purchase_item(db, student.id, payload.item_id)
    return {
        "id": item.id,
        "item_id": item.item_id,
        "name": item.name,
        "slot": item.slot,
        "equipped": item.equipped,
        "currency_balance": currency_balance,
    }


@router.get("/inventory")
def student_inventory(
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    inv = list_items(db, student.id)
    return [
        {
            "item_id": i.item_id,
            "name": i.name,
            "slot": i.slot,
            "equipped": i.equipped,
        }
        for i in inv
    ]


@router.post("/inventory/equip")
def student_equip(
    payload: ItemEquip,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    item = set_equipped(db, student.id, payload.item_id, payload.equipped)
    return {"item_id": item.item_id, "equipped": item.equipped, "slot": item.slot}


@router.get("/assignments")
def list_assignments(
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    classroom_ids = _student_classroom_ids(db, student.id)
    if not classroom_ids:
        return []

    assignments = (
        db.query(Assignment)
        .filter(Assignment.classroom_id.in_(classroom_ids))
        .order_by(Assignment.created_at.desc())
        .all()
    )

    classroom_map = {
        c.id: c
        for c in db.query(Classroom).filter(Classroom.id.in_(classroom_ids)).all()
    }

    completed_ids = {
        row.assignment_id
        for row in db.query(AssignmentCompletion)
        .filter(AssignmentCompletion.student_id == student.id)
        .all()
    }

    return [
        {
            "id": a.id,
            "classroom_id": a.classroom_id,
            "classroom_name": classroom_map[a.classroom_id].name,
            "grade": a.grade,
            "subject": a.subject,
            "title": a.title,
            "content": a.content,
            "created_at": a.created_at,
            "completed": a.id in completed_ids,
        }
        for a in assignments
    ]


@router.get("/assignments/{assignment_id}")
def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    classroom_ids = _student_classroom_ids(db, student.id)
    if assignment.classroom_id not in classroom_ids:
        raise HTTPException(status_code=403, detail="Assignment is not assigned to this student")

    classroom = db.query(Classroom).filter(Classroom.id == assignment.classroom_id).first()

    completed = (
        db.query(AssignmentCompletion)
        .filter(
            AssignmentCompletion.assignment_id == assignment.id,
            AssignmentCompletion.student_id == student.id,
        )
        .first()
        is not None
    )

    return {
        "id": assignment.id,
        "classroom_id": assignment.classroom_id,
        "classroom_name": classroom.name if classroom else "Unknown Classroom",
        "grade": assignment.grade,
        "subject": assignment.subject,
        "title": assignment.title,
        "content": assignment.content,
        "created_at": assignment.created_at,
        "completed": completed,
    }


@router.post("/assignments/{assignment_id}/complete")
def complete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    classroom_ids = _student_classroom_ids(db, student.id)
    if assignment.classroom_id not in classroom_ids:
        raise HTTPException(status_code=403, detail="Assignment is not assigned to this student")

    existing = (
        db.query(AssignmentCompletion)
        .filter(
            AssignmentCompletion.assignment_id == assignment.id,
            AssignmentCompletion.student_id == student.id,
        )
        .first()
    )

    if not existing:
        db.add(AssignmentCompletion(assignment_id=assignment.id, student_id=student.id))
        db.commit()

    return {"assignment_id": assignment.id, "completed": True}


@router.get("/quizzes")
def list_quizzes(
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    classroom_ids = _student_classroom_ids(db, student.id)
    if not classroom_ids:
        return []

    quizzes = (
        db.query(Quiz)
        .filter(Quiz.classroom_id.in_(classroom_ids))
        .order_by(Quiz.created_at.desc())
        .all()
    )

    classroom_map = {
        c.id: c
        for c in db.query(Classroom).filter(Classroom.id.in_(classroom_ids)).all()
    }

    out = []
    for quiz in quizzes:
        question_count = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz.id).count()
        out.append(
            {
                "id": quiz.id,
                "classroom_id": quiz.classroom_id,
                "classroom_name": classroom_map[quiz.classroom_id].name,
                "grade": quiz.grade,
                "subject": quiz.subject,
                "title": quiz.title,
                "created_at": quiz.created_at,
                "question_count": question_count,
            }
        )

    return out


@router.get("/quizzes/{quiz_id}")
def get_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    classroom_ids = _student_classroom_ids(db, student.id)
    if quiz.classroom_id not in classroom_ids:
        raise HTTPException(status_code=403, detail="Quiz is not assigned to this student")

    classroom = db.query(Classroom).filter(Classroom.id == quiz.classroom_id).first()

    questions = (
        db.query(QuizQuestion)
        .filter(QuizQuestion.quiz_id == quiz.id)
        .order_by(QuizQuestion.order_index.asc())
        .all()
    )

    return {
        "id": quiz.id,
        "classroom_id": quiz.classroom_id,
        "classroom_name": classroom.name if classroom else "Unknown Classroom",
        "grade": quiz.grade,
        "subject": quiz.subject,
        "title": quiz.title,
        "created_at": quiz.created_at,
        "questions": [
            {
                "id": q.id,
                "order_index": q.order_index,
                "prompt": q.prompt,
            }
            for q in questions
        ],
    }


@router.post("/quizzes/{quiz_id}/submit")
def submit_quiz_answers(
    quiz_id: int,
    payload: QuizSubmitRequest,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    classroom_ids = _student_classroom_ids(db, student.id)
    if quiz.classroom_id not in classroom_ids:
        raise HTTPException(status_code=403, detail="Quiz is not assigned to this student")

    questions = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz.id).all()
    question_map = {q.id: q for q in questions}

    results = []
    correct_count = 0

    for submitted in payload.answers:
        question = question_map.get(submitted.question_id)
        if not question:
            continue

        expected = (question.answer or "").strip().lower()
        given = submitted.answer.strip().lower()
        is_correct = bool(expected) and expected == given
        if is_correct:
            correct_count += 1

        results.append(
            {
                "question_id": question.id,
                "prompt": question.prompt,
                "submitted_answer": submitted.answer,
                "correct": is_correct,
            }
        )

    existing = (
        db.query(QuizCompletion)
        .filter(
            QuizCompletion.quiz_id == quiz.id,
            QuizCompletion.student_id == student.id,
        )
        .first()
    )
    newly_completed = existing is None
    if existing:
        existing.correct_count = correct_count
        existing.total_questions = len(question_map)
    else:
        db.add(
            QuizCompletion(
                quiz_id=quiz.id,
                student_id=student.id,
                correct_count=correct_count,
                total_questions=len(question_map),
            )
        )
    db.commit()

    xp_update = None
    if newly_completed:
        xp_update = add_xp(db, student.id, QUIZ_COMPLETION_XP)

    return {
        "quiz_id": quiz.id,
        "total_questions": len(question_map),
        "answered_questions": len(results),
        "correct_count": correct_count,
        "xp": xp_update.total_xp if xp_update else student.total_xp,
        "level": xp_update.current_level if xp_update else student.current_level,
        "xp_awarded": QUIZ_COMPLETION_XP if newly_completed else 0,
        "level_up": xp_update.level_up if xp_update else False,
        "current_level": xp_update.current_level if xp_update else student.current_level,
        "total_xp": xp_update.total_xp if xp_update else student.total_xp,
        "results": results,
    }
