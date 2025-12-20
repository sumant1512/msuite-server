"""
Order schemas for request/response validation
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid
from app.models.order import OrderStatus, PaymentStatus


class OrderItemCreate(BaseModel):
    """Order item creation schema"""
    product_id: uuid.UUID
    quantity: int = Field(..., gt=0)
    variant: Optional[str] = None


class OrderItemResponse(BaseModel):
    """Order item response schema"""
    id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    unit_price: float
    total_price: float
    variant: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    """Base order schema"""
    customer_id: uuid.UUID
    shipping_address: Optional[dict] = None
    billing_address: Optional[dict] = None
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    """Order creation schema"""
    items: List[OrderItemCreate] = Field(..., min_length=1)


class OrderUpdate(BaseModel):
    """Order update schema"""
    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None
    shipping_address: Optional[dict] = None
    billing_address: Optional[dict] = None
    notes: Optional[str] = None


class OrderResponse(OrderBase):
    """Order response schema"""
    id: uuid.UUID
    ecommerce_id: uuid.UUID
    order_number: str
    subtotal: float
    tax: float
    shipping: float
    total: float
    status: OrderStatus
    payment_status: PaymentStatus
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse] = []
    
    model_config = ConfigDict(from_attributes=True)
