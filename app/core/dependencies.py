"""
Dependency injection functions for FastAPI routes
"""
from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from datetime import datetime, timedelta
import uuid

from app.core.database import SessionLocal
from app.core.security import decode_token
from app.models.user import User
from app.models.token_blacklist import TokenBlacklist
from app.enums.user_role import UserRole


# OAuth2 scheme for JWT token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def get_db():
    """
    Database session dependency
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)]
) -> User:
    """
    Get current authenticated user from JWT token
    
    Args:
        token: JWT access token
        db: Database session
        
    Returns:
        Current user object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Check if token is blacklisted
    blacklisted = db.query(TokenBlacklist).filter(
        TokenBlacklist.token == token,
        TokenBlacklist.expires_at > datetime.utcnow()
    ).first()
    
    if blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked. Please login again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_uuid).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # Check session timeout (30 minutes of inactivity)
    if user.last_activity:
        time_elapsed = datetime.utcnow() - user.last_activity
        if time_elapsed > timedelta(minutes=30):
            # Blacklist the token
            exp = payload.get("exp")
            expires_at = datetime.fromtimestamp(exp) if exp else datetime.utcnow() + timedelta(hours=1)
            blacklisted_token = TokenBlacklist(
                token=token,
                user_id=user.id,
                reason="session_timeout",
                expires_at=expires_at
            )
            db.add(blacklisted_token)
            db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired due to inactivity. Please login again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # Update last activity
    user.last_activity = datetime.utcnow()
    db.commit()
    
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Ensure user is active
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Active user object
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def require_role(*allowed_roles: UserRole):
    """
    Dependency factory for role-based access control
    
    Args:
        *allowed_roles: Allowed user roles
        
    Returns:
        Dependency function that checks user role
    """
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_active_user)]
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires one of these roles: {[r.value for r in allowed_roles]}"
            )
        return current_user
    
    return role_checker


# Convenience dependencies for common role checks
require_super_admin = require_role(UserRole.SUPER_ADMIN)
require_agency_admin = require_role(UserRole.SUPER_ADMIN, UserRole.AGENCY_ADMIN)
require_ecommerce_user = require_role(UserRole.SUPER_ADMIN, UserRole.AGENCY_ADMIN, UserRole.ECOMMERCE)


def get_agency_id(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> Optional[uuid.UUID]:
    """
    Extract agency ID from current user context
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Agency ID or None
    """
    return current_user.agency_id


def get_ecommerce_id(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> Optional[uuid.UUID]:
    """
    Extract e-commerce ID from current user context
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        E-commerce ID or None
    """
    return current_user.ecommerce_id


def require_agency_context(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> uuid.UUID:
    """
    Ensure user has agency context
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Agency ID
        
    Raises:
        HTTPException: If user has no agency context
    """
    if current_user.agency_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agency context required"
        )
    return current_user.agency_id


def require_ecommerce_context(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> uuid.UUID:
    """
    Ensure user has e-commerce context
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        E-commerce ID
        
    Raises:
        HTTPException: If user has no e-commerce context
    """
    if current_user.ecommerce_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="E-commerce context required"
        )
    return current_user.ecommerce_id


async def verify_api_key(
    x_api_key: Annotated[str, Header(alias="X-API-Key")],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Verify ecommerce API key for frontend authentication
    
    Args:
        x_api_key: API key from X-API-Key header
        db: Database session
        
    Returns:
        Ecommerce object
        
    Raises:
        HTTPException: If API key is invalid or ecommerce is inactive
    """
    from app.models.ecommerce import Ecommerce
    
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Include X-API-Key header."
        )
    
    ecommerce = db.query(Ecommerce).filter(
        Ecommerce.api_key == x_api_key,
        Ecommerce.is_active == True
    ).first()
    
    if not ecommerce:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key"
        )
    
    # Check if agency is active
    if ecommerce.agency and not ecommerce.agency.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Parent agency is inactive"
        )
    
    # Check subscription status
    from app.models.agency import SubscriptionStatus
    if ecommerce.agency and ecommerce.agency.subscription_status not in [
        SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL
    ]:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Subscription inactive. Please contact your agency administrator."
        )
    
    # Check subscription expiry
    if ecommerce.agency and ecommerce.agency.subscription_expires_at:
        if ecommerce.agency.subscription_expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Subscription expired. Please renew."
            )
    
    return ecommerce


def validate_tenant_access(resource_ecommerce_id: uuid.UUID, user_ecommerce_id: Optional[uuid.UUID]):
    """
    Validate that user has access to the resource's tenant
    
    Args:
        resource_ecommerce_id: The ecommerce_id of the resource being accessed
        user_ecommerce_id: The ecommerce_id of the current user
        
    Raises:
        HTTPException: If user cannot access this tenant's resource
    """
    if user_ecommerce_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No ecommerce context"
        )
    
    if resource_ecommerce_id != user_ecommerce_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Resource belongs to different tenant"
        )
