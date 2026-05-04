import random
import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.deps.auth import require_admin, require_school_admin, require_super_admin
from app.core.security import hash_password
from app.db.session import get_db
from app.models.assignment import Assignment
from app.models.assignment_completion import AssignmentCompletion
from app.models.classroom import Classroom
from app.models.classroom_membership import ClassroomMembership
from app.models.inventory import InventoryItem
from app.models.progress import StudentProgress
from app.models.quiz import Quiz, QuizQuestion
from app.models.quiz_completion import QuizCompletion
from app.models.school import School
from app.models.user import User
from app.schemas.admin import (
    AdminChangeStudentPasswordRequest,
    AdminCreateUserRequest,
    AdminCreateUserResponse,
    AdminSchoolCreateRequest,
    AdminSchoolOut,
    AdminUpdateUserRequest,
    AdminUserOut,
)

router = APIRouter(prefix="/admin", tags=["admin"])


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z]", "", value).lower()
    return cleaned or "user"


def _generate_unique_email(db: Session, first_name: str, last_name: str) -> str:
    first = _slugify(first_name)
    last = _slugify(last_name)
    for _ in range(20):
        suffix = random.randint(100, 999)
        email = f"{first}.{last}.{suffix}@gmail.com"
        exists = db.query(User).filter(User.email == email).first()
        if not exists:
            return email
    raise HTTPException(status_code=409, detail="Unable to generate unique email")


def _get_school(db: Session, school_id: int) -> School:
    school = db.get(School, school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return school


def _resolve_school_scope(db: Session, admin: User, requested_school_id: int | None) -> School | None:
    if admin.role == "super_admin":
        if requested_school_id is None:
            return None
        return _get_school(db, requested_school_id)

    if admin.school_id is None:
        raise HTTPException(status_code=400, detail="Admin is not assigned to a school")
    if requested_school_id is not None and requested_school_id != admin.school_id:
        raise HTTPException(status_code=403, detail="Cannot manage another school")
    return _get_school(db, admin.school_id)


def _delete_user_dependencies(db: Session, user: User) -> None:
    if user.role == "student":
        db.query(ClassroomMembership).filter(ClassroomMembership.student_id == user.id).delete()
        db.query(AssignmentCompletion).filter(AssignmentCompletion.student_id == user.id).delete()
        db.query(QuizCompletion).filter(QuizCompletion.student_id == user.id).delete()
        db.query(InventoryItem).filter(InventoryItem.student_id == user.id).delete()
        db.query(StudentProgress).filter(StudentProgress.student_id == user.id).delete()
        return

    if user.role == "teacher":
        classroom_ids = [
            classroom_id
            for (classroom_id,) in db.query(Classroom.id).filter(Classroom.teacher_id == user.id).all()
        ]
        assignment_ids = [
            assignment_id
            for (assignment_id,) in db.query(Assignment.id).filter(Assignment.teacher_id == user.id).all()
        ]
        quiz_ids = [
            quiz_id
            for (quiz_id,) in db.query(Quiz.id).filter(Quiz.teacher_id == user.id).all()
        ]

        if assignment_ids:
            db.query(AssignmentCompletion).filter(AssignmentCompletion.assignment_id.in_(assignment_ids)).delete(
                synchronize_session=False
            )
        if quiz_ids:
            db.query(QuizCompletion).filter(QuizCompletion.quiz_id.in_(quiz_ids)).delete(
                synchronize_session=False
            )
            db.query(QuizQuestion).filter(QuizQuestion.quiz_id.in_(quiz_ids)).delete(
                synchronize_session=False
            )
            db.query(Quiz).filter(Quiz.id.in_(quiz_ids)).delete(synchronize_session=False)
        if assignment_ids:
            db.query(Assignment).filter(Assignment.id.in_(assignment_ids)).delete(synchronize_session=False)
        if classroom_ids:
            db.query(ClassroomMembership).filter(ClassroomMembership.classroom_id.in_(classroom_ids)).delete(
                synchronize_session=False
            )
            db.query(Classroom).filter(Classroom.id.in_(classroom_ids)).delete(synchronize_session=False)


@router.post("/users", response_model=AdminCreateUserResponse)
def create_user(
    payload: AdminCreateUserRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    role = payload.role.lower()
    if role not in {"student", "teacher", "admin"}:
        raise HTTPException(status_code=400, detail="Invalid role")

    if admin.role != "super_admin" and role == "admin":
        raise HTTPException(status_code=403, detail="Only super admins can create school admins")
    if role == "student" and payload.grade_level is None:
        raise HTTPException(status_code=400, detail="grade_level is required for student accounts")
    if role != "student" and payload.grade_level is not None:
        raise HTTPException(status_code=400, detail="grade_level can only be set for student accounts")

    school = _resolve_school_scope(db, admin, payload.school_id)
    if school is None:
        raise HTTPException(status_code=400, detail="school_id is required")

    is_admin = role == "admin"

    email = _generate_unique_email(db, payload.first_name, payload.last_name)
    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        role=role,
        is_admin=is_admin,
        must_change_password=True,
        school_id=school.id,
        grade_level=payload.grade_level if role == "student" else None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return AdminCreateUserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        is_admin=user.is_admin,
        school_id=user.school_id,
        school_name=school.name,
        grade_level=user.grade_level,
    )


@router.get("/users", response_model=list[AdminUserOut])
def list_users(
    q: str | None = None,
    role: str | None = None,
    school_id: int | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    school = _resolve_school_scope(db, admin, school_id)
    query = db.query(User, School.name).outerjoin(School, School.id == User.school_id)
    if q:
        needle = f"%{q.lower()}%"
        query = query.filter(User.email.ilike(needle))
    if role:
        query = query.filter(User.role == role.lower())
    if school is not None:
        query = query.filter(User.school_id == school.id)
    elif admin.role != "super_admin":
        query = query.filter(User.school_id == admin.school_id)

    rows = query.order_by(User.id.desc()).limit(max(1, min(limit, 200))).all()
    return [
        AdminUserOut(
            id=user.id,
            email=user.email,
            role=user.role,
            is_admin=user.is_admin,
            must_change_password=user.must_change_password,
            school_id=user.school_id,
            school_name=school_name,
            grade_level=user.grade_level,
        )
        for user, school_name in rows
    ]


@router.patch("/users/{user_id}", response_model=AdminUserOut)
def update_user(
    user_id: int,
    payload: AdminUpdateUserRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if admin.role != "super_admin" and user.school_id != admin.school_id:
        raise HTTPException(status_code=403, detail="Cannot manage a user from another school")
    if payload.grade_level is not None and user.role != "student":
        raise HTTPException(status_code=400, detail="grade_level can only be updated for student accounts")

    user.grade_level = payload.grade_level
    db.add(user)
    db.commit()
    db.refresh(user)

    school_name = db.query(School.name).filter(School.id == user.school_id).scalar()
    return AdminUserOut(
        id=user.id,
        email=user.email,
        role=user.role,
        is_admin=user.is_admin,
        must_change_password=user.must_change_password,
        school_id=user.school_id,
        school_name=school_name,
        grade_level=user.grade_level,
    )


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account")
    if user.role == "super_admin":
        raise HTTPException(status_code=403, detail="Super admin accounts cannot be deleted here")
    if admin.role != "super_admin" and user.school_id != admin.school_id:
        raise HTTPException(status_code=403, detail="Cannot delete a user from another school")

    _delete_user_dependencies(db, user)
    db.delete(user)
    db.commit()
    return {"status": "ok"}


@router.post("/students/{student_id}/password")
def change_student_password(
    student_id: int,
    payload: AdminChangeStudentPasswordRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_school_admin),
):
    student = db.get(User, student_id)
    if not student or student.role != "student":
        raise HTTPException(status_code=404, detail="Student not found")
    if admin.school_id is None or student.school_id != admin.school_id:
        raise HTTPException(status_code=403, detail="Cannot manage a student from another school")

    student.password_hash = hash_password(payload.new_password)
    student.must_change_password = True
    db.add(student)
    db.commit()
    return {"status": "ok", "student_id": student.id}


@router.get("/schools", response_model=list[AdminSchoolOut])
def list_schools(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    query = db.query(School)
    if admin.role != "super_admin":
        if admin.school_id is None:
            return []
        query = query.filter(School.id == admin.school_id)

    schools = query.order_by(School.name.asc()).all()
    return [AdminSchoolOut(id=school.id, name=school.name) for school in schools]


@router.post("/schools", response_model=AdminSchoolOut)
def create_school(
    payload: AdminSchoolCreateRequest,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_super_admin),
):
    existing = db.query(School).filter(School.name == payload.name.strip()).first()
    if existing:
        raise HTTPException(status_code=409, detail="School already exists")

    school = School(name=payload.name.strip())
    db.add(school)
    db.commit()
    db.refresh(school)
    return AdminSchoolOut(id=school.id, name=school.name)
