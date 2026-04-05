from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings

def register(db: Session, email: str, password: str, role: str) -> User:
    if not settings.ALLOW_PUBLIC_REGISTRATION:
        raise HTTPException(status_code=403, detail="Public registration is disabled")

    normalized_email = email.strip().lower()
    normalized_role = role.strip().lower()

    if normalized_role not in ("student", "teacher"):
        raise HTTPException(status_code=400, detail="Role must be student or teacher")

    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    if db.query(User).filter(User.email == normalized_email).first():
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=normalized_email,
        password_hash=hash_password(password),
        role=normalized_role,
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def login(db: Session, email: str, password: str) -> str:
    normalized_email = email.strip().lower()
    user = db.query(User).filter(User.email == normalized_email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return create_access_token(
        subject=str(user.id),
        role=user.role,
        is_admin=user.is_admin,
        must_change_password=user.must_change_password,
    )


def change_password(db: Session, user: User, current_password: str, new_password: str) -> None:
    if user.role not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="Only teachers and admins can change passwords")
    if not verify_password(current_password, user.password_hash):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    user.password_hash = hash_password(new_password)
    user.must_change_password = False
    db.commit()
