"""
Refund routes for order refund management
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Annotated, List, Optional
import uuid

from app.core.dependencies import (
    get_db,
    require_ecommerce_user,
    require_ecommerce_context,
    validate_tenant_access
)
from app.models.user import User
from app.models.refund import RefundStatus
from app.schemas.refund import (
    RefundCreate,
    RefundUpdate,
    RefundResponse,
    RefundApproval
)
from app.services.refund_service import RefundService


router = APIRouter(prefix="/refunds", tags=["Refunds"])


@router.post("/", response_model=RefundResponse, status_code=status.HTTP_201_CREATED)
async def create_refund(
    refund_data: RefundCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_ecommerce_user)],
    ecommerce_id: Annotated[uuid.UUID, Depends(require_ecommerce_context)]
):
    """
    Create a new refund request
    
    Customers can request refunds for their orders.
    """
    refund = RefundService.create_refund(db, ecommerce_id, refund_data, current_user.id)
    return RefundResponse.model_validate(refund)


@router.get("/", response_model=List[RefundResponse])
async def list_refunds(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_ecommerce_user)],
    ecommerce_id: Annotated[uuid.UUID, Depends(require_ecommerce_context)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status_filter: Optional[RefundStatus] = None
):
    """List all refunds for the ecommerce store"""
    refunds = RefundService.list_refunds(db, ecommerce_id, skip, limit, status_filter)
    return [RefundResponse.model_validate(r) for r in refunds]


@router.get("/{refund_id}", response_model=RefundResponse)
async def get_refund(
    refund_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_ecommerce_user)],
    ecommerce_id: Annotated[uuid.UUID, Depends(require_ecommerce_context)]
):
    """Get a specific refund by ID"""
    refund = RefundService.get_refund(db, refund_id)
    
    # Validate tenant access
    validate_tenant_access(refund.ecommerce_id, ecommerce_id)
    
    return RefundResponse.model_validate(refund)


@router.post("/{refund_id}/approve", response_model=RefundResponse)
async def approve_refund(
    refund_id: uuid.UUID,
    approval_data: RefundApproval,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_ecommerce_user)],
    ecommerce_id: Annotated[uuid.UUID, Depends(require_ecommerce_context)]
):
    """
    Approve or reject a refund request (Admin only)
    
    Only ecommerce admins can approve/reject refunds.
    """
    refund = RefundService.get_refund(db, refund_id)
    
    # Validate tenant access
    validate_tenant_access(refund.ecommerce_id, ecommerce_id)
    
    refund = RefundService.approve_refund(
        db,
        refund_id,
        current_user.id,
        approval_data.approve,
        approval_data.admin_notes
    )
    
    return RefundResponse.model_validate(refund)


@router.post("/{refund_id}/process", response_model=RefundResponse)
async def process_refund(
    refund_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_ecommerce_user)],
    ecommerce_id: Annotated[uuid.UUID, Depends(require_ecommerce_context)],
    transaction_id: str = Query(..., description="Payment gateway transaction ID"),
    refund_method: str = Query(..., description="Refund method used"),
    return_inventory: bool = Query(True, description="Return items to inventory")
):
    """
    Process an approved refund (Admin only)
    
    This endpoint processes the actual refund transaction and optionally returns inventory.
    """
    refund = RefundService.get_refund(db, refund_id)
    
    # Validate tenant access
    validate_tenant_access(refund.ecommerce_id, ecommerce_id)
    
    refund = RefundService.process_refund(
        db,
        refund_id,
        current_user.id,
        transaction_id,
        refund_method,
        return_inventory
    )
    
    return RefundResponse.model_validate(refund)


@router.patch("/{refund_id}", response_model=RefundResponse)
async def update_refund(
    refund_id: uuid.UUID,
    refund_update: RefundUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_ecommerce_user)],
    ecommerce_id: Annotated[uuid.UUID, Depends(require_ecommerce_context)]
):
    """
    Update refund details (Admin only)
    """
    refund = RefundService.get_refund(db, refund_id)
    
    # Validate tenant access
    validate_tenant_access(refund.ecommerce_id, ecommerce_id)
    
    refund = RefundService.update_refund(db, refund_id, refund_update)
    
    return RefundResponse.model_validate(refund)
