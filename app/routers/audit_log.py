"""
Audit log router for API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.audit_log import AuditLogResponse, AuditLogFilter
from app.services.audit_log_service import AuditLogService
from app.enums.user_role import UserRole

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("/", response_model=List[AuditLogResponse])
def get_audit_logs(
    user_id: Optional[UUID] = Query(None),
    ecommerce_id: Optional[UUID] = Query(None),
    agency_id: Optional[UUID] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get audit logs with filters (Admin only)
    
    - Super Admin: Can see all logs
    - Agency Admin: Can see logs for their agency
    - Other users: Cannot access
    """
    if current_user.role == UserRole.SUPER_ADMIN:
        # Super admin can see all logs
        pass
    elif current_user.role == UserRole.AGENCY_ADMIN:
        # Agency admin can only see logs for their agency
        if not current_user.agency_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Agency admin must be associated with an agency"
            )
        agency_id = current_user.agency_id
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access audit logs"
        )
    
    logs = AuditLogService.get_logs(
        db=db,
        user_id=user_id,
        ecommerce_id=ecommerce_id,
        agency_id=agency_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    return logs


@router.get("/my-activity", response_model=List[AuditLogResponse])
def get_my_activity(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get audit logs for current user"""
    logs = AuditLogService.get_logs(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return logs


@router.get("/{log_id}", response_model=AuditLogResponse)
def get_audit_log(
    log_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific audit log by ID (Admin only)"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.AGENCY_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access audit logs"
        )
    
    log = AuditLogService.get_log_by_id(db, log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found"
        )
    
    # Agency admins can only see logs from their agency
    if current_user.role == UserRole.AGENCY_ADMIN:
        if log.agency_id != current_user.agency_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access logs from other agencies"
            )
    
    return log


@router.get("/resource/{resource_type}/{resource_id}", response_model=List[AuditLogResponse])
def get_resource_history(
    resource_type: str,
    resource_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get audit history for a specific resource (Admin only)"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.AGENCY_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access audit logs"
        )
    
    logs = AuditLogService.get_resource_history(
        db=db,
        resource_type=resource_type,
        resource_id=resource_id,
        skip=skip,
        limit=limit
    )
    
    # Filter logs for agency admins
    if current_user.role == UserRole.AGENCY_ADMIN:
        logs = [log for log in logs if log.agency_id == current_user.agency_id]
    
    return logs
