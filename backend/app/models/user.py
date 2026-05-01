from sqlalchemy import String, Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20))  # student, teacher, admin, super_admin
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=False)
    school_id: Mapped[int | None] = mapped_column(ForeignKey("schools.id"), index=True, nullable=True)
    grade_level: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    total_xp: Mapped[int] = mapped_column(Integer, default=0)
    currency_balance: Mapped[int] = mapped_column(Integer, default=0)
    starter_monster: Mapped[str | None] = mapped_column(String(50), nullable=True)
    equipped_monster: Mapped[str | None] = mapped_column(String(50), nullable=True)

    @staticmethod
    def xp_required_for_level(level: int) -> int:
        safe_level = max(1, level)
        return 5 + (safe_level * 10)

    @property
    def current_level(self) -> int:
        total = max(0, self.total_xp)
        level = 1
        while total >= self.xp_required_for_level(level):
            total -= self.xp_required_for_level(level)
            level += 1
        return level

    @property
    def xp_into_current_level(self) -> int:
        total = max(0, self.total_xp)
        level = 1
        while total >= self.xp_required_for_level(level):
            total -= self.xp_required_for_level(level)
            level += 1
        return total

    @property
    def xp_to_next_level(self) -> int:
        return max(0, self.xp_required_for_level(self.current_level) - self.xp_into_current_level)

    @property
    def xp_progress_percentage(self) -> float:
        needed = self.xp_required_for_level(self.current_level)
        if needed <= 0:
            return 100.0
        return round((self.xp_into_current_level / needed) * 100, 2)
