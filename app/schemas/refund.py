"""
Refund schemas for request/response validation
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid
from enum import Enum


class RefundStatusEnum(str, Enum):
    """Refund status enumeration"""
    REQUESTED = "REQUESTED"
    APPROVED = "APPROVED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class RefundReasonEnum(str, Enum):
    """Refund reason enumeration"""
    CUSTOMER_REQUEST = "CUSTOMER_REQUEST"
    DEFECTIVE_PRODUCT = "DEFECTIVE_PRODUCT"
    WRONG_ITEM = "WRONG_ITEM"
    NOT_AS_DESCRIBED = "NOT_AS_DESCRIBED"
    DAMAGED_IN_TRANSIT = "DAMAGED_IN_TRANSIT"
    ORDER_CANCELLED = "ORDER_CANCELLED"
    OTHER = "OTHER"


class RefundCreate(BaseModel):
    """Schema for creating a refund request"""
    order_id: uuid.UUID
    amount: float = Field(gt=0, description="Refund amount")
    reason: RefundReasonEnum
    customer_notes: Optional[str] = Field(None, max_length=1000)
    
    class Config:
        from_attributes = True


class RefundUpdate(BaseModel):
    """Schema for updating a refund (admin only)"""
    status: Optional[RefundStatusEnum] = None
    admin_notes: Optional[str] = Field(None, max_length=1000)
    transaction_id: Optional[str] = None
    refund_method: Optional[str] = None
    inventory_returned: Optional[bool] = None
    
    class Config:
        from_attributes = True


class RefundResponse(BaseModel):
    """Schema for refund response"""
    id: uuid.UUID
    order_id: uuid.UUID
    ecommerce_id: uuid.UUID
    refund_number: str
    amount: float
    reason: RefundReasonEnum
    status: RefundStatusEnum
    customer_notes: Optional[str] = None
    admin_notes: Optional[str] = None
    transaction_id: Optional[str] = None
    refund_method: Optional[str] = None
    inventory_returned: bool
    requested_at: datetime
    approved_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RefundApproval(BaseModel):
    """Schema for approving/rejecting a refund"""
    approve: bool
    admin_notes: Optional[str] = Field(None, max_length=1000)
    
    class Config:
        from_attributes = True
