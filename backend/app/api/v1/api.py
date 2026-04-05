from fastapi import APIRouter

from app.api.v1.routers import admin, auth, gameplay, student, teacher

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(admin.router)
api_router.include_router(gameplay.router)
api_router.include_router(student.router)
api_router.include_router(teacher.router)
