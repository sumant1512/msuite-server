"""
Product management routes
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Annotated, List, Optional
import uuid

from app.core.dependencies import get_db, require_ecommerce_context
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    InventoryUpdate
)
from app.services.product_service import ProductService


router = APIRouter(prefix="/products", tags=["Products"])


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: Annotated[Session, Depends(get_db)],
    ecommerce_id: Annotated[uuid.UUID, Depends(require_ecommerce_context)]
):
    """
    Create a new product with inventory
    
    Automatically creates an inventory record with initial quantity
    """
    product = ProductService.create_product(db, ecommerce_id, product_data)
    return ProductResponse.model_validate(product)


@router.get("", response_model=List[ProductResponse])
async def list_products(
    db: Annotated[Session, Depends(get_db)],
    ecommerce_id: Annotated[uuid.UUID, Depends(require_ecommerce_context)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    """
    List products with optional filters
    
    Filters:
    - category: Filter by product category
    - is_active: Filter by active status
    - min_price/max_price: Price range filter
    """
    products = ProductService.list_products(
        db,
        ecommerce_id,
        skip=skip,
        limit=limit,
        category=category,
        is_active=is_active,
        min_price=min_price,
        max_price=max_price
    )
    return [ProductResponse.model_validate(p) for p in products]


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    ecommerce_id: Annotated[uuid.UUID, Depends(require_ecommerce_context)]
):
    """Get product details with inventory"""
    product = ProductService.get_product(db, product_id)
    
    # Verify tenant access
    if product.ecommerce_id != ecommerce_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied")
    
    return ProductResponse.model_validate(product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: uuid.UUID,
    product_data: ProductUpdate,
    db: Annotated[Session, Depends(get_db)],
    ecommerce_id: Annotated[uuid.UUID, Depends(require_ecommerce_context)]
):
    """Update product details"""
    product = ProductService.get_product(db, product_id)
    
    # Verify tenant access
    if product.ecommerce_id != ecommerce_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied")
    
    product = ProductService.update_product(db, product_id, product_data)
    return ProductResponse.model_validate(product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    ecommerce_id: Annotated[uuid.UUID, Depends(require_ecommerce_context)]
):
    """Delete (deactivate) product"""
    product = ProductService.get_product(db, product_id)
    
    # Verify tenant access
    if product.ecommerce_id != ecommerce_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied")
    
    ProductService.delete_product(db, product_id)


@router.put("/{product_id}/inventory", response_model=ProductResponse)
async def update_product_inventory(
    product_id: uuid.UUID,
    inventory_data: InventoryUpdate,
    db: Annotated[Session, Depends(get_db)],
    ecommerce_id: Annotated[uuid.UUID, Depends(require_ecommerce_context)]
):
    """
    Update product inventory quantity
    
    Adjusts the available quantity (not reserved quantity)
    """
    product = ProductService.get_product(db, product_id)
    
    # Verify tenant access
    if product.ecommerce_id != ecommerce_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied")
    
    product = ProductService.update_inventory(db, product_id, inventory_data.quantity)
    return ProductResponse.model_validate(product)
