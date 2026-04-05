import random
import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.deps.auth import require_admin
from app.core.security import hash_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.admin import AdminCreateUserRequest, AdminCreateUserResponse, AdminUserOut

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


@router.post("/users", response_model=AdminCreateUserResponse)
def create_user(
    payload: AdminCreateUserRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    role = payload.role.lower()
    is_admin = role == "admin"

    email = _generate_unique_email(db, payload.first_name, payload.last_name)
    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        role=role,
        is_admin=is_admin,
        must_change_password=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return AdminCreateUserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        is_admin=user.is_admin,
    )


@router.get("/users", response_model=list[AdminUserOut])
def list_users(
    q: str | None = None,
    role: str | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    query = db.query(User)
    if q:
        needle = f"%{q.lower()}%"
        query = query.filter(User.email.ilike(needle))
    if role:
        query = query.filter(User.role == role.lower())
    rows = query.order_by(User.id.desc()).limit(max(1, min(limit, 200))).all()
    return [
        AdminUserOut(
            id=u.id,
            email=u.email,
            role=u.role,
            is_admin=u.is_admin,
            must_change_password=u.must_change_password,
        )
        for u in rows
    ]
