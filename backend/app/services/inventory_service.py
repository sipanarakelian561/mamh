from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.inventory import InventoryItem
from app.models.user import User
from app.services.economy_service import get_student_balance_or_404

CHARACTER_IDS = {"monster", "dog", "dinosaur"}

# Server-authoritative shop catalog.
SHOP_CATALOG: dict[str, dict[str, str | int]] = {
    "hat_1": {
        "name": "Wizard Hat",
        "slot": "head",
        "category": "accessory",
        "cost": 10,
        "image_key": "monster",
    },
    "hat_2": {
        "name": "Knight Helm",
        "slot": "head",
        "category": "accessory",
        "cost": 10,
        "image_key": "monster",
    },
    "hat_3": {
        "name": "Shop Hat",
        "slot": "head",
        "category": "accessory",
        "cost": 15,
        "image_key": "monster",
    },
    "monster": {
        "name": "Monster Unlock",
        "slot": "character",
        "category": "character",
        "cost": 670,
        "base_character": "monster",
        "image_key": "monster",
    },
    "dog": {
        "name": "Dog Unlock",
        "slot": "character",
        "category": "character",
        "cost": 670,
        "base_character": "dog",
        "image_key": "dog",
    },
    "dinosaur": {
        "name": "Dinosaur Unlock",
        "slot": "character",
        "category": "character",
        "cost": 670,
        "base_character": "dinosaur",
        "image_key": "dinosaur",
    },
    "rare_pet_skin": {
        "name": "Rare Monster Skin",
        "slot": "skin",
        "category": "skin",
        "cost": 100,
        "base_character": "monster",
        "image_key": "monster_s1",
    },
    "legendary_pet_skin": {
        "name": "Legendary Monster Skin",
        "slot": "skin",
        "category": "skin",
        "cost": 100,
        "base_character": "monster",
        "image_key": "monster_s2",
    },
    "mystic_pet_skin": {
        "name": "Mystic Monster Skin",
        "slot": "skin",
        "category": "skin",
        "cost": 100,
        "base_character": "monster",
        "image_key": "monster_s2",
    },
    "dog_s1_skin": {
        "name": "Rare Dog Skin",
        "slot": "skin",
        "category": "skin",
        "cost": 100,
        "base_character": "dog",
        "image_key": "dog_s1",
    },
    "dog_s2_skin": {
        "name": "Legendary Dog Skin",
        "slot": "skin",
        "category": "skin",
        "cost": 100,
        "base_character": "dog",
        "image_key": "dog_s2",
    },
    "dinosaur_s1_skin": {
        "name": "Rare Dinosaur Skin",
        "slot": "skin",
        "category": "skin",
        "cost": 100,
        "base_character": "dinosaur",
        "image_key": "dinosaur_s1",
    },
    "dinosaur_s2_skin": {
        "name": "Legendary Dinosaur Skin",
        "slot": "skin",
        "category": "skin",
        "cost": 100,
        "base_character": "dinosaur",
        "image_key": "dinosaur_s2",
    },
}


def add_item(db: Session, student_id: int, item_id: str, name: str, slot: str) -> InventoryItem:
    item = InventoryItem(student_id=student_id, item_id=item_id, name=name, slot=slot, equipped=False)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def _owned_character_ids(db: Session, student: User) -> set[str]:
    owned = set()
    if student.starter_monster:
        owned.add(student.starter_monster.lower())
    character_rows = (
        db.query(InventoryItem.item_id)
        .filter(InventoryItem.student_id == student.id, InventoryItem.slot == "character")
        .all()
    )
    for (item_id,) in character_rows:
        if item_id:
            owned.add(str(item_id).lower())
    return owned


def _owned_item_ids(db: Session, student_id: int) -> set[str]:
    return {
        item_id
        for (item_id,) in db.query(InventoryItem.item_id).filter(InventoryItem.student_id == student_id).all()
    }


def _prune_invalid_skin_ownership(db: Session, student: User) -> None:
    owned_characters = _owned_character_ids(db, student)
    skin_rows = (
        db.query(InventoryItem)
        .filter(InventoryItem.student_id == student.id, InventoryItem.slot == "skin")
        .all()
    )
    invalid_ids = []
    for row in skin_rows:
        base_character = str(SHOP_CATALOG.get(row.item_id, {}).get("base_character", "")).lower()
        if base_character and base_character not in owned_characters:
            invalid_ids.append(row.id)

    if not invalid_ids:
        return

    (
        db.query(InventoryItem)
        .filter(InventoryItem.id.in_(invalid_ids))
        .delete(synchronize_session=False)
    )
    db.commit()


def _catalog_state_for_student(student: User, item_id: str, item: dict[str, str | int], owned_item_ids: set[str], owned_characters: set[str]) -> dict[str, str | int | bool | None]:
    base_character = str(item.get("base_character", "") or "").lower() or None
    category = str(item["category"])
    owned = item_id in owned_item_ids or (category == "character" and item_id in owned_characters)
    can_purchase = False
    lock_reason: str | None = None

    if owned:
        can_purchase = False
    elif category == "character":
        if item_id == (student.starter_monster or "").lower():
            lock_reason = "Starter already owned"
        else:
            can_purchase = True
    elif category == "skin":
        if base_character not in owned_characters:
            lock_reason = "Unlock %s first" % str(base_character).capitalize()
        elif (student.equipped_monster or "").lower() != base_character:
            lock_reason = "Equip %s to buy this skin" % str(base_character).capitalize()
        else:
            can_purchase = True
    else:
        can_purchase = True

    return {
        "item_id": item_id,
        "name": str(item["name"]),
        "slot": str(item["slot"]),
        "category": category,
        "cost": int(item["cost"]),
        "base_character": base_character,
        "image_key": item.get("image_key"),
        "owned": owned,
        "can_purchase": can_purchase,
        "lock_reason": lock_reason,
    }


def get_shop_catalog(db: Session, student_id: int) -> list[dict[str, str | int | bool | None]]:
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    _prune_invalid_skin_ownership(db, student)
    owned_item_ids = _owned_item_ids(db, student_id)
    owned_characters = _owned_character_ids(db, student)
    return [
        _catalog_state_for_student(student, item_id, item, owned_item_ids, owned_characters)
        for item_id, item in SHOP_CATALOG.items()
    ]


def purchase_item(db: Session, student_id: int, item_id: str) -> tuple[InventoryItem, int]:
    item_def = SHOP_CATALOG.get(item_id)
    if not item_def:
        raise HTTPException(status_code=404, detail="Shop item not found")

    try:
        student = get_student_balance_or_404(db, student_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Student not found") from exc
    _prune_invalid_skin_ownership(db, student)

    existing = (
        db.query(InventoryItem)
        .filter(InventoryItem.student_id == student_id, InventoryItem.item_id == item_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Item already owned")

    owned_characters = _owned_character_ids(db, student)
    category = str(item_def["category"])
    base_character = str(item_def.get("base_character", "") or "").lower()

    if category == "character":
        if item_id in owned_characters or item_id == (student.starter_monster or "").lower():
            raise HTTPException(status_code=409, detail="Character already owned")
    elif category == "skin":
        if base_character not in owned_characters:
            raise HTTPException(status_code=400, detail="Unlock that character first")
        if (student.equipped_monster or "").lower() != base_character:
            raise HTTPException(status_code=400, detail="Equip that character to buy this skin")

    cost = int(item_def["cost"])
    if student.currency_balance < cost:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    student.currency_balance -= cost
    item = InventoryItem(
        student_id=student_id,
        item_id=item_id,
        name=str(item_def["name"]),
        slot=str(item_def["slot"]),
        equipped=category == "character",
    )
    if category == "character":
        (
            db.query(InventoryItem)
            .filter(InventoryItem.student_id == student_id, InventoryItem.slot == "character")
            .update({"equipped": False})
        )
        (
            db.query(InventoryItem)
            .filter(InventoryItem.student_id == student_id, InventoryItem.slot == "skin")
            .update({"equipped": False})
        )
        student.equipped_monster = item_id

    db.add(student)
    db.add(item)
    db.commit()
    db.refresh(item)
    db.refresh(student)
    return item, student.currency_balance


def list_items(db: Session, student_id: int) -> list[InventoryItem]:
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        return []
    _prune_invalid_skin_ownership(db, student)
    return db.query(InventoryItem).filter(InventoryItem.student_id == student_id).all()


def set_equipped(db: Session, student_id: int, item_id: str, equipped: bool) -> InventoryItem:
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    item = (
        db.query(InventoryItem)
        .filter(InventoryItem.student_id == student_id, InventoryItem.item_id == item_id)
        .first()
    )
    if not item:
        if equipped and item_id == (student.starter_monster or "").lower():
            (
                db.query(InventoryItem)
                .filter(InventoryItem.student_id == student_id, InventoryItem.slot == "character")
                .update({"equipped": False})
            )
            (
                db.query(InventoryItem)
                .filter(InventoryItem.student_id == student_id, InventoryItem.slot == "skin")
                .update({"equipped": False})
            )
            student.equipped_monster = item_id
            db.add(student)
            db.commit()
            transient = InventoryItem(
                student_id=student_id,
                item_id=item_id,
                name=item_id.capitalize(),
                slot="character",
                equipped=True,
            )
            return transient
        raise HTTPException(status_code=404, detail="Item not found")

    if item.slot == "character":
        if not equipped:
            raise HTTPException(status_code=400, detail="A character must stay equipped")
        (
            db.query(InventoryItem)
            .filter(
                InventoryItem.student_id == student_id,
                InventoryItem.slot == "character",
                InventoryItem.id != item.id,
            )
            .update({"equipped": False})
        )
        (
            db.query(InventoryItem)
            .filter(InventoryItem.student_id == student_id, InventoryItem.slot == "skin")
            .update({"equipped": False})
        )
        item.equipped = True
        student.equipped_monster = item.item_id
        db.add(student)
        db.commit()
        db.refresh(item)
        db.refresh(student)
        return item

    if item.slot == "skin":
        base_character = str(SHOP_CATALOG.get(item.item_id, {}).get("base_character", "")).lower()
        if base_character and (student.equipped_monster or "").lower() != base_character:
            raise HTTPException(status_code=400, detail="Equip that character before equipping this skin")

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
