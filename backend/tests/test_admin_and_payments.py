import hmac
import hashlib

import pytest
from pydantic import SecretStr
from app.core.exceptions import ForbiddenException


def test_get_current_admin_user_requires_superuser():
    from app.api.admin import get_current_admin_user
    from app.models.user import User

    user = User(
        email="customer@example.com",
        full_name="Customer",
        hashed_password="hashed",
        is_verified=True,
        is_superuser=False,
    )

    with pytest.raises(ForbiddenException) as exc_info:
        get_current_admin_user(current_user=user)


def test_get_current_admin_user_allows_superuser():
    from app.api.admin import get_current_admin_user
    from app.models.user import User

    user = User(
        email="admin@example.com",
        full_name="Admin",
        hashed_password="hashed",
        is_verified=True,
        is_superuser=True,
    )

    assert get_current_admin_user(current_user=user) == user


def test_verify_webhook_signature(monkeypatch):
    from app.services.razorpay_service import verify_webhook_signature
    from app.config import settings

    secret = "webhook-secret"
    payload = b'{"event":"payment.captured"}'
    signature = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

    monkeypatch.setattr(settings, "RAZORPAY_WEBHOOK_SECRET", SecretStr(secret))

    assert verify_webhook_signature(payload, signature) is True
    assert verify_webhook_signature(payload, "bad-signature") is False