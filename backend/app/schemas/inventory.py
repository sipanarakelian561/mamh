from pydantic import BaseModel

class ItemAdd(BaseModel):
    item_id: str
    name: str
    slot: str

class ItemEquip(BaseModel):
    item_id: str
    equipped: bool
