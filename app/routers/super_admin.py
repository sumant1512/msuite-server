"""
Super Admin routes for system-wide management
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Annotated, List, Optional
import uuid

from app.core.dependencies import get_db, require_super_admin
from app.models.user import User
from app.schemas.agency import AgencyCreate, AgencyUpdate, AgencyResponse
from app.schemas.subscription import (
    SubscriptionPlanCreate,
    SubscriptionPlanUpdate,
    SubscriptionPlanResponse
)
from app.services.agency_service import AgencyService
from app.services.subscription_service import SubscriptionService


router = APIRouter(prefix="/admin", tags=["Super Admin"])


# Subscription Plan Routes
@router.post(
    "/subscription-plans",
    response_model=SubscriptionPlanResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_subscription_plan(
    plan_data: SubscriptionPlanCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_super_admin)]
):
    """Create a new subscription plan (Super Admin only)"""
    plan = SubscriptionService.create_plan(db, plan_data)
    return SubscriptionPlanResponse.model_validate(plan)


@router.get("/subscription-plans", response_model=List[SubscriptionPlanResponse])
async def list_subscription_plans(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_super_admin)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    active_only: bool = False
):
    """List all subscription plans"""
    plans = SubscriptionService.list_plans(db, skip, limit, active_only)
    return [SubscriptionPlanResponse.model_validate(p) for p in plans]


@router.get("/subscription-plans/{plan_id}", response_model=SubscriptionPlanResponse)
async def get_subscription_plan(
    plan_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_super_admin)]
):
    """Get subscription plan details"""
    plan = SubscriptionService.get_plan(db, plan_id)
    return SubscriptionPlanResponse.model_validate(plan)


@router.put("/subscription-plans/{plan_id}", response_model=SubscriptionPlanResponse)
async def update_subscription_plan(
    plan_id: uuid.UUID,
    plan_data: SubscriptionPlanUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_super_admin)]
):
    """Update subscription plan"""
    plan = SubscriptionService.update_plan(db, plan_id, plan_data)
    return SubscriptionPlanResponse.model_validate(plan)


@router.delete("/subscription-plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription_plan(
    plan_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_super_admin)]
):
    """Delete (deactivate) subscription plan"""
    SubscriptionService.delete_plan(db, plan_id)


# Agency Routes
@router.post("/agencies", response_model=AgencyResponse, status_code=status.HTTP_201_CREATED)
async def create_agency(
    agency_data: AgencyCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_super_admin)]
):
    """
    Create a new agency with admin user (Super Admin only)
    
    Creates both the agency and an agency admin user account
    """
    agency = AgencyService.create_agency(db, agency_data)
    
    # Add ecommerce count
    response = AgencyResponse.model_validate(agency)
    response.ecommerce_count = AgencyService.get_ecommerce_count(db, agency.id)
    
    return response


@router.get("/agencies", response_model=List[AgencyResponse])
async def list_agencies(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_super_admin)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    active_only: bool = False
):
    """List all agencies"""
    agencies = AgencyService.list_agencies(db, skip, limit, active_only)
    
    result = []
    for agency in agencies:
        response = AgencyResponse.model_validate(agency)
        response.ecommerce_count = AgencyService.get_ecommerce_count(db, agency.id)
        result.append(response)
    
    return result


@router.get("/agencies/{agency_id}", response_model=AgencyResponse)
async def get_agency(
    agency_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_super_admin)]
):
    """Get agency details"""
    agency = AgencyService.get_agency(db, agency_id)
    
    response = AgencyResponse.model_validate(agency)
    response.ecommerce_count = AgencyService.get_ecommerce_count(db, agency.id)
    
    return response


@router.put("/agencies/{agency_id}", response_model=AgencyResponse)
async def update_agency(
    agency_id: uuid.UUID,
    agency_data: AgencyUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_super_admin)]
):
    """Update agency"""
    agency = AgencyService.update_agency(db, agency_id, agency_data)
    
    response = AgencyResponse.model_validate(agency)
    response.ecommerce_count = AgencyService.get_ecommerce_count(db, agency.id)
    
    return response


@router.delete("/agencies/{agency_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agency(
    agency_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_super_admin)]
):
    """Delete (deactivate) agency"""
    AgencyService.delete_agency(db, agency_id)
