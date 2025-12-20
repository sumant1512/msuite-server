"""
Subscription plan service for managing subscription tiers
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
import uuid

from app.models.subscription import SubscriptionPlan
from app.schemas.subscription import SubscriptionPlanCreate, SubscriptionPlanUpdate


class SubscriptionService:
    """Subscription plan service class"""
    
    @staticmethod
    def create_plan(db: Session, plan_data: SubscriptionPlanCreate) -> SubscriptionPlan:
        """Create a new subscription plan"""
        # Check if plan name already exists
        existing = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.name == plan_data.name
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subscription plan with this name already exists"
            )
        
        plan = SubscriptionPlan(
            id=uuid.uuid4(),
            **plan_data.model_dump()
        )
        
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan
    
    @staticmethod
    def get_plan(db: Session, plan_id: uuid.UUID) -> SubscriptionPlan:
        """Get subscription plan by ID"""
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.id == plan_id
        ).first()
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription plan not found"
            )
        
        return plan
    
    @staticmethod
    def list_plans(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> List[SubscriptionPlan]:
        """List all subscription plans"""
        query = db.query(SubscriptionPlan)
        
        if active_only:
            query = query.filter(SubscriptionPlan.is_active == True)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_plan(
        db: Session,
        plan_id: uuid.UUID,
        plan_data: SubscriptionPlanUpdate
    ) -> SubscriptionPlan:
        """Update subscription plan"""
        plan = SubscriptionService.get_plan(db, plan_id)
        
        update_data = plan_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(plan, field, value)
        
        db.commit()
        db.refresh(plan)
        return plan
    
    @staticmethod
    def delete_plan(db: Session, plan_id: uuid.UUID) -> None:
        """Delete (deactivate) subscription plan"""
        plan = SubscriptionService.get_plan(db, plan_id)
        
        # Check if any agencies are using this plan
        if plan.agencies:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete plan with active agencies"
            )
        
        plan.is_active = False
        db.commit()
