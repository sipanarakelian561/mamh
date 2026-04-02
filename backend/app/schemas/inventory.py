from pydantic import BaseModel, Field


class ItemAdd(BaseModel):
    item_id: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)
    slot: str = Field(min_length=1, max_length=30)


class ItemEquip(BaseModel):
    item_id: str = Field(min_length=1, max_length=50)
    equipped: bool
