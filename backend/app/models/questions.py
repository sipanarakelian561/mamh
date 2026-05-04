from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class GameplayQuestion(Base):
    __tablename__ = "gameplay_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    teacher_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True, nullable=True)
    grade: Mapped[int] = mapped_column(Integer, index=True)
    subject: Mapped[str] = mapped_column(String(50), index=True)
    difficulty: Mapped[str] = mapped_column(String(20), default="easy", index=True)
    prompt: Mapped[str] = mapped_column(Text)

    answer_a: Mapped[str] = mapped_column(String(255))
    answer_b: Mapped[str] = mapped_column(String(255))
    answer_c: Mapped[str] = mapped_column(String(255))
    answer_d: Mapped[str] = mapped_column(String(255))

    correct_index: Mapped[int] = mapped_column(Integer)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    def to_public_dict(self) -> dict:
        return {
            "id": self.id,
            "grade": self.grade,
            "subject": self.subject,
            "difficulty": self.difficulty,
            "prompt": self.prompt,
            "answers": [
                self.answer_a,
                self.answer_b,
                self.answer_c,
                self.answer_d,
            ],
        }
