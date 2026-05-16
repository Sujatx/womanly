"""Example email-related background tasks for Celery.

These tasks are simple placeholders that integrate with the Celery app.
Replace the send logic with the real email provider integration.
"""
import asyncio
from typing import Dict
from app.celery_app import celery_app
from app.core.logging import get_structured_logger
from app.services import (
    _send_verification_email_impl,
    _send_order_confirmation_impl,
    _send_shipping_notification_impl,
)

logger = get_structured_logger(__name__)


@celery_app.task(bind=True, name="app.tasks.email.send_order_confirmation", max_retries=3)
def send_order_confirmation(self, to_email: str, subject: str, body: str, metadata: Dict = None) -> Dict:
    """Send order confirmation email (background task).

    Retries on failure with exponential backoff.
    """
    try:
        # Placeholder: integrate with real email service (aiosmtplib or provider SDK)
        logger.info("Sending order confirmation email", to=to_email, subject=subject)
        # Simulate work / call actual provider here
        return {"status": "sent", "to": to_email}

    except Exception as exc:
        # Retry with exponential backoff
        countdown = min(60 * (2 ** self.request.retries), 3600)
        logger.warning("Email send failed, scheduling retry", error=str(exc), retries=self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)


@celery_app.task(bind=True, name="app.tasks.email.send_verification_email_task", max_retries=3)
def send_verification_email_task(self, email: str, token: str) -> Dict:
    try:
        asyncio.run(_send_verification_email_impl(email, token))
        return {"status": "sent", "to": email}
    except Exception as exc:
        countdown = min(60 * (2 ** self.request.retries), 3600)
        logger.warning("Verification email send failed, scheduling retry", error=str(exc), retries=self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)


@celery_app.task(bind=True, name="app.tasks.email.send_order_confirmation_notification_task", max_retries=3)
def send_order_confirmation_notification_task(self, email: str, order_id: int, amount: float) -> Dict:
    try:
        asyncio.run(_send_order_confirmation_impl(email, order_id, amount))
        return {"status": "sent", "to": email, "order_id": order_id}
    except Exception as exc:
        countdown = min(60 * (2 ** self.request.retries), 3600)
        logger.warning("Order confirmation email send failed, scheduling retry", error=str(exc), retries=self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)


@celery_app.task(bind=True, name="app.tasks.email.send_shipping_notification_task", max_retries=3)
def send_shipping_notification_task(self, email: str, order_id: int, tracking_number: str, provider: str) -> Dict:
    try:
        asyncio.run(_send_shipping_notification_impl(email, order_id, tracking_number, provider))
        return {"status": "sent", "to": email, "order_id": order_id}
    except Exception as exc:
        countdown = min(60 * (2 ** self.request.retries), 3600)
        logger.warning("Shipping notification email send failed, scheduling retry", error=str(exc), retries=self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)
