from sqlalchemy import Integer, ForeignKey, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    item_id: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(100))
    slot: Mapped[str] = mapped_column(String(30))   # head/body/weapon/etc.
    equipped: Mapped[bool] = mapped_column(Boolean, default=False)
