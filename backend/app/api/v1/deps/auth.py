from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.get(User, user_id_int)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    token_role = payload.get("role")
    token_admin = payload.get("adm", False)
    token_school_id = payload.get("sch")
    if (
        token_role != user.role
        or bool(token_admin) != bool(user.is_admin)
        or token_school_id != user.school_id
    ):
        raise HTTPException(status_code=401, detail="Token no longer matches user permissions")
    return user

def require_teacher(user: User = Depends(get_current_user)) -> User:
    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="Teacher access required")
    return user

def require_student(user: User = Depends(get_current_user)) -> User:
    if user.role != "student":
        raise HTTPException(status_code=403, detail="Student access required")
    return user

def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def require_school_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin" or not user.is_admin:
        raise HTTPException(status_code=403, detail="School admin access required")
    return user


def require_super_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "super_admin" or not user.is_admin:
        raise HTTPException(status_code=403, detail="Super admin access required")
    return user
