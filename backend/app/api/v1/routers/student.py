from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.v1.deps.auth import require_student
from app.models.user import User
from app.schemas.inventory import ItemAdd, ItemEquip
from app.services.progress_service import get_or_create_progress
from app.services.inventory_service import add_item, list_items, set_equipped

router = APIRouter(prefix="/student", tags=["student"])

@router.get("/progress")
def student_progress(db: Session = Depends(get_db), student: User = Depends(require_student)):
    p = get_or_create_progress(db, student.id)
    return {"student_id": student.id, "xp": p.xp, "level": p.level, "problems_solved": p.problems_solved}

@router.post("/inventory/add")
def student_add_item(payload: ItemAdd, db: Session = Depends(get_db), student: User = Depends(require_student)):
    item = add_item(db, student.id, payload.item_id, payload.name, payload.slot)
    return {"id": item.id, "item_id": item.item_id, "equipped": item.equipped}

@router.get("/inventory")
def student_inventory(db: Session = Depends(get_db), student: User = Depends(require_student)):
    inv = list_items(db, student.id)
    return [{"item_id": i.item_id, "name": i.name, "slot": i.slot, "equipped": i.equipped} for i in inv]

@router.post("/inventory/equip")
def student_equip(payload: ItemEquip, db: Session = Depends(get_db), student: User = Depends(require_student)):
    item = set_equipped(db, student.id, payload.item_id, payload.equipped)
    return {"item_id": item.item_id, "equipped": item.equipped, "slot": item.slot}
