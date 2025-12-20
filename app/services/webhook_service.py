"""
Webhook service for business logic
"""
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from typing import List, Optional
from uuid import UUID
import secrets
import hashlib
import hmac
import httpx
from datetime import datetime, timedelta

from app.models.webhook import Webhook, WebhookDelivery, WebhookEventType
from app.schemas.webhook import WebhookCreate, WebhookUpdate


class WebhookService:
    """Service for webhook operations"""

    @staticmethod
    def generate_secret() -> str:
        """Generate a secure webhook secret"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def generate_signature(payload: str, secret: str) -> str:
        """Generate HMAC signature for webhook payload"""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

    @staticmethod
    def create_webhook(
        db: Session,
        ecommerce_id: UUID,
        webhook_data: WebhookCreate
    ) -> Webhook:
        """Create a new webhook"""
        webhook = Webhook(
            ecommerce_id=ecommerce_id,
            secret=WebhookService.generate_secret(),
            **webhook_data.model_dump()
        )
        db.add(webhook)
        db.commit()
        db.refresh(webhook)
        return webhook

    @staticmethod
    def get_webhook_by_id(
        db: Session,
        webhook_id: UUID,
        ecommerce_id: UUID
    ) -> Optional[Webhook]:
        """Get webhook by ID"""
        return db.query(Webhook).filter(
            and_(
                Webhook.id == webhook_id,
                Webhook.ecommerce_id == ecommerce_id
            )
        ).first()

    @staticmethod
    def get_webhooks(
        db: Session,
        ecommerce_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Webhook]:
        """Get all webhooks for an ecommerce"""
        return db.query(Webhook).filter(
            Webhook.ecommerce_id == ecommerce_id
        ).order_by(Webhook.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_webhook(
        db: Session,
        webhook: Webhook,
        webhook_data: WebhookUpdate
    ) -> Webhook:
        """Update a webhook"""
        update_data = webhook_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(webhook, field, value)
        
        db.commit()
        db.refresh(webhook)
        return webhook

    @staticmethod
    def delete_webhook(
        db: Session,
        webhook: Webhook
    ) -> None:
        """Delete a webhook"""
        db.delete(webhook)
        db.commit()

    @staticmethod
    def regenerate_secret(
        db: Session,
        webhook: Webhook
    ) -> Webhook:
        """Regenerate webhook secret"""
        webhook.secret = WebhookService.generate_secret()
        db.commit()
        db.refresh(webhook)
        return webhook

    @staticmethod
    def get_active_webhooks_for_event(
        db: Session,
        ecommerce_id: UUID,
        event_type: WebhookEventType
    ) -> List[Webhook]:
        """Get active webhooks subscribed to an event"""
        return db.query(Webhook).filter(
            and_(
                Webhook.ecommerce_id == ecommerce_id,
                Webhook.is_active == True,
                Webhook.events.contains([event_type.value])
            )
        ).all()

    @staticmethod
    def create_delivery(
        db: Session,
        webhook_id: UUID,
        event_type: WebhookEventType,
        payload: dict
    ) -> WebhookDelivery:
        """Create a webhook delivery record"""
        delivery = WebhookDelivery(
            webhook_id=webhook_id,
            event_type=event_type,
            payload=payload,
            status="PENDING",
            attempt_count=0
        )
        db.add(delivery)
        db.commit()
        db.refresh(delivery)
        return delivery

    @staticmethod
    def deliver_webhook(
        db: Session,
        webhook: Webhook,
        delivery: WebhookDelivery
    ) -> WebhookDelivery:
        """Attempt to deliver a webhook"""
        import json
        
        delivery.attempt_count += 1
        payload_str = json.dumps(delivery.payload)
        signature = WebhookService.generate_signature(payload_str, webhook.secret)
        
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Webhook-Event": delivery.event_type.value
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    webhook.url,
                    content=payload_str,
                    headers=headers
                )
                
                delivery.http_status = response.status_code
                delivery.response_body = response.text[:1000]  # Limit response size
                
                if 200 <= response.status_code < 300:
                    delivery.status = "SUCCESS"
                    delivery.delivered_at = datetime.now(datetime.timezone.utc)
                else:
                    delivery.status = "FAILED"
                    delivery.error_message = f"HTTP {response.status_code}"
                    
                    # Schedule retry if attempts remaining
                    if delivery.attempt_count < webhook.retry_count:
                        # Exponential backoff: 2^attempt minutes
                        retry_delay = 2 ** delivery.attempt_count
                        delivery.next_retry_at = datetime.now(datetime.timezone.utc) + timedelta(minutes=retry_delay)
                        
        except Exception as e:
            delivery.status = "FAILED"
            delivery.error_message = str(e)[:500]
            
            # Schedule retry if attempts remaining
            if delivery.attempt_count < webhook.retry_count:
                retry_delay = 2 ** delivery.attempt_count
                delivery.next_retry_at = datetime.now(datetime.timezone.utc) + timedelta(minutes=retry_delay)
        
        db.commit()
        db.refresh(delivery)
        return delivery

    @staticmethod
    def get_deliveries(
        db: Session,
        webhook_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[WebhookDelivery]:
        """Get webhook deliveries"""
        return db.query(WebhookDelivery).filter(
            WebhookDelivery.webhook_id == webhook_id
        ).order_by(WebhookDelivery.created_at.desc()).offset(skip).limit(limit).all()
