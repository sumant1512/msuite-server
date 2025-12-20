"""
Audit log service for tracking system changes
"""
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.models.audit_log import AuditLog
from app.models.user import User


class AuditLogService:
    """Service for audit logging operations"""

    @staticmethod
    def create_log(
        db: Session,
        action: str,
        resource_type: str,
        user: Optional[User] = None,
        resource_id: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        endpoint: Optional[str] = None,
        description: Optional[str] = None
    ) -> AuditLog:
        """Create an audit log entry"""
        log = AuditLog(
            user_id=user.id if user else None,
            user_email=user.email if user else None,
            ecommerce_id=user.ecommerce_id if user else None,
            agency_id=user.agency_id if user else None,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            description=description
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def get_logs(
        db: Session,
        user_id: Optional[UUID] = None,
        ecommerce_id: Optional[UUID] = None,
        agency_id: Optional[UUID] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs with filters"""
        query = db.query(AuditLog)
        
        conditions = []
        if user_id:
            conditions.append(AuditLog.user_id == user_id)
        if ecommerce_id:
            conditions.append(AuditLog.ecommerce_id == ecommerce_id)
        if agency_id:
            conditions.append(AuditLog.agency_id == agency_id)
        if action:
            conditions.append(AuditLog.action == action)
        if resource_type:
            conditions.append(AuditLog.resource_type == resource_type)
        if resource_id:
            conditions.append(AuditLog.resource_id == resource_id)
        if start_date:
            conditions.append(AuditLog.created_at >= start_date)
        if end_date:
            conditions.append(AuditLog.created_at <= end_date)
        
        if conditions:
            query = query.filter(and_(*conditions))
        
        return query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_log_by_id(
        db: Session,
        log_id: UUID
    ) -> Optional[AuditLog]:
        """Get audit log by ID"""
        return db.query(AuditLog).filter(AuditLog.id == log_id).first()

    @staticmethod
    def get_resource_history(
        db: Session,
        resource_type: str,
        resource_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get all audit logs for a specific resource"""
        return db.query(AuditLog).filter(
            and_(
                AuditLog.resource_type == resource_type,
                AuditLog.resource_id == resource_id
            )
        ).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def log_user_action(
        db: Session,
        user: User,
        action: str,
        description: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """Log a user action (login, logout, etc.)"""
        return AuditLogService.create_log(
            db=db,
            action=action,
            resource_type="User",
            user=user,
            resource_id=str(user.id),
            description=description,
            ip_address=ip_address,
            user_agent=user_agent
        )

    @staticmethod
    def log_model_change(
        db: Session,
        user: User,
        action: str,
        model_name: str,
        model_id: UUID,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        endpoint: Optional[str] = None
    ) -> AuditLog:
        """Log a model create/update/delete action"""
        return AuditLogService.create_log(
            db=db,
            action=action,
            resource_type=model_name,
            user=user,
            resource_id=str(model_id),
            old_values=old_values,
            new_values=new_values,
            endpoint=endpoint
        )
