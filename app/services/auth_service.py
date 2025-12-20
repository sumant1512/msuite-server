"""
Authentication service for user authentication and token management
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import timedelta, datetime
from typing import Optional
import uuid

from app.models.user import User
from app.models.token_blacklist import TokenBlacklist
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse
)
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.core.config import settings
from app.enums.user_role import UserRole


class AuthService:
    """Authentication service class"""
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password
        
        Args:
            db: Database session
            email: User email
            password: User password
            
        Returns:
            User object if authenticated, None otherwise
        """
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    def create_tokens(user: User) -> dict:
        """
        Create access and refresh tokens for user
        
        Args:
            user: User object
            
        Returns:
            Dictionary with access_token, refresh_token, and expires_in
        """
        # Token payload
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
        }
        
        # Add agency_id if present
        if user.agency_id:
            token_data["agency_id"] = str(user.agency_id)
        
        # Add ecommerce_id if present
        if user.ecommerce_id:
            token_data["ecommerce_id"] = str(user.ecommerce_id)
        
        # Create tokens
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    @staticmethod
    def login(db: Session, credentials: LoginRequest) -> TokenResponse:
        """
        Login user and return tokens
        
        Args:
            db: Database session
            credentials: Login credentials
            
        Returns:
            TokenResponse with tokens and user info
            
        Raises:
            HTTPException: If credentials are invalid
        """
        user = AuthService.authenticate_user(db, credentials.email, credentials.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user account"
            )
        
        tokens = AuthService.create_tokens(user)
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            expires_in=tokens["expires_in"],
            user=UserResponse.model_validate(user)
        )
    
    @staticmethod
    def register(db: Session, user_data: RegisterRequest) -> User:
        """
        Register a new user
        
        Args:
            db: Database session
            user_data: User registration data
            
        Returns:
            Created user object
            
        Raises:
            HTTPException: If email already exists
        """
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Default role to ECOMMERCE if not specified
        role = user_data.role if user_data.role else UserRole.ECOMMERCE
        
        # Create new user
        new_user = User(
            id=uuid.uuid4(),
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password),
            role=role,
            agency_id=user_data.agency_id,
            ecommerce_id=user_data.ecommerce_id,
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    
    @staticmethod
    def refresh_tokens(db: Session, refresh_token: str) -> TokenResponse:
        """
        Refresh access token using refresh token
        
        Args:
            db: Database session
            refresh_token: Refresh token
            
        Returns:
            TokenResponse with new tokens
            
        Raises:
            HTTPException: If refresh token is invalid
        """
        payload = decode_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user = db.query(User).filter(User.id == user_uuid).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        tokens = AuthService.create_tokens(user)
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            expires_in=tokens["expires_in"],
            user=UserResponse.model_validate(user)
        )

    @staticmethod
    def logout(db: Session, token: str, user: User) -> dict:
        """
        Logout user by blacklisting the token
        
        Args:
            db: Database session
            token: JWT access token to blacklist
            user: Current user
            
        Returns:
            Success message
        """
        # Decode token to get expiry
        payload = decode_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Get token expiry
        exp = payload.get("exp")
        expires_at = datetime.fromtimestamp(exp) if exp else datetime.utcnow() + timedelta(hours=1)
        
        # Add token to blacklist
        blacklisted_token = TokenBlacklist(
            token=token,
            user_id=user.id,
            reason="logout",
            expires_at=expires_at
        )
        db.add(blacklisted_token)
        db.commit()
        
        return {"message": "Successfully logged out"}

    @staticmethod
    def is_token_blacklisted(db: Session, token: str) -> bool:
        """
        Check if token is blacklisted
        
        Args:
            db: Database session
            token: JWT token to check
            
        Returns:
            True if token is blacklisted, False otherwise
        """
        blacklisted = db.query(TokenBlacklist).filter(
            TokenBlacklist.token == token,
            TokenBlacklist.expires_at > datetime.utcnow()
        ).first()
        return blacklisted is not None

    @staticmethod
    def update_user_activity(db: Session, user: User) -> None:
        """
        Update user's last activity timestamp
        
        Args:
            db: Database session
            user: User object
        """
        user.last_activity = datetime.utcnow()
        db.commit()

    @staticmethod
    def check_session_timeout(user: User, timeout_minutes: int = 30) -> bool:
        """
        Check if user session has timed out due to inactivity
        
        Args:
            user: User object
            timeout_minutes: Timeout period in minutes (default 30)
            
        Returns:
            True if session is still valid, False if timed out
        """
        if not user.last_activity:
            return True  # First time, consider valid
        
        time_elapsed = datetime.utcnow() - user.last_activity
        return time_elapsed < timedelta(minutes=timeout_minutes)

    @staticmethod
    def extend_session(db: Session, user: User) -> dict:
        """
        Extend user session by updating last activity and creating new tokens
        
        Args:
            db: Database session
            user: Current user
            
        Returns:
            New tokens with extended session
        """
        # Update last activity
        AuthService.update_user_activity(db, user)
        
        # Create new tokens
        tokens = AuthService.create_tokens(user)
        
        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "expires_in": tokens["expires_in"],
            "message": "Session extended successfully"
        }
