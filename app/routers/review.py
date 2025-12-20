"""
Product review router for API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.review import (
    ReviewCreate, ReviewUpdate, ReviewResponse, 
    ReviewModeration, ReviewStats
)
from app.services.review_service import ReviewService
from app.enums.user_role import UserRole

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new product review (Customer only)"""
    if not current_user.ecommerce_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with an ecommerce"
        )
    
    # Get customer_id from current user (assuming user has a customer relationship)
    # For now, we'll use the user's ID as customer_id
    # In production, you'd need proper customer lookup
    from app.models.customer import Customer
    from sqlalchemy import select
    
    customer = db.query(Customer).filter(Customer.email == current_user.email).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found"
        )
    
    review = ReviewService.create_review(db, customer.id, review_data)
    return review


@router.get("/product/{product_id}", response_model=List[ReviewResponse])
def get_product_reviews(
    product_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    approved_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all reviews for a product (public endpoint)"""
    reviews = ReviewService.get_product_reviews(
        db, product_id, skip, limit, approved_only
    )
    return reviews


@router.get("/product/{product_id}/stats", response_model=ReviewStats)
def get_product_review_stats(
    product_id: UUID,
    db: Session = Depends(get_db)
):
    """Get review statistics for a product (public endpoint)"""
    stats = ReviewService.get_product_review_stats(db, product_id)
    return stats


@router.get("/my-reviews", response_model=List[ReviewResponse])
def get_my_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all reviews by current customer"""
    from app.models.customer import Customer
    from sqlalchemy import select
    
    customer = db.query(Customer).filter(Customer.email == current_user.email).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found"
        )
    
    reviews = ReviewService.get_customer_reviews(db, customer.id, skip, limit)
    return reviews


@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(
    review_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific review by ID"""
    review = ReviewService.get_review_by_id(db, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    return review


@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: UUID,
    review_data: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a review (owner only)"""
    review = ReviewService.get_review_by_id(db, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Get customer to verify ownership
    from app.models.customer import Customer
    from sqlalchemy import select
    
    customer = db.query(Customer).filter(Customer.email == current_user.email).first()
    
    if not customer or review.customer_id != customer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this review"
        )
    
    updated_review = ReviewService.update_review(db, review, review_data)
    return updated_review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a review (owner or admin)"""
    review = ReviewService.get_review_by_id(db, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Get customer to verify ownership
    from app.models.customer import Customer
    from sqlalchemy import select
    
    customer = db.query(Customer).filter(Customer.email == current_user.email).first()
    
    # Allow owner or admin to delete
    is_owner = customer and review.customer_id == customer.id
    is_admin = current_user.role in [UserRole.SUPER_ADMIN, UserRole.AGENCY_ADMIN]
    
    if not (is_owner or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this review"
        )
    
    ReviewService.delete_review(db, review)


@router.patch("/{review_id}/moderate", response_model=ReviewResponse)
def moderate_review(
    review_id: UUID,
    moderation: ReviewModeration,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Moderate a review (Admin only)"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.AGENCY_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can moderate reviews"
        )
    
    review = ReviewService.get_review_by_id(db, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    moderated_review = ReviewService.moderate_review(
        db, review, moderation.is_approved
    )
    return moderated_review


@router.post("/{review_id}/helpful", response_model=ReviewResponse)
def mark_review_helpful(
    review_id: UUID,
    db: Session = Depends(get_db)
):
    """Mark a review as helpful (public endpoint)"""
    review = ReviewService.get_review_by_id(db, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    updated_review = ReviewService.increment_helpful_count(db, review)
    return updated_review
