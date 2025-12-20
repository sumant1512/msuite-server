"""
Agency service for managing multi-tenant agencies
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from app.models.agency import Agency
from app.models.user import User
from app.models.ecommerce import Ecommerce
from app.schemas.agency import AgencyCreate, AgencyUpdate
from app.core.security import get_password_hash
from app.enums.user_role import UserRole


class AgencyService:
    """Agency service class"""
    
    @staticmethod
    def create_agency(db: Session, agency_data: AgencyCreate) -> Agency:
        """Create a new agency with admin user"""
        # Check if email already exists
        existing = db.query(Agency).filter(Agency.email == agency_data.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Agency with this email already exists"
            )
        
        # Check if admin email already exists
        existing_user = db.query(User).filter(User.email == agency_data.admin_email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin email already registered"
            )
        
        # Create agency
        agency = Agency(
            id=uuid.uuid4(),
            name=agency_data.name,
            email=agency_data.email,
            phone=agency_data.phone,
            address=agency_data.address,
            subscription_plan_id=agency_data.subscription_plan_id,
            max_ecommerce=agency_data.max_ecommerce,
            metadata_=agency_data.metadata_,
            subscription_expires_at=datetime.utcnow() + timedelta(days=30)  # 30-day trial
        )
        
        db.add(agency)
        db.flush()  # Get agency ID
        
        # Create agency admin user
        admin_user = User(
            id=uuid.uuid4(),
            email=agency_data.admin_email,
            full_name=agency_data.admin_name,
            hashed_password=get_password_hash(agency_data.admin_password),
            role=UserRole.AGENCY_ADMIN,
            agency_id=agency.id,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(agency)
        
        return agency
    
    @staticmethod
    def get_agency(db: Session, agency_id: uuid.UUID) -> Agency:
        """Get agency by ID"""
        agency = db.query(Agency).filter(Agency.id == agency_id).first()
        
        if not agency:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agency not found"
            )
        
        return agency
    
    @staticmethod
    def list_agencies(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> List[Agency]:
        """List all agencies"""
        query = db.query(Agency)
        
        if active_only:
            query = query.filter(Agency.is_active == True)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_agency(
        db: Session,
        agency_id: uuid.UUID,
        agency_data: AgencyUpdate
    ) -> Agency:
        """Update agency"""
        agency = AgencyService.get_agency(db, agency_id)
        
        update_data = agency_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agency, field, value)
        
        db.commit()
        db.refresh(agency)
        return agency
    
    @staticmethod
    def delete_agency(db: Session, agency_id: uuid.UUID) -> None:
        """Delete (deactivate) agency"""
        agency = AgencyService.get_agency(db, agency_id)
        agency.is_active = False
        db.commit()
    
    @staticmethod
    def get_ecommerce_count(db: Session, agency_id: uuid.UUID) -> int:
        """Get count of e-commerce tenants for agency"""
        return db.query(func.count(Ecommerce.id)).filter(
            Ecommerce.agency_id == agency_id
        ).scalar()
