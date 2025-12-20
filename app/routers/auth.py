"""
Authentication routes for login, registration, and token management
"""
from fastapi import APIRouter, Depends, status, Header, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated, Optional

from app.core.dependencies import get_db, get_current_active_user
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse
)
from app.services.auth_service import AuthService
from app.models.user import User


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: RegisterRequest,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Register a new customer (ecommerce user only)
    
    Self-registration is restricted to ECOMMERCE role (customers).
    Super Admin and Agency Admin accounts must be created by authorized users only.
    
    - **email**: User email address (must be unique)
    - **password**: User password (minimum 8 characters)
    - **full_name**: User's full name
    - **ecommerce_id**: Required e-commerce ID for customer account
    - **role**: Must be ECOMMERCE (enforced)
    """
    # Security: Only allow self-registration for ECOMMERCE role (customers)
    if user_data.role != UserRole.ECOMMERCE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Self-registration is only allowed for customers. Admin accounts must be created by authorized administrators."
        )
    
    user = AuthService.register(db, user_data)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Login user with email and password
    
    Returns JWT access token and refresh token
    """
    return AuthService.login(db, credentials)


@router.post("/login/form", response_model=TokenResponse)
async def login_form(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Login user with OAuth2 password flow (for Swagger UI)
    
    Returns JWT access token and refresh token
    """
    credentials = LoginRequest(email=form_data.username, password=form_data.password)
    return AuthService.login(db, credentials)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Refresh access token using refresh token
    
    Returns new access token and refresh token
    """
    return AuthService.refresh_tokens(db, refresh_data.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Get current authenticated user's profile
    
    Requires valid JWT access token
    """
    return UserResponse.model_validate(current_user)


@router.post("/logout")
async def logout(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    authorization: Annotated[Optional[str], Header()] = None
):
    """
    Logout current user by blacklisting the token
    
    The token will be invalidated and cannot be used for further requests.
    Requires valid JWT access token in Authorization header.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.split(" ")[1]
    return AuthService.logout(db, token, current_user)


@router.post("/extend-session")
async def extend_session(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Extend user session by generating new tokens
    
    This endpoint should be called periodically by the client to keep the session active.
    Returns new access and refresh tokens with updated expiry.
    
    - Automatically called when user is active
    - Resets the 30-minute inactivity timer
    - Provides new tokens for continued access
    """
    return AuthService.extend_session(db, current_user)
