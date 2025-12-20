"""
User service for user management
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
import uuid

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


class UserService:
    """Service for user management operations"""

    @staticmethod
    def create_user(db: Session, user_data: UserCreate, agency_id: uuid.UUID) -> User:
        """
        Create a new user
        
        Args:
            db: Database session
            user_data: User creation data
            agency_id: Agency ID for the user
            
        Returns:
            Created user
            
        Raises:
            HTTPException: If email already exists
        """
        # Check if email exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password),
            role=user_data.role,
            agency_id=agency_id,
            ecommerce_id=user_data.ecommerce_id,
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user(db: Session, user_id: uuid.UUID) -> User:
        """
        Get user by ID
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User
            
        Raises:
            HTTPException: If user not found
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    @staticmethod
    def list_users(
        db: Session,
        agency_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """
        List users for an agency
        
        Args:
            db: Database session
            agency_id: Agency ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of users
        """
        return db.query(User)\
            .filter(User.agency_id == agency_id)\
            .offset(skip)\
            .limit(limit)\
            .all()

    @staticmethod
    def update_user(
        db: Session,
        user_id: uuid.UUID,
        user_data: UserUpdate
    ) -> User:
        """
        Update user
        
        Args:
            db: Database session
            user_id: User ID
            user_data: User update data
            
        Returns:
            Updated user
            
        Raises:
            HTTPException: If user not found or email already exists
        """
        user = UserService.get_user(db, user_id)
        
        # Check email uniqueness if being updated
        if user_data.email and user_data.email != user.email:
            existing_user = db.query(User).filter(User.email == user_data.email).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Update fields
        update_data = user_data.model_dump(exclude_unset=True)
        
        # Hash password if provided
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: uuid.UUID) -> None:
        """
        Delete (deactivate) user
        
        Args:
            db: Database session
            user_id: User ID
            
        Raises:
            HTTPException: If user not found
        """
        user = UserService.get_user(db, user_id)
        user.is_active = False
        db.commit()
