from pydantic import BaseModel, Field


class ItemAdd(BaseModel):
    item_id: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)
    slot: str = Field(min_length=1, max_length=30)


class ItemEquip(BaseModel):
    item_id: str = Field(min_length=1, max_length=50)
    equipped: bool


class ItemPurchase(BaseModel):
    item_id: str = Field(min_length=1, max_length=50)


class ShopItemOut(BaseModel):
    item_id: str
    name: str
    slot: str
    cost: int
    category: str
    base_character: str | None = None
    image_key: str | None = None
    owned: bool = False
    can_purchase: bool = False
    lock_reason: str | None = None


class ItemPurchaseOut(BaseModel):
    id: int
    item_id: str
    name: str
    slot: str
    equipped: bool
    currency_balance: int
