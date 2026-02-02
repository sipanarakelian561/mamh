from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.api import api_router
from app.db.init_db import init_db

app = FastAPI(title=settings.APP_NAME)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "ok"}
