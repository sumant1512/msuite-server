"""
Coupon router for API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.coupon import CouponCreate, CouponUpdate, CouponResponse, CouponValidation
from app.services.coupon_service import CouponService
from app.enums.user_role import UserRole

router = APIRouter(prefix="/coupons", tags=["Coupons"])


@router.post("/", response_model=CouponResponse, status_code=status.HTTP_201_CREATED)
def create_coupon(
    coupon_data: CouponCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new coupon (Agency Admin or Ecommerce user only)"""
    if current_user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admins cannot create coupons directly"
        )
    
    if not current_user.ecommerce_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with an ecommerce"
        )
    
    # Check if coupon code already exists
    existing = CouponService.get_coupon_by_code(
        db, coupon_data.code, current_user.ecommerce_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon code already exists"
        )
    
    coupon = CouponService.create_coupon(
        db, current_user.ecommerce_id, coupon_data
    )
    return coupon


@router.get("/", response_model=List[CouponResponse])
def get_coupons(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all coupons for current ecommerce"""
    if not current_user.ecommerce_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with an ecommerce"
        )
    
    coupons = CouponService.get_coupons(
        db, current_user.ecommerce_id, skip, limit
    )
    return coupons


@router.get("/{coupon_id}", response_model=CouponResponse)
def get_coupon(
    coupon_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific coupon by ID"""
    if not current_user.ecommerce_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with an ecommerce"
        )
    
    coupon = CouponService.get_coupon_by_id(
        db, coupon_id, current_user.ecommerce_id
    )
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    return coupon


@router.put("/{coupon_id}", response_model=CouponResponse)
def update_coupon(
    coupon_id: UUID,
    coupon_data: CouponUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a coupon"""
    if not current_user.ecommerce_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with an ecommerce"
        )
    
    coupon = CouponService.get_coupon_by_id(
        db, coupon_id, current_user.ecommerce_id
    )
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    updated_coupon = CouponService.update_coupon(db, coupon, coupon_data)
    return updated_coupon


@router.delete("/{coupon_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_coupon(
    coupon_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a coupon"""
    if not current_user.ecommerce_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with an ecommerce"
        )
    
    coupon = CouponService.get_coupon_by_id(
        db, coupon_id, current_user.ecommerce_id
    )
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    CouponService.delete_coupon(db, coupon)


@router.post("/validate/{code}", response_model=CouponValidation)
def validate_coupon(
    code: str,
    order_amount: float = Query(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate a coupon code and calculate discount"""
    if not current_user.ecommerce_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with an ecommerce"
        )
    
    is_valid, discount_amount, message = CouponService.validate_coupon(
        db, code, current_user.ecommerce_id, order_amount, current_user.id
    )
    
    return CouponValidation(
        is_valid=is_valid,
        discount_amount=discount_amount,
        message=message
    )
