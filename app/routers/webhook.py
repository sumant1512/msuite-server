"""
Webhook router for API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.webhook import WebhookEventType
from app.schemas.webhook import (
    WebhookCreate, WebhookUpdate, WebhookResponse, 
    WebhookDeliveryResponse, WebhookTest
)
from app.services.webhook_service import WebhookService
from app.enums.user_role import UserRole

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
def create_webhook(
    webhook_data: WebhookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new webhook (Agency Admin or Ecommerce user only)"""
    if current_user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admins cannot create webhooks directly"
        )
    
    if not current_user.ecommerce_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with an ecommerce"
        )
    
    webhook = WebhookService.create_webhook(
        db, current_user.ecommerce_id, webhook_data
    )
    return webhook


@router.get("/", response_model=List[WebhookResponse])
def get_webhooks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all webhooks for current ecommerce"""
    if not current_user.ecommerce_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with an ecommerce"
        )
    
    webhooks = WebhookService.get_webhooks(
        db, current_user.ecommerce_id, skip, limit
    )
    return webhooks


@router.get("/{webhook_id}", response_model=WebhookResponse)
def get_webhook(
    webhook_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific webhook by ID"""
    if not current_user.ecommerce_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with an ecommerce"
        )
    
    webhook = WebhookService.get_webhook_by_id(
        db, webhook_id, current_user.ecommerce_id
    )
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    return webhook


@router.put("/{webhook_id}", response_model=WebhookResponse)
def update_webhook(
    webhook_id: UUID,
    webhook_data: WebhookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a webhook"""
    if not current_user.ecommerce_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with an ecommerce"
        )
    
    webhook = WebhookService.get_webhook_by_id(
        db, webhook_id, current_user.ecommerce_id
    )
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    updated_webhook = WebhookService.update_webhook(db, webhook, webhook_data)
    return updated_webhook


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_webhook(
    webhook_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a webhook"""
    if not current_user.ecommerce_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with an ecommerce"
        )
    
    webhook = WebhookService.get_webhook_by_id(
        db, webhook_id, current_user.ecommerce_id
    )
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    WebhookService.delete_webhook(db, webhook)


@router.post("/{webhook_id}/regenerate-secret", response_model=WebhookResponse)
def regenerate_webhook_secret(
    webhook_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Regenerate webhook secret"""
    if not current_user.ecommerce_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with an ecommerce"
        )
    
    webhook = WebhookService.get_webhook_by_id(
        db, webhook_id, current_user.ecommerce_id
    )
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    updated_webhook = WebhookService.regenerate_secret(db, webhook)
    return updated_webhook


@router.post("/{webhook_id}/test", response_model=WebhookDeliveryResponse)
def test_webhook(
    webhook_id: UUID,
    test_data: WebhookTest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Test a webhook by sending a test event"""
    if not current_user.ecommerce_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with an ecommerce"
        )
    
    webhook = WebhookService.get_webhook_by_id(
        db, webhook_id, current_user.ecommerce_id
    )
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    # Create test payload
    test_payload = {
        "event_type": test_data.event_type.value,
        "test": True,
        "data": test_data.test_payload
    }
    
    # Create and deliver
    delivery = WebhookService.create_delivery(
        db, webhook_id, test_data.event_type, test_payload
    )
    delivery = WebhookService.deliver_webhook(db, webhook, delivery)
    
    return delivery


@router.get("/{webhook_id}/deliveries", response_model=List[WebhookDeliveryResponse])
def get_webhook_deliveries(
    webhook_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get delivery history for a webhook"""
    if not current_user.ecommerce_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with an ecommerce"
        )
    
    webhook = WebhookService.get_webhook_by_id(
        db, webhook_id, current_user.ecommerce_id
    )
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    deliveries = WebhookService.get_deliveries(db, webhook_id, skip, limit)
    return deliveries
