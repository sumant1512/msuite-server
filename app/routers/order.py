"""
Order management routes
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Annotated, List, Optional
import uuid

from app.core.dependencies import get_db, require_ecommerce_context
from app.schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderStatus
)
from app.services.order_service import OrderService


router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: Annotated[Session, Depends(get_db)],
    ecommerce_id: Annotated[uuid.UUID, Depends(require_ecommerce_context)]
):
    """
    Create a new order
    
    - Validates product availability
    - Reserves inventory for ordered items
    - Calculates totals including tax and shipping
    """
    order = OrderService.create_order(db, ecommerce_id, order_data)
    return OrderResponse.model_validate(order)


@router.get("", response_model=List[OrderResponse])
async def list_orders(
    db: Annotated[Session, Depends(get_db)],
    ecommerce_id: Annotated[uuid.UUID, Depends(require_ecommerce_context)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[OrderStatus] = None,
    customer_id: Optional[uuid.UUID] = None
):
    """
    List orders with optional filters
    
    Filters:
    - status: Filter by order status (PENDING, CONFIRMED, etc.)
    - customer_id: Filter by customer
    """
    orders = OrderService.list_orders(
        db,
        ecommerce_id,
        skip=skip,
        limit=limit,
        status=status,
        customer_id=customer_id
    )
    return [OrderResponse.model_validate(o) for o in orders]


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    ecommerce_id: Annotated[uuid.UUID, Depends(require_ecommerce_context)]
):
    """Get order details with items"""
    order = OrderService.get_order(db, order_id)
    
    # Verify tenant access
    if order.ecommerce_id != ecommerce_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied")
    
    return OrderResponse.model_validate(order)


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: uuid.UUID,
    order_data: OrderUpdate,
    db: Annotated[Session, Depends(get_db)],
    ecommerce_id: Annotated[uuid.UUID, Depends(require_ecommerce_context)]
):
    """
    Update order status
    
    Status changes affect inventory:
    - CANCELLED: Releases reserved inventory
    - DELIVERED/COMPLETED: Removes reserved inventory
    """
    order = OrderService.get_order(db, order_id)
    
    # Verify tenant access
    if order.ecommerce_id != ecommerce_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied")
    
    order = OrderService.update_order(db, order_id, order_data)
    return OrderResponse.model_validate(order)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    ecommerce_id: Annotated[uuid.UUID, Depends(require_ecommerce_context)]
):
    """
    Cancel an order
    
    - Releases reserved inventory back to available stock
    - Can only cancel PENDING or CONFIRMED orders
    """
    order = OrderService.get_order(db, order_id)
    
    # Verify tenant access
    if order.ecommerce_id != ecommerce_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied")
    
    order = OrderService.cancel_order(db, order_id)
    return OrderResponse.model_validate(order)
