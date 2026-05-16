"""
Consolidated service helpers for the backend.

This package keeps the small utility-style services in one place so callers can import
from app.services instead of hopping across many tiny files.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from email.message import EmailMessage
from typing import Optional
import html
import asyncio
import json
import logging
import os
import re
import ssl

import aiosmtplib
from aiosmtplib import SMTP

from app.config import settings
from app.core.logging import get_structured_logger
from app.core.circuit_breaker import CircuitBreaker

logger = get_structured_logger(__name__)

EMAIL_BREAKER = CircuitBreaker("email", "email", failure_threshold=3, recovery_timeout=60)

# -----------------------------
# Sanitization helpers
# -----------------------------

try:
    import bleach
    BLEACH_AVAILABLE = True
except ImportError:
    BLEACH_AVAILABLE = False
    logger.warning("bleach not installed. Using html.escape only for sanitization.")

ALLOWED_TAGS = ["p", "br", "strong", "em", "u", "ol", "ul", "li", "a"]
ALLOWED_ATTRIBUTES = {"a": ["href", "title"]}


def escape_html(text: str) -> str:
    if not isinstance(text, str):
        return text
    return html.escape(text)


def sanitize_text(text: str, allow_html: bool = False) -> str:
    if not isinstance(text, str):
        return text
    text = text.replace("\x00", "")
    if not allow_html:
        return escape_html(text)
    if BLEACH_AVAILABLE:
        return bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
    logger.warning("bleach not available, escaping HTML")
    return escape_html(text)


def sanitize_json_field(data: dict, field_name: str, allow_html: bool = False) -> None:
    if field_name in data and isinstance(data[field_name], str):
        data[field_name] = sanitize_text(data[field_name], allow_html=allow_html)


def sanitize_product_description(description: str) -> str:
    return sanitize_text(description, allow_html=True)


def sanitize_user_name(name: str) -> str:
    return sanitize_text(name, allow_html=False)


def sanitize_address(address: str) -> str:
    return sanitize_text(address, allow_html=False)


def sanitize_email(email: str) -> str:
    email = escape_html(email).strip().lower()
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        logger.warning(f"Invalid email format detected: {email[:20]}...")
    return email


def sanitize_phone(phone: str) -> str:
    phone = phone.strip()
    phone = re.sub(r"[^\d\s\-\+]", "", phone)
    return phone.replace(" ", "")


def sanitize_all_text_fields(data: dict, text_fields: list) -> dict:
    sanitized = data.copy()
    for field in text_fields:
        if field in sanitized and isinstance(sanitized[field], str):
            sanitized[field] = sanitize_text(sanitized[field])
    return sanitized


def test_xss_payload(text: str) -> bool:
    xss_patterns = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<embed",
        r"<object",
    ]
    text_lower = text.lower()
    for pattern in xss_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL):
            return True
    return False

# -----------------------------
# Email helpers
# -----------------------------

async def send_email(subject: str, to: str, html_content: str):
    message = EmailMessage()
    message["From"] = settings.SMTP_FROM
    message["To"] = to
    message["Subject"] = subject
    message.add_alternative(html_content, subtype="html")

    async with SMTP(hostname=settings.SMTP_HOST, port=settings.SMTP_PORT) as smtp:
        await smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        await smtp.send_message(message)


async def _send_verification_email_impl(email: str, token: str):
    verify_url = f"{settings.FRONTEND_URL}/#/auth/verify?token={token}"
    logger.info(f"Sending verification email to {email} with link: {verify_url}")

    html_content = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 24px;">
        <h1 style="font-size: 24px; font-weight: 900; letter-spacing: 0.05em; text-transform: uppercase;">Womanly</h1>
        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
        <p style="font-size: 16px; font-weight: 600; color: #64748b;">PLEASE VERIFY YOUR ACCOUNT</p>
        <p style="font-size: 14px; line-height: 1.6; color: #1e293b;">Welcome to Womanly. Click the button below to verify your email address and activate your account.</p>
        <a href="{verify_url}" style="display: inline-block; padding: 14px 28px; background: #0f172a; color: white; text-decoration: none; border-radius: 32px; font-weight: 900; font-size: 12px; margin-top: 20px; text-transform: uppercase;">VERIFY ACCOUNT</a>
        <p style="font-size: 12px; color: #94a3b8; margin-top: 40px;">If you didn't create an account, you can safely ignore this email.</p>
    </div>
    """
    await send_email("Verify your Womanly account", email, html_content)


async def send_verification_email(email: str, token: str):
    async def _fallback():
        from app.tasks.email import send_verification_email_task

        send_verification_email_task.delay(email, token)
        return {"status": "queued", "email": email}

    return await EMAIL_BREAKER.acall(_send_verification_email_impl, email, token, fallback=_fallback)


async def _send_order_confirmation_impl(email: str, order_id: int, amount: float):
    html_content = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 24px;">
        <h1 style="font-size: 24px; font-weight: 900; letter-spacing: 0.05em; text-transform: uppercase;">Womanly</h1>
        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
        <p style="font-size: 16px; font-weight: 600; color: #64748b;">ORDER CONFIRMED</p>
        <p style="font-size: 14px; line-height: 1.6; color: #1e293b;">Thank you for your purchase. Your order <strong>#{order_id}</strong> has been received and is being processed.</p>
        <div style="background: #f8fafc; padding: 20px; border-radius: 16px; margin: 20px 0;">
            <p style="margin: 0; font-size: 12px; font-weight: 800; color: #64748b;">TOTAL AMOUNT</p>
            <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: 900;">${amount}</p>
        </div>
        <a href="http://localhost:3000/account/orders" style="display: inline-block; padding: 14px 28px; background: #0f172a; color: white; text-decoration: none; border-radius: 32px; font-weight: 900; font-size: 12px; text-transform: uppercase;">VIEW ORDER STATUS</a>
    </div>
    """
    await send_email(f"Order Confirmation #{order_id}", email, html_content)


async def send_order_confirmation(email: str, order_id: int, amount: float):
    async def _fallback():
        from app.tasks.email import send_order_confirmation_notification_task

        send_order_confirmation_notification_task.delay(email, order_id, amount)
        return {"status": "queued", "order_id": order_id}

    return await EMAIL_BREAKER.acall(_send_order_confirmation_impl, email, order_id, amount, fallback=_fallback)


async def _send_shipping_notification_impl(email: str, order_id: int, tracking_number: str, provider: str):
    html_content = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 24px;">
        <h1 style="font-size: 24px; font-weight: 900; letter-spacing: 0.05em; text-transform: uppercase;">Womanly</h1>
        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
        <p style="font-size: 16px; font-weight: 600; color: #64748b;">YOUR ORDER HAS SHIPPED</p>
        <p style="font-size: 14px; line-height: 1.6; color: #1e293b;">Great news! Your order <strong>#{order_id}</strong> has been shipped via <strong>{provider.upper()}</strong>.</p>
        <div style="background: #f8fafc; padding: 20px; border-radius: 16px; margin: 20px 0;">
            <p style="margin: 0; font-size: 12px; font-weight: 800; color: #64748b;">TRACKING NUMBER</p>
            <p style="margin: 5px 0 0 0; font-size: 20px; font-weight: 900; letter-spacing: 0.1em;">{tracking_number}</p>
        </div>
        <a href="http://localhost:3000/account/orders" style="display: inline-block; padding: 14px 28px; background: #0f172a; color: white; text-decoration: none; border-radius: 32px; font-weight: 900; font-size: 12px; text-transform: uppercase;">TRACK ORDER</a>
    </div>
    """
    await send_email(f"Your Womanly Order #{order_id} has shipped!", email, html_content)


async def send_shipping_notification(email: str, order_id: int, tracking_number: str, provider: str):
    async def _fallback():
        from app.tasks.email import send_shipping_notification_task

        send_shipping_notification_task.delay(email, order_id, tracking_number, provider)
        return {"status": "queued", "order_id": order_id}

    return await EMAIL_BREAKER.acall(_send_shipping_notification_impl, email, order_id, tracking_number, provider, fallback=_fallback)

# -----------------------------
# Secrets provider
# -----------------------------

class SecretProvider(ABC):
    @abstractmethod
    def get_secret(self, secret_name: str) -> str:
        pass

    @abstractmethod
    def get_secret_json(self, secret_name: str) -> dict:
        pass

    @abstractmethod
    def secret_exists(self, secret_name: str) -> bool:
        pass


class EnvSecretProvider(SecretProvider):
    def get_secret(self, secret_name: str) -> str:
        value = os.getenv(secret_name)
        if not value:
            raise ValueError(f"Secret '{secret_name}' not found in environment variables")
        return value

    def get_secret_json(self, secret_name: str) -> dict:
        value = self.get_secret(secret_name)
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            raise ValueError(f"Secret '{secret_name}' is not valid JSON")

    def secret_exists(self, secret_name: str) -> bool:
        return secret_name in os.environ


class AWSSecretsManagerProvider(SecretProvider):
    def __init__(self, region_name: str = "us-east-1"):
        try:
            import boto3
            self.client = boto3.client("secretsmanager", region_name=region_name)
        except ImportError:
            raise ImportError("boto3 is required for AWS Secrets Manager. Install with: pip install boto3")

    def get_secret(self, secret_name: str) -> str:
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            if "SecretString" in response:
                return response["SecretString"]
            logger.error(f"Binary secrets not supported: {secret_name}")
            raise ValueError(f"Secret '{secret_name}' is binary")
        except Exception as e:
            logger.error(f"Failed to retrieve secret '{secret_name}' from AWS: {str(e)}")
            raise

    def get_secret_json(self, secret_name: str) -> dict:
        value = self.get_secret(secret_name)
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            raise ValueError(f"Secret '{secret_name}' is not valid JSON")

    def secret_exists(self, secret_name: str) -> bool:
        try:
            self.client.describe_secret(SecretId=secret_name)
            return True
        except self.client.exceptions.ResourceNotFoundException:
            return False


class HashiCorpVaultProvider(SecretProvider):
    def __init__(self, vault_url: str, vault_token: str, mount_path: str = "secret"):
        try:
            import hvac
            self.client = hvac.Client(url=vault_url, token=vault_token)
            self.mount_path = mount_path
        except ImportError:
            raise ImportError("hvac is required for HashiCorp Vault. Install with: pip install hvac")

    def get_secret(self, secret_name: str) -> str:
        try:
            response = self.client.secrets.kv.v2.read_secret_version(path=secret_name, mount_point=self.mount_path)
            data = response["data"]["data"]
            if len(data) == 1:
                return list(data.values())[0]
            elif "value" in data:
                return data["value"]
            raise ValueError(f"Secret '{secret_name}' does not contain a 'value' field")
        except Exception as e:
            logger.error(f"Failed to retrieve secret '{secret_name}' from Vault: {str(e)}")
            raise

    def get_secret_json(self, secret_name: str) -> dict:
        response = self.client.secrets.kv.v2.read_secret_version(path=secret_name, mount_point=self.mount_path)
        return response["data"]["data"]

    def secret_exists(self, secret_name: str) -> bool:
        try:
            self.client.secrets.kv.v2.read_secret_version(path=secret_name, mount_point=self.mount_path)
            return True
        except self.client.exceptions.InvalidPath:
            return False


class AzureKeyVaultProvider(SecretProvider):
    def __init__(self, vault_url: str, credential=None):
        try:
            from azure.identity import DefaultAzureCredential
            from azure.keyvault.secrets import SecretClient
            if credential is None:
                credential = DefaultAzureCredential()
            self.client = SecretClient(vault_url=vault_url, credential=credential)
        except ImportError:
            raise ImportError("Azure SDK is required for Azure Key Vault. Install with: pip install azure-identity azure-keyvault-secrets")

    def get_secret(self, secret_name: str) -> str:
        try:
            secret = self.client.get_secret(secret_name)
            return secret.value
        except Exception as e:
            logger.error(f"Failed to retrieve secret '{secret_name}' from Azure Key Vault: {str(e)}")
            raise

    def get_secret_json(self, secret_name: str) -> dict:
        value = self.get_secret(secret_name)
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            raise ValueError(f"Secret '{secret_name}' is not valid JSON")

    def secret_exists(self, secret_name: str) -> bool:
        try:
            self.client.get_secret(secret_name)
            return True
        except Exception:
            return False


class SecretRotationTracker:
    def __init__(self):
        self.rotation_log: dict = {}

    def record_rotation(self, secret_name: str, rotated_by: str = "system"):
        self.rotation_log[secret_name] = {"rotated_at": datetime.utcnow().isoformat(), "rotated_by": rotated_by}
        logger.info(f"Secret '{secret_name}' rotated by {rotated_by}")

    def get_rotation_status(self, secret_name: str, rotation_interval_days: int = 90) -> dict:
        if secret_name not in self.rotation_log:
            return {"rotated": False, "needs_rotation": True}
        last_rotation = datetime.fromisoformat(self.rotation_log[secret_name]["rotated_at"])
        days_since_rotation = (datetime.utcnow() - last_rotation).days
        return {
            "rotated": True,
            "last_rotated_at": self.rotation_log[secret_name]["rotated_at"],
            "days_since_rotation": days_since_rotation,
            "needs_rotation": days_since_rotation >= rotation_interval_days,
        }


rotation_tracker = SecretRotationTracker()


def get_secret_provider(provider_type: str = "env", **kwargs) -> SecretProvider:
    providers = {
        "env": EnvSecretProvider,
        "aws": AWSSecretsManagerProvider,
        "vault": HashiCorpVaultProvider,
        "azure": AzureKeyVaultProvider,
    }
    if provider_type not in providers:
        raise ValueError(f"Unknown provider type: {provider_type}")
    return providers[provider_type](**kwargs)
