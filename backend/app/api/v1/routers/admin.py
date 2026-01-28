from fastapi import APIRouter, Depends
from app.api.v1.deps.auth import require_admin
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/me")
def admin_me(admin: User = Depends(require_admin)):
    return {"id": admin.id, "email": admin.email, "role": admin.role, "is_admin": admin.is_admin}
