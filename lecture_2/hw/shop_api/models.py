from pydantic import BaseModel, Field
from typing import Optional, List

class Item(BaseModel):
    id: Optional[int] = None
    name: str
    price: float = Field(gt=0)
    deleted: bool = False

class CartItem(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool

class Cart(BaseModel):
    id: int
    items: List[CartItem] = []
    price: float = 0
