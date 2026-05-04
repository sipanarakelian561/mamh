from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Import ALL models here so SQLAlchemy knows about them
from app.models.user import User
from app.models.password_reset_code import PasswordResetCode