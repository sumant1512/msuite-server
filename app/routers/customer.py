"""
Customer management routes
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Annotated, List
import uuid

from app.core.dependencies import get_db, require_ecommerce_context
from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerStats
)
from app.services.customer_service import CustomerService


router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    db: Annotated[Session, Depends(get_db)],
    ecommerce_id: Annotated[uuid.UUID, Depends(require_ecommerce_context)]
):
    """Create a new customer profile"""
    customer = CustomerService.create_customer(db, ecommerce_id, customer_data)
    return CustomerResponse.model_validate(customer)


@router.get("", response_model=List[CustomerResponse])
async def list_customers(
    db: Annotated[Session, Depends(get_db)],
    ecommerce_id: Annotated[uuid.UUID, Depends(require_ecommerce_context)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """List all customers"""
    customers = CustomerService.list_customers(db, ecommerce_id, skip, limit)
    return [CustomerResponse.model_validate(c) for c in customers]


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    ecommerce_id: Annotated[uuid.UUID, Depends(require_ecommerce_context)]
):
    """Get customer details"""
    customer = CustomerService.get_customer(db, customer_id)
    
    # Verify tenant access
    if customer.ecommerce_id != ecommerce_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied")
    
    return CustomerResponse.model_validate(customer)


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: uuid.UUID,
    customer_data: CustomerUpdate,
    db: Annotated[Session, Depends(get_db)],
    ecommerce_id: Annotated[uuid.UUID, Depends(require_ecommerce_context)]
):
    """Update customer details"""
    customer = CustomerService.get_customer(db, customer_id)
    
    # Verify tenant access
    if customer.ecommerce_id != ecommerce_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied")
    
    customer = CustomerService.update_customer(db, customer_id, customer_data)
    return CustomerResponse.model_validate(customer)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    ecommerce_id: Annotated[uuid.UUID, Depends(require_ecommerce_context)]
):
    """Delete customer"""
    customer = CustomerService.get_customer(db, customer_id)
    
    # Verify tenant access
    if customer.ecommerce_id != ecommerce_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied")
    
    CustomerService.delete_customer(db, customer_id)


@router.get("/{customer_id}/stats", response_model=CustomerStats)
async def get_customer_stats(
    customer_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    ecommerce_id: Annotated[uuid.UUID, Depends(require_ecommerce_context)]
):
    """
    Get customer statistics
    
    Returns:
    - Total orders count
    - Total amount spent
    - Customer profile
    """
    customer = CustomerService.get_customer(db, customer_id)
    
    # Verify tenant access
    if customer.ecommerce_id != ecommerce_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied")
    
    return CustomerService.get_customer_stats(db, customer_id)
