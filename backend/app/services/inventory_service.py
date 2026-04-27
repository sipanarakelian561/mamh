from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.inventory import InventoryItem
from app.services.economy_service import get_student_balance_or_404

# Server-authoritative shop catalog. Clients purchase by item_id only.
SHOP_CATALOG: dict[str, dict[str, str | int]] = {
    "hat_1": {"name": "Wizard Hat", "slot": "head", "cost": 10},
    "hat_2": {"name": "Knight Helm", "slot": "head", "cost": 10},
    "hat_3": {"name": "Shop Hat", "slot": "head", "cost": 15},
    "rare_pet_skin": {"name": "Rare", "slot": "skin", "cost": 50},
    "legendary_pet_skin": {"name": "Legendary", "slot": "skin", "cost": 100},
    "mystic_pet_skin": {"name": "Mystic", "slot": "skin", "cost": 300},
}


def add_item(db: Session, student_id: int, item_id: str, name: str, slot: str) -> InventoryItem:
    item = InventoryItem(student_id=student_id, item_id=item_id, name=name, slot=slot, equipped=False)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_shop_catalog(db: Session, student_id: int) -> list[dict[str, str | int | bool]]:
    owned_item_ids = {
        item_id
        for (item_id,) in db.query(InventoryItem.item_id).filter(InventoryItem.student_id == student_id).all()
    }
    return [
        {
            "item_id": item_id,
            "name": str(item["name"]),
            "slot": str(item["slot"]),
            "cost": int(item["cost"]),
            "owned": item_id in owned_item_ids,
        }
        for item_id, item in SHOP_CATALOG.items()
    ]


def purchase_item(db: Session, student_id: int, item_id: str) -> tuple[InventoryItem, int]:
    item_def = SHOP_CATALOG.get(item_id)
    if not item_def:
        raise HTTPException(status_code=404, detail="Shop item not found")

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

    cost = int(item_def["cost"])
    if student.currency_balance < cost:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    student.currency_balance -= cost
    item = InventoryItem(
        student_id=student_id,
        item_id=item_id,
        name=str(item_def["name"]),
        slot=str(item_def["slot"]),
        equipped=False,
    )
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
