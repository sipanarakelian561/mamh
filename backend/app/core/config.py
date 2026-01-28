from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Monster Ate My Homework API"
    ENV: str = "local"
    DATABASE_URL: str = "sqlite:///./app.db"
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"

settings = Settings()
