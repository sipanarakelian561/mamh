import random
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, ChangePasswordRequest
from app.schemas.password_reset import (
    ForgotPasswordRequest,
    VerifyCodeRequest,
    ResetPasswordRequest,
)
from app.services.auth_service import register, login, change_password
from app.services.email_service import send_reset_email
from app.api.v1.deps.auth import get_current_user
from app.models.user import User
from app.models.password_reset_code import PasswordResetCode
from app.core.security import hash_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = register(db, payload.email, payload.password, payload.role, payload.school_id)
    return {"id": user.id, "email": user.email, "role": user.role, "is_admin": user.is_admin}


@router.post("/login", response_model=TokenResponse)
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    token = login(db, payload.email, payload.password)
    return TokenResponse(access_token=token)


@router.post("/change-password")
def change_password_route(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    change_password(db, user, payload.current_password, payload.new_password)
    return {"status": "ok"}


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    code = str(random.randint(100000, 999999))

    reset_code = PasswordResetCode(
        email=payload.email,
        code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=10),
        used=False,
    )

    db.add(reset_code)
    db.commit()

    send_reset_email(payload.email, code)

    return {"message": "Reset code sent"}


@router.post("/verify-reset-code")
def verify_reset_code(payload: VerifyCodeRequest, db: Session = Depends(get_db)):
    reset_code = db.query(PasswordResetCode).filter(
        PasswordResetCode.email == payload.email,
        PasswordResetCode.code == payload.code,
        PasswordResetCode.used == False,
        PasswordResetCode.expires_at > datetime.utcnow(),
    ).first()

    if not reset_code:
        raise HTTPException(status_code=400, detail="Invalid or expired code")

    return {"message": "Code verified"}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    reset_code = db.query(PasswordResetCode).filter(
        PasswordResetCode.email == payload.email,
        PasswordResetCode.code == payload.code,
        PasswordResetCode.used == False,
        PasswordResetCode.expires_at > datetime.utcnow(),
    ).first()

    if not reset_code:
        raise HTTPException(status_code=400, detail="Invalid or expired code")

    user = db.query(User).filter(User.email == payload.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hash_password(payload.new_password)
    reset_code.used = True

    db.commit()

    return {"message": "Password Changed Successfully"}