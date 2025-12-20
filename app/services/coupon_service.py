"""
Coupon service for business logic
"""
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.models.coupon import Coupon
from app.schemas.coupon import CouponCreate, CouponUpdate


class CouponService:
    """Service for coupon operations"""

    @staticmethod
    def create_coupon(
        db: Session,
        ecommerce_id: UUID,
        coupon_data: CouponCreate
    ) -> Coupon:
        """Create a new coupon"""
        coupon = Coupon(
            ecommerce_id=ecommerce_id,
            **coupon_data.model_dump()
        )
        db.add(coupon)
        db.commit()
        db.refresh(coupon)
        return coupon

    @staticmethod
    def get_coupon_by_id(
        db: Session,
        coupon_id: UUID,
        ecommerce_id: UUID
    ) -> Optional[Coupon]:
        """Get coupon by ID"""
        return db.query(Coupon).filter(
            and_(
                Coupon.id == coupon_id,
                Coupon.ecommerce_id == ecommerce_id
            )
        ).first()

    @staticmethod
    def get_coupon_by_code(
        db: Session,
        code: str,
        ecommerce_id: UUID
    ) -> Optional[Coupon]:
        """Get coupon by code"""
        return db.query(Coupon).filter(
            and_(
                Coupon.code == code,
                Coupon.ecommerce_id == ecommerce_id
            )
        ).first()

    @staticmethod
    def get_coupons(
        db: Session,
        ecommerce_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Coupon]:
        """Get all coupons for an ecommerce"""
        return db.query(Coupon).filter(
            Coupon.ecommerce_id == ecommerce_id
        ).order_by(Coupon.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_coupon(
        db: Session,
        coupon: Coupon,
        coupon_data: CouponUpdate
    ) -> Coupon:
        """Update a coupon"""
        update_data = coupon_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(coupon, field, value)
        
        db.commit()
        db.refresh(coupon)
        return coupon

    @staticmethod
    def delete_coupon(
        db: Session,
        coupon: Coupon
    ) -> None:
        """Delete a coupon"""
        db.delete(coupon)
        db.commit()

    @staticmethod
    def validate_coupon(
        db: Session,
        code: str,
        ecommerce_id: UUID,
        order_amount: float,
        customer_id: Optional[UUID] = None
    ) -> tuple[bool, Optional[float], Optional[str]]:
        """
        Validate a coupon and calculate discount
        Returns: (is_valid, discount_amount, message)
        """
        coupon = CouponService.get_coupon_by_code(db, code, ecommerce_id)
        
        if not coupon:
            return False, None, "Coupon not found"
        
        if not coupon.is_active:
            return False, None, "Coupon is not active"
        
        # Check validity period
        now = datetime.now(datetime.timezone.utc)
        if coupon.valid_from > now:
            return False, None, "Coupon is not yet valid"
        
        if coupon.valid_until and coupon.valid_until < now:
            return False, None, "Coupon has expired"
        
        # Check usage limits
        if coupon.usage_limit and coupon.usage_count >= coupon.usage_limit:
            return False, None, "Coupon usage limit reached"
        
        # Check minimum purchase amount
        if coupon.minimum_purchase_amount and order_amount < coupon.minimum_purchase_amount:
            return False, None, f"Minimum purchase amount is ${coupon.minimum_purchase_amount}"
        
        # Calculate discount
        discount_amount = 0.0
        if coupon.discount_type == "PERCENTAGE":
            discount_amount = (order_amount * coupon.discount_value) / 100
        elif coupon.discount_type == "FIXED_AMOUNT":
            discount_amount = min(coupon.discount_value, order_amount)
        elif coupon.discount_type == "FREE_SHIPPING":
            discount_amount = 0.0  # Handle in shipping calculation
        
        return True, discount_amount, "Coupon is valid"

    @staticmethod
    def increment_usage(
        db: Session,
        coupon: Coupon
    ) -> Coupon:
        """Increment coupon usage count"""
        coupon.usage_count += 1
        db.commit()
        db.refresh(coupon)
        return coupon
