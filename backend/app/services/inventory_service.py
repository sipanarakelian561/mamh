from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.inventory import InventoryItem
from app.services.economy_service import get_student_balance_or_404


def add_item(db: Session, student_id: int, item_id: str, name: str, slot: str) -> InventoryItem:
    item = InventoryItem(student_id=student_id, item_id=item_id, name=name, slot=slot, equipped=False)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def purchase_item(
    db: Session,
    student_id: int,
    item_id: str,
    name: str,
    slot: str,
    cost: int,
) -> tuple[InventoryItem, int]:
    existing = (
        db.query(InventoryItem)
        .filter(InventoryItem.student_id == student_id, InventoryItem.item_id == item_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Item already owned")

    try:
        student = get_student_balance_or_404(db, student_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Student not found") from exc
    if student.currency_balance < cost:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    student.currency_balance -= cost
    item = InventoryItem(student_id=student_id, item_id=item_id, name=name, slot=slot, equipped=False)
    db.add(student)
    db.add(item)
    db.commit()
    db.refresh(item)
    db.refresh(student)
    return item, student.currency_balance


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
