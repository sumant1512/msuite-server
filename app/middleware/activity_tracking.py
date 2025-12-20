"""
Activity tracking middleware for session management
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
from typing import Callable

from app.core.dependencies import get_db
from app.services.auth_service import AuthService
from app.core.security import decode_token
from app.models.user import User
import uuid


class ActivityTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware to track user activity and enforce session timeout"""
    
    # Paths that don't require activity tracking
    EXEMPT_PATHS = [
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/refresh",
        "/api/v1/auth/login/form"
    ]
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Skip activity tracking for exempt paths
        if any(request.url.path.startswith(path) for path in self.EXEMPT_PATHS):
            return await call_next(request)
        
        # Get authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return await call_next(request)
        
        token = auth_header.split(" ")[1]
        
        # Get database session
        db = next(get_db())
        try:
            # Check if token is blacklisted
            if AuthService.is_token_blacklisted(db, token):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked. Please login again."
                )
            
            # Decode token to get user
            payload = decode_token(token)
            if not payload:
                return await call_next(request)
            
            user_id_str = payload.get("sub")
            if not user_id_str:
                return await call_next(request)
            
            try:
                user_id = uuid.UUID(user_id_str)
            except ValueError:
                return await call_next(request)
            
            # Get user from database
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return await call_next(request)
            
            # Check session timeout (30 minutes of inactivity)
            if not AuthService.check_session_timeout(user, timeout_minutes=30):
                # Blacklist the token
                exp = payload.get("exp")
                expires_at = datetime.fromtimestamp(exp) if exp else datetime.utcnow()
                from app.models.token_blacklist import TokenBlacklist
                blacklisted = TokenBlacklist(
                    token=token,
                    user_id=user.id,
                    reason="session_timeout",
                    expires_at=expires_at
                )
                db.add(blacklisted)
                db.commit()
                
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Session expired due to inactivity. Please login again."
                )
            
            # Update last activity
            user.last_activity = datetime.utcnow()
            db.commit()
            
        finally:
            db.close()
        
        return await call_next(request)
