from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, ChangePasswordRequest
from app.services.auth_service import register, login, change_password
from app.api.v1.deps.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = register(db, payload.email, payload.password, payload.role)
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
