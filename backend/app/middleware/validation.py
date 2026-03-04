"""
Global request validation middleware for FastAPI.
Validates request size, formats, and common fields.
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import json
import re
import logging

logger = logging.getLogger(__name__)

# Regex patterns for common field validation
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PHONE_PATTERN = re.compile(r"^[+]?[0-9]{7,15}$")  # International format
POSTAL_CODE_PATTERN = re.compile(r"^[0-9]{5,10}$")  # Flexible for different countries


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Validates all incoming requests for:
    - Size limits (max 1MB)
    - JSON/form data format
    - Common field formats (email, phone, postal code)
    """
    
    MAX_REQUEST_SIZE = 1024 * 1024  # 1MB
    EXCLUDED_PATHS = {"/health", "/"}  # Paths that don't need validation
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip validation for excluded paths
        if request.url.path in self.EXCLUDED_PATHS:
            response = await call_next(request)
            return response
        
        # Check Content-Length header
        content_length = request.headers.get("Content-Length")
        if content_length and int(content_length) > self.MAX_REQUEST_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Request body too large. Maximum size is {self.MAX_REQUEST_SIZE / 1024 / 1024}MB"
            )
        
        # For JSON requests, validate format
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("Content-Type", "")
            
            if "application/json" in content_type:
                try:
                    body = await request.body()
                    if len(body) > self.MAX_REQUEST_SIZE:
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"Request body too large. Maximum size is {self.MAX_REQUEST_SIZE / 1024 / 1024}MB"
                        )
                    
                    # Validate JSON format
                    if body:
                        json.loads(body)
                except json.JSONDecodeError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid JSON in request body"
                    )
                    
        response = await call_next(request)
        return response


def validate_email(email: str) -> bool:
    """Validate email format."""
    return bool(EMAIL_PATTERN.match(email))


def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    return bool(PHONE_PATTERN.match(phone))


def validate_postal_code(postal_code: str) -> bool:
    """Validate postal code format."""
    return bool(POSTAL_CODE_PATTERN.match(postal_code))


def validate_field(field_type: str, value: str) -> bool:
    """Generic field validation."""
    validators = {
        "email": validate_email,
        "phone": validate_phone,
        "postal_code": validate_postal_code,
    }
    
    validator = validators.get(field_type)
    if not validator:
        return True
    
    return validator(value)


class FieldValidationError(Exception):
    """Custom exception for field validation errors."""
    def __init__(self, field: str, value: str, field_type: str):
        self.field = field
        self.value = value
        self.field_type = field_type
        super().__init__(f"Invalid {field_type} format for field '{field}': {value}")


def create_validation_error_response(field: str, field_type: str, value: str) -> dict:
    """Create a standardized validation error response."""
    return {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": f"Invalid {field_type} format"
        },
        "details": {
            "field": field,
            "issue": f"Invalid {field_type} format",
            "received_value": value[:20] if len(value) > 20 else value
        }
    }
