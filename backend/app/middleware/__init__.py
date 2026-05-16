"""
Consolidated middleware package for the backend.

This package groups the cross-cutting HTTP middleware and helper functions in one place
so the app doesn't have to bounce across many tiny files.
"""

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from hashlib import md5, sha256
from typing import Optional
import hashlib
import json
import logging
import re
import time
import uuid

from fastapi import HTTPException, Request, status
from prometheus_client import Counter, Gauge, Histogram
from sqlmodel import Session, select
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

# -----------------------------
# Security headers
# -----------------------------

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        if "server" in response.headers:
            del response.headers["server"]
        return response


# -----------------------------
# Request validation
# -----------------------------

EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PHONE_PATTERN = re.compile(r"^[+]?[0-9]{7,15}$")
POSTAL_CODE_PATTERN = re.compile(r"^[0-9]{5,10}$")


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Validate request size and basic JSON format."""

    MAX_REQUEST_SIZE = 1024 * 1024
    EXCLUDED_PATHS = {"/health", "/"}

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)

        content_length = request.headers.get("Content-Length")
        if content_length and int(content_length) > self.MAX_REQUEST_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Request body too large. Maximum size is {self.MAX_REQUEST_SIZE / 1024 / 1024}MB",
            )

        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("Content-Type", "")
            if "application/json" in content_type:
                try:
                    body = await request.body()
                    if len(body) > self.MAX_REQUEST_SIZE:
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"Request body too large. Maximum size is {self.MAX_REQUEST_SIZE / 1024 / 1024}MB",
                        )
                    if body:
                        json.loads(body)
                except json.JSONDecodeError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid JSON in request body",
                    )

        return await call_next(request)


def validate_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.match(email))


def validate_phone(phone: str) -> bool:
    return bool(PHONE_PATTERN.match(phone))


def validate_postal_code(postal_code: str) -> bool:
    return bool(POSTAL_CODE_PATTERN.match(postal_code))


def validate_field(field_type: str, value: str) -> bool:
    validators = {
        "email": validate_email,
        "phone": validate_phone,
        "postal_code": validate_postal_code,
    }
    validator = validators.get(field_type)
    return True if not validator else validator(value)


class FieldValidationError(Exception):
    def __init__(self, field: str, value: str, field_type: str):
        self.field = field
        self.value = value
        self.field_type = field_type
        super().__init__(f"Invalid {field_type} format for field '{field}': {value}")


def create_validation_error_response(field: str, field_type: str, value: str) -> dict:
    return {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": f"Invalid {field_type} format",
        },
        "details": {
            "field": field,
            "issue": f"Invalid {field_type} format",
            "received_value": value[:20] if len(value) > 20 else value,
        },
    }


# -----------------------------
# CSRF
# -----------------------------

class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """CSRF protection middleware."""

    EXCLUDED_PATHS = {
        "/health",
        "/",
        "/api/v1/auth/signup",
        "/api/v1/auth/login",
        "/api/v1/auth/verify-email",
        "/docs",
        "/openapi.json",
    }
    STATE_CHANGING_METHODS = {"POST", "PUT", "DELETE", "PATCH"}

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in self.EXCLUDED_PATHS or request.method not in self.STATE_CHANGING_METHODS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return await call_next(request)

        csrf_token = request.headers.get("X-CSRF-Token")
        if not csrf_token:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "CSRF token missing. Include X-CSRF-Token header for state-changing requests."},
            )

        return await call_next(request)


def generate_csrf_token_value() -> str:
    return str(uuid.uuid4())


def create_csrf_token_in_db(session: Session, session_id: str = None) -> str:
    from app.models.user import CSRFToken

    token = generate_csrf_token_value()
    csrf_token = CSRFToken(
        token=token,
        session_id=session_id or str(uuid.uuid4()),
        expires_at=datetime.utcnow() + timedelta(hours=1),
    )
    session.add(csrf_token)
    session.commit()
    return token


def validate_csrf_token(session: Session, token: str) -> bool:
    from app.models.user import CSRFToken

    csrf_token = session.exec(select(CSRFToken).where(CSRFToken.token == token)).first()
    if not csrf_token:
        logger.warning(f"Invalid CSRF token attempted: {token[:10]}...")
        return False
    if csrf_token.expires_at < datetime.utcnow():
        logger.warning("CSRF token expired")
        return False
    if csrf_token.is_used:
        logger.warning("CSRF token already used")
        return False

    csrf_token.is_used = True
    session.add(csrf_token)
    session.commit()
    return True


def get_csrf_token_dependency(request: Request, session: Session):
    csrf_token = request.headers.get("X-CSRF-Token")
    if not csrf_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF token missing")
    if not validate_csrf_token(session, csrf_token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or expired CSRF token")
    return True


# -----------------------------
# Idempotency
# -----------------------------

IDEMPOTENT_ENDPOINTS = {
    "/api/v1/payments/create-order",
    "/api/v1/payments/verify",
}
IDEMPOTENCY_KEY_TTL = timedelta(hours=1)


async def store_idempotency_key(
    session: Session,
    idempotency_key: str,
    user_id: int,
    endpoint: str,
    request_body: bytes,
    response_json: str,
    response_status: int,
):
    from app.models.idempotency import IdempotencyKey

    request_hash = sha256(request_body).hexdigest()
    key = IdempotencyKey(
        idempotency_key=idempotency_key,
        user_id=user_id,
        endpoint=endpoint,
        request_hash=request_hash,
        response_json=response_json,
        response_status_code=response_status,
        expires_at=datetime.now(timezone.utc) + IDEMPOTENCY_KEY_TTL,
    )
    session.add(key)
    session.commit()
    logger.info(f"Stored idempotency key: {idempotency_key} for {endpoint}")


async def get_cached_response(session: Session, idempotency_key: str, endpoint: str, user_id: int):
    from app.models.idempotency import IdempotencyKey

    key = session.exec(
        select(IdempotencyKey)
        .where(IdempotencyKey.idempotency_key == idempotency_key)
        .where(IdempotencyKey.endpoint == endpoint)
        .where(IdempotencyKey.user_id == user_id)
    ).first()

    if not key:
        return None
    if key.is_expired():
        session.delete(key)
        session.commit()
        return None
    return key


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """Validate idempotency keys for payment endpoints."""

    async def dispatch(self, request: Request, call_next):
        if request.url.path not in IDEMPOTENT_ENDPOINTS:
            return await call_next(request)

        idempotency_key = request.headers.get("Idempotency-Key")
        if not idempotency_key:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Idempotency-Key header is required for payment endpoints"},
            )

        if len(idempotency_key) < 8 or len(idempotency_key) > 255:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Invalid Idempotency-Key format"},
            )

        return await call_next(request)


def get_idempotency_key_from_request(request: Request) -> str:
    idempotency_key = request.headers.get("Idempotency-Key")
    if not idempotency_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Idempotency-Key header is required")
    return idempotency_key


# -----------------------------
# Rate limiting
# -----------------------------

class RateLimitStore:
    def __init__(self):
        self.attempts = defaultdict(list)

    def is_rate_limited(self, key: str, max_attempts: int, window_seconds: int) -> bool:
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(seconds=window_seconds)
        self.attempts[key] = [attempt_time for attempt_time in self.attempts[key] if attempt_time > cutoff]
        if len(self.attempts[key]) >= max_attempts:
            return True
        self.attempts[key].append(now)
        return False

    def get_remaining(self, key: str, max_attempts: int) -> int:
        return max(0, max_attempts - len(self.attempts.get(key, [])))

    def reset(self, key: str):
        if key in self.attempts:
            del self.attempts[key]


rate_limit_store = RateLimitStore()


class RateLimitMiddleware(BaseHTTPMiddleware):
    RATE_LIMITS = {
        "/api/v1/auth/login": {"max_attempts": 5, "window_seconds": 15 * 60},
        "/api/v1/auth/signup": {"max_attempts": 3, "window_seconds": 60 * 60},
        "/api/v1/auth/verify-email": {"max_attempts": 10, "window_seconds": 60 * 60},
    }

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path not in self.RATE_LIMITS:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        config = self.RATE_LIMITS[path]
        max_attempts = config["max_attempts"]
        window_seconds = config["window_seconds"]
        rate_limit_key = f"{path}:{client_ip}"

        if rate_limit_store.is_rate_limited(rate_limit_key, max_attempts, window_seconds):
            logger.warning(f"Rate limit exceeded for {path} from IP {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many attempts. Please try again later."},
                headers={
                    "Retry-After": str(window_seconds),
                    "X-RateLimit-Limit": str(max_attempts),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)
        remaining = rate_limit_store.get_remaining(rate_limit_key, max_attempts)
        response.headers["X-RateLimit-Limit"] = str(max_attempts)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int((datetime.now(timezone.utc) + timedelta(seconds=window_seconds)).timestamp()))
        return response


def get_rate_limit_key(request: Request, identifier: str = None) -> str:
    if identifier:
        return f"{request.url.path}:{identifier}"
    client_ip = request.client.host if request.client else "unknown"
    return f"{request.url.path}:{client_ip}"


def check_rate_limit(key: str, max_attempts: int = 5, window_seconds: int = 900) -> bool:
    return rate_limit_store.is_rate_limited(key, max_attempts, window_seconds)


# -----------------------------
# Metrics
# -----------------------------

HTTP_REQUESTS_TOTAL = Counter(
    "womanly_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "womanly_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path", "status"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)

HTTP_INFLIGHT_REQUESTS = Gauge(
    "womanly_http_inflight_requests",
    "In-flight HTTP requests",
)

HTTP_SERVER_ERRORS_TOTAL = Counter(
    "womanly_http_server_errors_total",
    "Total unhandled server-side errors",
    ["method", "path"],
)


def _resolve_route_path(request) -> str:
    route = request.scope.get("route")
    if route and getattr(route, "path", None):
        return route.path
    return request.url.path


async def metrics_middleware(request, call_next):
    method = request.method
    start = time.perf_counter()
    HTTP_INFLIGHT_REQUESTS.inc()

    status_code = "500"
    path_label = request.url.path

    try:
        response = await call_next(request)
        status_code = str(response.status_code)
        path_label = _resolve_route_path(request)
        return response
    except Exception:
        path_label = _resolve_route_path(request)
        HTTP_SERVER_ERRORS_TOTAL.labels(method=method, path=path_label).inc()
        raise
    finally:
        elapsed = time.perf_counter() - start
        HTTP_REQUESTS_TOTAL.labels(method=method, path=path_label, status=status_code).inc()
        HTTP_REQUEST_DURATION_SECONDS.labels(method=method, path=path_label, status=status_code).observe(elapsed)
        HTTP_INFLIGHT_REQUESTS.dec()


# -----------------------------
# Cache headers
# -----------------------------

class CacheControlMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        path = request.url.path

        if response.status_code >= 400:
            response.headers["Cache-Control"] = "no-store"
            return response

        if path.startswith("/api/v1/products") and request.method == "GET":
            response.headers["Cache-Control"] = "public, max-age=3600, stale-while-revalidate=7200"
        elif path.startswith("/api/v1/categories") and request.method == "GET":
            response.headers["Cache-Control"] = "public, max-age=86400, stale-while-revalidate=172800"
        elif path.startswith("/health") or path.startswith("/api/v1/health"):
            response.headers["Cache-Control"] = "public, max-age=30"
        elif path.startswith("/api/v1/") and request.method == "GET":
            if "user" in path or "cart" in path or "order" in path or "wishlist" in path:
                response.headers["Cache-Control"] = "private, no-cache, no-store, must-revalidate"
            else:
                response.headers["Cache-Control"] = "public, max-age=300"
        elif path.startswith("/api/"):
            response.headers["Cache-Control"] = "private, no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        else:
            response.headers["Cache-Control"] = "no-cache, must-revalidate"

        if request.method == "GET" and response.status_code < 400:
            cache_control = response.headers.get("Cache-Control", "")
            is_cacheable = "no-store" not in cache_control and "private" not in cache_control
            if is_cacheable:
                body = b""
                async for chunk in response.body_iterator:
                    body += chunk

                etag = f'W/"{hashlib.md5(body).hexdigest()}"'
                incoming_etag = request.headers.get("If-None-Match")
                if incoming_etag == etag:
                    return Response(status_code=304, headers={"ETag": etag})

                headers = dict(response.headers)
                headers["ETag"] = etag
                return Response(
                    content=body,
                    status_code=response.status_code,
                    headers=headers,
                    media_type=response.media_type,
                    background=response.background,
                )

        return response
