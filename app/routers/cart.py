"""
Shopping cart routes
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Annotated
import uuid

from app.core.dependencies import get_db, require_ecommerce_context
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartResponse, CartItemResponse
from app.services.cart_service import CartService


router = APIRouter(prefix="/cart", tags=["Cart"])


def _to_response(cart) -> CartResponse:
    items = [
        CartItemResponse(
            product_id=i.product_id,
            quantity=i.quantity,
            unit_price=float(i.unit_price),
            total_price=float(i.total_price)
        ) for i in cart.items
    ]
    subtotal = sum(i.total_price for i in items)
    return CartResponse(
        id=cart.id,
        ecommerce_id=cart.ecommerce_id,
        customer_id=cart.customer_id,
        items=items,
        subtotal=float(subtotal),
        total_items=sum(i.quantity for i in items)
    )


@router.get("/{customer_id}", response_model=CartResponse)
async def get_cart(
    customer_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    ecommerce_id: Annotated[uuid.UUID, Depends(require_ecommerce_context)]
):
    cart = CartService.get_cart(db, ecommerce_id, customer_id)
    return _to_response(cart)


@router.post("/{customer_id}/items", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def add_item(
    customer_id: uuid.UUID,
    item: CartItemCreate,
    db: Annotated[Session, Depends(get_db)],
    ecommerce_id: Annotated[uuid.UUID, Depends(require_ecommerce_context)]
):
    cart = CartService.add_item(db, ecommerce_id, customer_id, item)
    return _to_response(cart)


@router.put("/{customer_id}/items/{product_id}", response_model=CartResponse)
async def update_item(
    customer_id: uuid.UUID,
    product_id: uuid.UUID,
    update: CartItemUpdate,
    db: Annotated[Session, Depends(get_db)],
    ecommerce_id: Annotated[uuid.UUID, Depends(require_ecommerce_context)]
):
    cart = CartService.update_item(db, ecommerce_id, customer_id, product_id, update)
    return _to_response(cart)


@router.delete("/{customer_id}/items/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item(
    customer_id: uuid.UUID,
    product_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    ecommerce_id: Annotated[uuid.UUID, Depends(require_ecommerce_context)]
):
    CartService.remove_item(db, ecommerce_id, customer_id, product_id)


@router.post("/{customer_id}/clear", response_model=CartResponse)
async def clear_cart(
    customer_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    ecommerce_id: Annotated[uuid.UUID, Depends(require_ecommerce_context)]
):
    cart = CartService.clear_cart(db, ecommerce_id, customer_id)
    return _to_response(cart)
