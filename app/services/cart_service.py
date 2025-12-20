"""
Service for shopping cart management
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
import uuid

from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.models.customer import Customer
from app.schemas.cart import CartItemCreate, CartItemUpdate


class CartService:
    @staticmethod
    def _get_or_create_cart(db: Session, ecommerce_id: uuid.UUID, customer_id: uuid.UUID) -> Cart:
        cart = db.query(Cart).filter(
            Cart.ecommerce_id == ecommerce_id,
            Cart.customer_id == customer_id
        ).first()
        if cart is None:
            # Validate customer belongs to tenant
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            if customer is None or customer.ecommerce_id != ecommerce_id:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
            cart = Cart(ecommerce_id=ecommerce_id, customer_id=customer_id)
            db.add(cart)
            db.flush()
        return cart

    @staticmethod
    def get_cart(db: Session, ecommerce_id: uuid.UUID, customer_id: uuid.UUID) -> Cart:
        cart = db.query(Cart).filter(
            Cart.ecommerce_id == ecommerce_id,
            Cart.customer_id == customer_id
        ).first()
        if cart is None:
            # Return empty cart (create lazily)
            cart = Cart(ecommerce_id=ecommerce_id, customer_id=customer_id)
            db.add(cart)
            db.flush()
        return cart

    @staticmethod
    def add_item(
        db: Session,
        ecommerce_id: uuid.UUID,
        customer_id: uuid.UUID,
        item: CartItemCreate
    ) -> Cart:
        cart = CartService._get_or_create_cart(db, ecommerce_id, customer_id)
        # Validate product belongs to tenant
        product = db.query(Product).filter(
            Product.id == item.product_id,
            Product.ecommerce_id == ecommerce_id,
            Product.is_active == True
        ).first()
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        # Check if item exists -> update qty
        existing = db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == item.product_id
        ).first()
        if existing:
            existing.quantity += item.quantity
            existing.total_price = float(existing.quantity) * float(existing.unit_price)
        else:
            ci = CartItem(
                cart_id=cart.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=product.price,
                total_price=float(item.quantity) * float(product.price)
            )
            db.add(ci)
        db.commit()
        db.refresh(cart)
        return cart

    @staticmethod
    def update_item(
        db: Session,
        ecommerce_id: uuid.UUID,
        customer_id: uuid.UUID,
        product_id: uuid.UUID,
        update: CartItemUpdate
    ) -> Cart:
        cart = CartService._get_or_create_cart(db, ecommerce_id, customer_id)
        ci = db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        ).first()
        if ci is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
        ci.quantity = update.quantity
        ci.total_price = float(update.quantity) * float(ci.unit_price)
        db.commit()
        db.refresh(cart)
        return cart

    @staticmethod
    def remove_item(
        db: Session,
        ecommerce_id: uuid.UUID,
        customer_id: uuid.UUID,
        product_id: uuid.UUID
    ) -> Cart:
        cart = CartService._get_or_create_cart(db, ecommerce_id, customer_id)
        ci = db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        ).first()
        if ci is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
        db.delete(ci)
        db.commit()
        db.refresh(cart)
        return cart

    @staticmethod
    def clear_cart(db: Session, ecommerce_id: uuid.UUID, customer_id: uuid.UUID) -> Cart:
        cart = CartService._get_or_create_cart(db, ecommerce_id, customer_id)
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        db.commit()
        db.refresh(cart)
        return cart
