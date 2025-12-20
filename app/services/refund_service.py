"""
Refund service for managing order refunds
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
import uuid
from datetime import datetime

from app.models.refund import OrderRefund, RefundStatus, RefundReason
from app.models.order import Order, OrderStatus
from app.models.inventory import Inventory
from app.schemas.refund import RefundCreate, RefundUpdate


class RefundService:
    """Service for refund operations"""
    
    @staticmethod
    def create_refund(
        db: Session,
        ecommerce_id: uuid.UUID,
        refund_data: RefundCreate,
        user_id: uuid.UUID
    ) -> OrderRefund:
        """
        Create a new refund request
        """
        # Verify order exists and belongs to ecommerce
        order = db.query(Order).filter(Order.id == refund_data.order_id).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        if order.ecommerce_id != ecommerce_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this order"
            )
        
        # Validate refund amount doesn't exceed order total
        if refund_data.amount > float(order.total):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refund amount exceeds order total"
            )
        
        # Generate unique refund number
        refund_number = f"REF-{uuid.uuid4().hex[:12].upper()}"
        
        # Create refund
        refund = OrderRefund(
            order_id=refund_data.order_id,
            ecommerce_id=ecommerce_id,
            refund_number=refund_number,
            amount=refund_data.amount,
            reason=refund_data.reason,
            customer_notes=refund_data.customer_notes,
            status=RefundStatus.REQUESTED
        )
        
        db.add(refund)
        db.commit()
        db.refresh(refund)
        
        return refund
    
    @staticmethod
    def get_refund(db: Session, refund_id: uuid.UUID) -> OrderRefund:
        """Get a refund by ID"""
        refund = db.query(OrderRefund).filter(OrderRefund.id == refund_id).first()
        if not refund:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Refund not found"
            )
        return refund
    
    @staticmethod
    def list_refunds(
        db: Session,
        ecommerce_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[RefundStatus] = None
    ) -> List[OrderRefund]:
        """List refunds for an ecommerce store"""
        query = db.query(OrderRefund).filter(OrderRefund.ecommerce_id == ecommerce_id)
        
        if status_filter:
            query = query.filter(OrderRefund.status == status_filter)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def approve_refund(
        db: Session,
        refund_id: uuid.UUID,
        admin_user_id: uuid.UUID,
        approve: bool,
        admin_notes: Optional[str] = None
    ) -> OrderRefund:
        """
        Approve or reject a refund request
        """
        refund = RefundService.get_refund(db, refund_id)
        
        if refund.status != RefundStatus.REQUESTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refund has already been processed"
            )
        
        if approve:
            refund.status = RefundStatus.APPROVED
            refund.approved_by_id = admin_user_id
            refund.approved_at = datetime.utcnow()
        else:
            refund.status = RefundStatus.REJECTED
        
        if admin_notes:
            refund.admin_notes = admin_notes
        
        db.commit()
        db.refresh(refund)
        
        return refund
    
    @staticmethod
    def process_refund(
        db: Session,
        refund_id: uuid.UUID,
        admin_user_id: uuid.UUID,
        transaction_id: str,
        refund_method: str,
        return_inventory: bool = True
    ) -> OrderRefund:
        """
        Process an approved refund and optionally return inventory
        """
        refund = RefundService.get_refund(db, refund_id)
        
        if refund.status != RefundStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refund must be approved before processing"
            )
        
        # Update refund status
        refund.status = RefundStatus.PROCESSING
        refund.processed_by_id = admin_user_id
        refund.processed_at = datetime.utcnow()
        refund.transaction_id = transaction_id
        refund.refund_method = refund_method
        
        # Return inventory if requested
        if return_inventory:
            order = refund.order
            for item in order.items:
                # Find inventory record
                inventory = db.query(Inventory).filter(
                    Inventory.product_id == item.product_id,
                    Inventory.ecommerce_id == order.ecommerce_id
                ).first()
                
                if inventory:
                    inventory.quantity += item.quantity
            
            refund.inventory_returned = True
        
        # Mark refund as completed
        refund.status = RefundStatus.COMPLETED
        refund.completed_at = datetime.utcnow()
        
        # Update order status if full refund
        order = refund.order
        if refund.amount >= float(order.total):
            order.status = OrderStatus.REFUNDED
        
        db.commit()
        db.refresh(refund)
        
        return refund
    
    @staticmethod
    def update_refund(
        db: Session,
        refund_id: uuid.UUID,
        refund_update: RefundUpdate
    ) -> OrderRefund:
        """Update refund details (admin only)"""
        refund = RefundService.get_refund(db, refund_id)
        
        update_data = refund_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(refund, field, value)
        
        db.commit()
        db.refresh(refund)
        
        return refund
