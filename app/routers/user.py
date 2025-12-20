"""
User management routes
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Annotated, List
import uuid

from app.core.dependencies import (
    get_db,
    get_current_user,
    require_agency_admin,
    require_super_admin,
    require_agency_context
)
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_agency_admin)],
    agency_id: Annotated[uuid.UUID, Depends(require_agency_context)]
):
    """
    Create a new user (Agency Admin only)
    
    Users are scoped to the agency context
    """
    user = UserService.create_user(db, user_data, agency_id)
    return UserResponse.model_validate(user)


@router.get("", response_model=List[UserResponse])
async def list_users(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_agency_admin)],
    agency_id: Annotated[uuid.UUID, Depends(require_agency_context)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """List all users in the agency"""
    users = UserService.list_users(db, agency_id, skip, limit)
    return [UserResponse.model_validate(u) for u in users]


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Get current user profile"""
    return UserResponse.model_validate(current_user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_agency_admin)],
    agency_id: Annotated[uuid.UUID, Depends(require_agency_context)]
):
    """Get user details"""
    user = UserService.get_user(db, user_id)
    
    # Verify belongs to agency
    if user.agency_id != agency_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied")
    
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    user_data: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_agency_admin)],
    agency_id: Annotated[uuid.UUID, Depends(require_agency_context)]
):
    """Update user details"""
    user = UserService.get_user(db, user_id)
    
    # Verify belongs to agency
    if user.agency_id != agency_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied")
    
    user = UserService.update_user(db, user_id, user_data)
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_agency_admin)],
    agency_id: Annotated[uuid.UUID, Depends(require_agency_context)]
):
    """Delete (deactivate) user"""
    user = UserService.get_user(db, user_id)
    
    # Verify belongs to agency
    if user.agency_id != agency_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied")
    
    UserService.delete_user(db, user_id)

