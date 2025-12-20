"""
Order service for managing e-commerce orders
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime
import uuid

from app.models.order import Order, OrderItem, OrderStatus, PaymentStatus
from app.models.product import Product
from app.models.inventory import Inventory
from app.schemas.order import OrderCreate, OrderUpdate
from app.services.customer_service import CustomerService


class OrderService:
    """Order service class"""
    
    @staticmethod
    def generate_order_number() -> str:
        """Generate unique order number"""
        date_str = datetime.utcnow().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"ORD-{date_str}-{unique_id}"
    
    @staticmethod
    def create_order(
        db: Session,
        ecommerce_id: uuid.UUID,
        order_data: OrderCreate
    ) -> Order:
        """Create a new order"""
        # Verify customer exists and belongs to this e-commerce
        customer = CustomerService.get_customer(db, order_data.customer_id)
        if customer.ecommerce_id != ecommerce_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Customer does not belong to this e-commerce"
            )
        
        # Calculate order totals
        subtotal = 0.0
        order_items_data = []
        
        for item in order_data.items:
            # Get product
            product = db.query(Product).filter(
                Product.id == item.product_id,
                Product.ecommerce_id == ecommerce_id
            ).first()
            
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product {item.product_id} not found"
                )
            
            if not product.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product {product.name} is not active"
                )
            
            # Check inventory
            inventory = db.query(Inventory).filter(
                Inventory.product_id == product.id
            ).first()
            
            if not inventory or inventory.available < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient inventory for {product.name}"
                )
            
            # Calculate item total
            item_total = float(product.price) * item.quantity
            subtotal += item_total
            
            order_items_data.append({
                "product_id": product.id,
                "quantity": item.quantity,
                "unit_price": float(product.price),
                "total_price": item_total,
                "variant": item.variant
            })
        
        # Calculate tax and total (assuming 8.5% tax rate)
        tax = subtotal * 0.085
        shipping = 10.0  # Flat shipping rate
        total = subtotal + tax + shipping
        
        # Create order
        order = Order(
            id=uuid.uuid4(),
            ecommerce_id=ecommerce_id,
            customer_id=order_data.customer_id,
            order_number=OrderService.generate_order_number(),
            subtotal=subtotal,
            tax=tax,
            shipping=shipping,
            total=total,
            shipping_address=order_data.shipping_address,
            billing_address=order_data.billing_address,
            notes=order_data.notes
        )
        
        db.add(order)
        db.flush()
        
        # Create order items and reserve inventory
        for item_data in order_items_data:
            order_item = OrderItem(
                id=uuid.uuid4(),
                order_id=order.id,
                **item_data
            )
            db.add(order_item)
            
            # Reserve inventory
            inventory = db.query(Inventory).filter(
                Inventory.product_id == item_data["product_id"]
            ).first()
            inventory.reserved += item_data["quantity"]
        
        db.commit()
        db.refresh(order)
        
        return order
    
    @staticmethod
    def get_order(db: Session, order_id: uuid.UUID) -> Order:
        """Get order by ID"""
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        return order
    
    @staticmethod
    def list_orders(
        db: Session,
        ecommerce_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[OrderStatus] = None,
        customer_id: Optional[uuid.UUID] = None
    ) -> List[Order]:
        """List orders for an e-commerce tenant"""
        query = db.query(Order).filter(Order.ecommerce_id == ecommerce_id)
        
        if status_filter:
            query = query.filter(Order.status == status_filter)
        
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)
        
        return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_order(
        db: Session,
        order_id: uuid.UUID,
        order_data: OrderUpdate
    ) -> Order:
        """Update order"""
        order = OrderService.get_order(db, order_id)
        
        # If status is being changed to DELIVERED, deduct from inventory
        if order_data.status and order_data.status != order.status:
            if order_data.status == OrderStatus.DELIVERED:
                for item in order.items:
                    inventory = db.query(Inventory).filter(
                        Inventory.product_id == item.product_id
                    ).first()
                    if inventory:
                        inventory.quantity -= item.quantity
                        inventory.reserved -= item.quantity
            
            # If cancelled or refunded, release reserved inventory
            elif order_data.status in [OrderStatus.CANCELLED, OrderStatus.REFUNDED]:
                for item in order.items:
                    inventory = db.query(Inventory).filter(
                        Inventory.product_id == item.product_id
                    ).first()
                    if inventory:
                        inventory.reserved -= item.quantity
        
        update_data = order_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(order, field, value)
        
        db.commit()
        db.refresh(order)
        return order
    
    @staticmethod
    def cancel_order(db: Session, order_id: uuid.UUID) -> Order:
        """Cancel an order"""
        order = OrderService.get_order(db, order_id)
        
        if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel order in current status"
            )
        
        # Release reserved inventory
        for item in order.items:
            inventory = db.query(Inventory).filter(
                Inventory.product_id == item.product_id
            ).first()
            if inventory:
                inventory.reserved -= item.quantity
        
        order.status = OrderStatus.CANCELLED
        db.commit()
        db.refresh(order)
        
        return order
