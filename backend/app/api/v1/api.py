from fastapi import APIRouter
from app.api.v1.routers import auth, student, teacher, admin, gameplay

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(student.router)
api_router.include_router(teacher.router)
api_router.include_router(admin.router)
api_router.include_router(gameplay.router)
