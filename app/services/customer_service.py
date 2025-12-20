"""
Customer service for managing e-commerce customers
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from typing import List
import uuid

from app.models.customer import Customer
from app.models.order import Order
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:
    """Customer service class"""
    
    @staticmethod
    def create_customer(
        db: Session,
        ecommerce_id: uuid.UUID,
        customer_data: CustomerCreate
    ) -> Customer:
        """Create a new customer"""
        # Check if email already exists for this e-commerce
        existing = db.query(Customer).filter(
            Customer.ecommerce_id == ecommerce_id,
            Customer.email == customer_data.email
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer with this email already exists"
            )
        
        customer = Customer(
            id=uuid.uuid4(),
            ecommerce_id=ecommerce_id,
            **customer_data.model_dump()
        )
        
        db.add(customer)
        db.commit()
        db.refresh(customer)
        
        return customer
    
    @staticmethod
    def get_customer(db: Session, customer_id: uuid.UUID) -> Customer:
        """Get customer by ID"""
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        return customer
    
    @staticmethod
    def list_customers(
        db: Session,
        ecommerce_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Customer]:
        """List customers for an e-commerce tenant"""
        return db.query(Customer).filter(
            Customer.ecommerce_id == ecommerce_id
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_customer(
        db: Session,
        customer_id: uuid.UUID,
        customer_data: CustomerUpdate
    ) -> Customer:
        """Update customer"""
        customer = CustomerService.get_customer(db, customer_id)
        
        update_data = customer_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(customer, field, value)
        
        db.commit()
        db.refresh(customer)
        return customer
    
    @staticmethod
    def delete_customer(db: Session, customer_id: uuid.UUID) -> None:
        """Delete customer"""
        customer = CustomerService.get_customer(db, customer_id)
        db.delete(customer)
        db.commit()
    
    @staticmethod
    def get_customer_stats(db: Session, customer_id: uuid.UUID) -> dict:
        """Get customer order statistics"""
        total_orders = db.query(func.count(Order.id)).filter(
            Order.customer_id == customer_id
        ).scalar()
        
        total_spent = db.query(func.sum(Order.total)).filter(
            Order.customer_id == customer_id
        ).scalar() or 0.0
        
        return {
            "total_orders": total_orders,
            "total_spent": float(total_spent)
        }
