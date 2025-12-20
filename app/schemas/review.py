"""
Product review schemas for request/response validation
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class ReviewBase(BaseModel):
    """Base review schema"""
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=200)
    comment: Optional[str] = None
    images: Optional[List[str]] = None


class ReviewCreate(ReviewBase):
    """Schema for creating a review"""
    product_id: UUID
    order_id: Optional[UUID] = None


class ReviewUpdate(BaseModel):
    """Schema for updating a review"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, max_length=200)
    comment: Optional[str] = None
    images: Optional[List[str]] = None


class ReviewModeration(BaseModel):
    """Schema for moderating a review"""
    is_approved: bool


class ReviewResponse(ReviewBase):
    """Schema for review response"""
    id: UUID
    product_id: UUID
    customer_id: UUID
    order_id: Optional[UUID] = None
    is_verified_purchase: bool
    is_approved: bool
    helpful_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewStats(BaseModel):
    """Schema for product review statistics"""
    average_rating: float
    total_reviews: int
    rating_distribution: dict  # {1: count, 2: count, ...}
    verified_purchase_count: int
