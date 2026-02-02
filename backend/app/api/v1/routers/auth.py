from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.services.auth_service import register, login

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = register(db, payload.email, payload.password, payload.role)
    return {"id": user.id, "email": user.email, "role": user.role, "is_admin": user.is_admin}

@router.post("/login", response_model=TokenResponse)
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    token = login(db, payload.email, payload.password)
    return TokenResponse(access_token=token)
