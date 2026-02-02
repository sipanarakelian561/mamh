from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token

def register(db: Session, email: str, password: str, role: str) -> User:
    if role not in ("student", "teacher"):
        raise HTTPException(status_code=400, detail="Role must be student or teacher")

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(email=email, password_hash=hash_password(password), role=role, is_admin=False)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def login(db: Session, email: str, password: str) -> str:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return create_access_token(subject=str(user.id), role=user.role, is_admin=user.is_admin)
