from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.inventory import InventoryItem


def add_item(db: Session, student_id: int, item_id: str, name: str, slot: str) -> InventoryItem:
    item = InventoryItem(student_id=student_id, item_id=item_id, name=name, slot=slot, equipped=False)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_items(db: Session, student_id: int) -> list[InventoryItem]:
    return db.query(InventoryItem).filter(InventoryItem.student_id == student_id).all()


def set_equipped(db: Session, student_id: int, item_id: str, equipped: bool) -> InventoryItem:
    item = (
        db.query(InventoryItem)
        .filter(InventoryItem.student_id == student_id, InventoryItem.item_id == item_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if equipped:
        (
            db.query(InventoryItem)
            .filter(
                InventoryItem.student_id == student_id,
                InventoryItem.slot == item.slot,
                InventoryItem.id != item.id,
            )
            .update({"equipped": False})
        )

    item.equipped = equipped
    db.commit()
    db.refresh(item)
    return item
