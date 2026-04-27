import json

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    APP_NAME: str = "Monster Ate My Homework API"
    ENV: str = "local"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./app.db"
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALLOW_PUBLIC_REGISTRATION: bool = False
    ADMIN_EMAIL: str | None = None
    ADMIN_PASSWORD: str | None = None
    RUN_DB_INIT: bool = True
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ]

    @field_validator("ACCESS_TOKEN_EXPIRE_MINUTES")
    @classmethod
    def validate_token_expiration(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be greater than 0")
        return value

    @field_validator("JWT_SECRET")
    @classmethod
    def validate_jwt_secret_strength(cls, value: str, info) -> str:
        env = str((info.data or {}).get("ENV", "local")).lower()
        db_url = str((info.data or {}).get("DATABASE_URL", ""))
        debug = bool((info.data or {}).get("DEBUG", True))
        weak_values = {"change-me", "change-me-super-secret", "secret", "password"}
        non_local_db = not db_url.startswith("sqlite")
        must_be_strong = env != "local" or not debug or non_local_db
        if must_be_strong and (value in weak_values or len(value) < 32):
            raise ValueError(
                "JWT_SECRET is too weak for non-local environments. "
                "Use at least 32 random characters."
            )
        return value

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def split_allowed_origins(cls, value):
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return []
            if stripped.startswith("["):
                return json.loads(stripped)
            return [v.strip() for v in value.split(",") if v.strip()]
        return value

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
