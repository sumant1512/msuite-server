from pydantic import BaseModel, Field
from typing import List, Optional
import uuid


class CartItemCreate(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(gt=0)


class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0)


class CartItemResponse(BaseModel):
    product_id: uuid.UUID
    quantity: int
    unit_price: float
    total_price: float


class CartResponse(BaseModel):
    id: uuid.UUID
    ecommerce_id: uuid.UUID
    customer_id: uuid.UUID
    items: List[CartItemResponse]
    subtotal: float
    total_items: int
