from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class StudentProgress(Base):
    __tablename__ = "student_progress"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=1)
    problems_solved: Mapped[int] = mapped_column(Integer, default=0)
