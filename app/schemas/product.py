"""
Product schemas for request/response validation
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid


class ProductBase(BaseModel):
    """Base product schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    sku: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    compare_at_price: Optional[float] = Field(None, gt=0)
    cost: Optional[float] = Field(None, ge=0)
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = Field(default_factory=list)
    images: Optional[List[str]] = Field(default_factory=list)
    variants: Optional[dict] = None
    metadata_: Optional[dict] = Field(None, alias="metadata")


class ProductCreate(ProductBase):
    """Product creation schema"""
    initial_quantity: Optional[int] = Field(default=0, ge=0)
    low_stock_threshold: Optional[int] = Field(default=10, ge=0)


class ProductUpdate(BaseModel):
    """Product update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    sku: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[float] = Field(None, gt=0)
    compare_at_price: Optional[float] = Field(None, gt=0)
    cost: Optional[float] = Field(None, ge=0)
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None
    variants: Optional[dict] = None
    is_active: Optional[bool] = None
    metadata_: Optional[dict] = Field(None, alias="metadata")


class InventoryUpdate(BaseModel):
    """Inventory update schema"""
    quantity: int = Field(..., ge=0)


class InventoryResponse(BaseModel):
    """Inventory response schema"""
    product_id: uuid.UUID
    quantity: int
    reserved: int
    available: int
    low_stock_threshold: int
    is_low_stock: bool
    
    model_config = ConfigDict(from_attributes=True)


class ProductResponse(ProductBase):
    """Product response schema"""
    id: uuid.UUID
    ecommerce_id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    inventory: Optional[InventoryResponse] = None
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
