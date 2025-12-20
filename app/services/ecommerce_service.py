"""
E-commerce service for managing tenant stores
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from typing import List, Optional
import uuid
import secrets

from app.models.ecommerce import Ecommerce
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.models.customer import Customer
from app.schemas.ecommerce import EcommerceCreate, EcommerceUpdate, EcommerceStats
from app.core.security import get_password_hash
from app.enums.user_role import UserRole
from app.services.agency_service import AgencyService


class EcommerceService:
    """E-commerce service class"""
    
    @staticmethod
    def create_ecommerce(
        db: Session,
        agency_id: uuid.UUID,
        ecommerce_data: EcommerceCreate
    ) -> Ecommerce:
        """Create a new e-commerce tenant"""
        # Verify agency exists
        agency = AgencyService.get_agency(db, agency_id)
        
        # Validate subscription status
        from app.models.agency import SubscriptionStatus
        from datetime import datetime
        
        if agency.subscription_status not in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Cannot create e-commerce store. Agency subscription is {agency.subscription_status.value}"
            )
        
        # Check if subscription has expired
        if agency.subscription_expires_at and agency.subscription_expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Agency subscription has expired. Please renew to create new e-commerce stores."
            )
        
        # Check tenant limit
        current_count = AgencyService.get_ecommerce_count(db, agency_id)
        if current_count >= agency.max_ecommerce:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Agency has reached maximum e-commerce limit ({agency.max_ecommerce})"
            )
        
        # Check if domain already exists
        existing = db.query(Ecommerce).filter(
            Ecommerce.domain == ecommerce_data.domain
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Domain already in use"
            )
        
        # Check if admin email exists
        existing_user = db.query(User).filter(
            User.email == ecommerce_data.admin_email
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin email already registered"
            )
        
        # Create e-commerce tenant
        ecommerce = Ecommerce(
            id=uuid.uuid4(),
            agency_id=agency_id,
            name=ecommerce_data.name,
            domain=ecommerce_data.domain,
            description=ecommerce_data.description,
            settings=ecommerce_data.settings,
            api_key=secrets.token_urlsafe(32)
        )
        
        db.add(ecommerce)
        db.flush()
        
        # Create e-commerce admin user
        admin_user = User(
            id=uuid.uuid4(),
            email=ecommerce_data.admin_email,
            full_name=ecommerce_data.admin_name,
            hashed_password=get_password_hash(ecommerce_data.admin_password),
            role=UserRole.ECOMMERCE,
            agency_id=agency_id,
            ecommerce_id=ecommerce.id,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(ecommerce)
        
        return ecommerce
    
    @staticmethod
    def get_ecommerce(db: Session, ecommerce_id: uuid.UUID) -> Ecommerce:
        """Get e-commerce by ID"""
        ecommerce = db.query(Ecommerce).filter(Ecommerce.id == ecommerce_id).first()
        
        if not ecommerce:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="E-commerce tenant not found"
            )
        
        return ecommerce
    
    @staticmethod
    def list_ecommerce(
        db: Session,
        agency_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Ecommerce]:
        """List e-commerce tenants"""
        query = db.query(Ecommerce)
        
        if agency_id:
            query = query.filter(Ecommerce.agency_id == agency_id)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_ecommerce(
        db: Session,
        ecommerce_id: uuid.UUID,
        ecommerce_data: EcommerceUpdate
    ) -> Ecommerce:
        """Update e-commerce tenant"""
        ecommerce = EcommerceService.get_ecommerce(db, ecommerce_id)
        
        update_data = ecommerce_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(ecommerce, field, value)
        
        db.commit()
        db.refresh(ecommerce)
        return ecommerce
    
    @staticmethod
    def delete_ecommerce(db: Session, ecommerce_id: uuid.UUID) -> None:
        """Delete (deactivate) e-commerce tenant"""
        ecommerce = EcommerceService.get_ecommerce(db, ecommerce_id)
        ecommerce.is_active = False
        db.commit()
    
    @staticmethod
    def get_stats(db: Session, ecommerce_id: uuid.UUID) -> EcommerceStats:
        """Get e-commerce statistics"""
        total_products = db.query(func.count(Product.id)).filter(
            Product.ecommerce_id == ecommerce_id
        ).scalar()
        
        total_orders = db.query(func.count(Order.id)).filter(
            Order.ecommerce_id == ecommerce_id
        ).scalar()
        
        total_customers = db.query(func.count(Customer.id)).filter(
            Customer.ecommerce_id == ecommerce_id
        ).scalar()
        
        total_revenue = db.query(func.sum(Order.total)).filter(
            Order.ecommerce_id == ecommerce_id
        ).scalar() or 0.0
        
        return EcommerceStats(
            total_products=total_products,
            total_orders=total_orders,
            total_customers=total_customers,
            total_revenue=float(total_revenue)
        )
    
    @staticmethod
    def regenerate_api_key(db: Session, ecommerce_id: uuid.UUID) -> str:
        """
        Regenerate API key for an e-commerce tenant
        
        Returns the new API key (plaintext). The old key is immediately invalidated.
        """
        ecommerce = EcommerceService.get_ecommerce(db, ecommerce_id)
        
        # Generate new secure API key
        new_api_key = secrets.token_urlsafe(32)
        
        # Update the e-commerce record
        ecommerce.api_key = new_api_key
        db.commit()
        db.refresh(ecommerce)
        
        return new_api_key

