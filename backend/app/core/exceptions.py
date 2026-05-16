"""
Centralized exception classes for the application.
All exceptions should inherit from AppException for consistent error handling.

Exceptions use structured error codes from app.core.error_codes for consistent API responses.
"""

from typing import Any, Dict, Optional
from app.core.error_codes import ErrorCode, get_error_info


class AppException(Exception):
    """Base application exception with structured error code."""
    
    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int | None = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        
        # If no status code provided, look it up from error codes
        if status_code is None:
            status_code, _, _ = get_error_info(error_code)
        self.status_code = status_code
        
        super().__init__(self.message)


# Authentication & Security Exceptions

class InvalidCredentialsException(AppException):
    """Invalid email or password."""
    
    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(
            error_code=ErrorCode.AUTH_INVALID_CREDENTIALS,
            message=message,
        )


class UserAlreadyExistsException(AppException):
    """User with this email already exists."""
    
    def __init__(self, email: str):
        super().__init__(
            error_code=ErrorCode.USER_ALREADY_EXISTS,
            message=f"User with email {email} already exists",
            details={"field": "email", "value": email}
        )


class InvalidTokenException(AppException):
    """Token is invalid or expired."""
    
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(
            error_code=ErrorCode.AUTH_TOKEN_INVALID,
            message=message,
        )


class TokenExpiredException(AppException):
    """Token has expired."""
    
    def __init__(self, message: str = "Token has expired"):
        super().__init__(
            error_code=ErrorCode.AUTH_TOKEN_EXPIRED,
            message=message,
        )


class UnauthorizedException(AppException):
    """User is not authenticated."""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            error_code=ErrorCode.AUTH_TOKEN_INVALID,
            message=message,
        )


class ForbiddenException(AppException):
    """User is authenticated but not authorized to access this resource."""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            error_code=ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS,
            message=message,
        )


# Resource Exceptions

class ProductNotFoundException(AppException):
    """Product not found."""
    
    def __init__(self, product_id: int):
        super().__init__(
            error_code=ErrorCode.INVENTORY_PRODUCT_NOT_FOUND,
            message=f"Product with ID {product_id} not found",
            details={"resource": "product", "id": product_id}
        )


class CategoryNotFoundException(AppException):
    """Category not found."""
    
    def __init__(self, category_slug: str):
        super().__init__(
            error_code=ErrorCode.INVENTORY_PRODUCT_NOT_FOUND,
            message=f"Category '{category_slug}' not found",
            details={"resource": "category", "slug": category_slug}
        )


class OrderNotFoundException(AppException):
    """Order not found."""
    
    def __init__(self, order_id: int):
        super().__init__(
            error_code=ErrorCode.ORDER_NOT_FOUND,
            message=f"Order with ID {order_id} not found",
            details={"resource": "order", "id": order_id}
        )


class UserNotFoundException(AppException):
    """User not found."""
    
    def __init__(self, user_id: int):
        super().__init__(
            error_code=ErrorCode.USER_NOT_FOUND,
            message=f"User with ID {user_id} not found",
            details={"resource": "user", "id": user_id}
        )


class CartNotFoundException(AppException):
    """Cart not found."""
    
    def __init__(self, cart_id: int):
        super().__init__(
            error_code="CART_NOT_FOUND",
            message=f"Cart with ID {cart_id} not found",
            status_code=404,
            details={"resource": "cart", "id": cart_id}
        )


# Validation Exceptions

class ValidationException(AppException):
    """Input validation failed."""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_code=ErrorCode.VALIDATION_INVALID_FORMAT,
            message=message,
            details=details or ({"field": field} if field else {})
        )


class InvalidPriceException(AppException):
    """Price validation failed."""
    
    def __init__(self, message: str = "Price must be greater than 0"):
        super().__init__(
            error_code=ErrorCode.VALIDATION_INVALID_FORMAT,
            message=message,
        )


class InvalidStockQuantityException(AppException):
    """Stock quantity validation failed."""
    
    def __init__(self, message: str = "Stock quantity must be non-negative"):
        super().__init__(
            error_code=ErrorCode.VALIDATION_INVALID_FORMAT,
            message=message,
        )


class InvalidPaginationException(AppException):
    """Pagination parameters are invalid."""
    
    def __init__(self, field: str, min_val: int, max_val: int):
        super().__init__(
            error_code=ErrorCode.VALIDATION_INVALID_PAGINATION,
            message=f"{field} must be between {min_val} and {max_val}",
            details={"field": field, "min": min_val, "max": max_val}
        )


# Payment Exceptions

class PaymentFailedException(AppException):
    """Payment processing failed."""
    
    def __init__(self, message: str = "Payment processing failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_code=ErrorCode.PAYMENT_FAILED,
            message=message,
            details=details
        )


class InvalidSignatureException(AppException):
    """Payment signature verification failed."""
    
    def __init__(self, message: str = "Invalid payment signature"):
        super().__init__(
            error_code=ErrorCode.VALIDATION_INVALID_FORMAT,
            message=message,
        )


class DuplicatePaymentException(AppException):
    """Duplicate payment request detected."""
    
    def __init__(self, message: str = "Duplicate payment request"):
        super().__init__(
            error_code=ErrorCode.PAYMENT_DUPLICATE,
            message=message,
        )


# Stock Exceptions

class InsufficientStockException(AppException):
    """Product variant is out of stock."""
    
    def __init__(self, variant_id: int, available: int = 0, requested: int = 1):
        super().__init__(
            error_code=ErrorCode.INVENTORY_INSUFFICIENT,
            message=f"Insufficient stock for variant {variant_id}. Available: {available}, Requested: {requested}",
            details={"variant_id": variant_id, "available": available, "requested": requested}
        )


class OutOfStockException(AppException):
    """Product variant is completely out of stock."""
    
    def __init__(self, variant_id: int):
        super().__init__(
            error_code=ErrorCode.INVENTORY_OUT_OF_STOCK,
            message=f"Variant {variant_id} is out of stock",
            details={"variant_id": variant_id}
        )


# Order Exceptions

class InvalidOrderTransitionException(AppException):
    """Invalid order status transition."""
    
    def __init__(self, current_status: str, requested_status: str):
        super().__init__(
            error_code=ErrorCode.ORDER_INVALID_STATE_TRANSITION,
            message=f"Cannot transition from '{current_status}' to '{requested_status}'",
            details={"current_status": current_status, "requested_status": requested_status}
        )


class OrderAlreadyCanceledException(AppException):
    """Order has already been cancelled."""
    
    def __init__(self, order_id: int):
        super().__init__(
            error_code=ErrorCode.ORDER_ALREADY_CANCELLED,
            message=f"Order {order_id} has already been cancelled",
            details={"order_id": order_id}
        )


# Configuration Exceptions

class ConfigurationException(AppException):
    """Application configuration error."""
    
    def __init__(self, message: str):
        super().__init__(
            error_code=ErrorCode.INTERNAL_CONFIG_ERROR,
            message=message,
        )


# External Service Exceptions

class ExternalServiceException(AppException):
    """External service (Razorpay, Email, etc.) failed."""
    
    def __init__(self, service_name: str, message: str, details: Optional[Dict[str, Any]] = None):
        code_map = {
            "razorpay": ErrorCode.EXTERNAL_PAYMENT_UNAVAILABLE,
            "email": ErrorCode.EXTERNAL_EMAIL_UNAVAILABLE,
            "shipping": ErrorCode.EXTERNAL_SHIPPING_UNAVAILABLE,
        }
        super().__init__(
            error_code=code_map.get(service_name.lower(), ErrorCode.EXTERNAL_SERVICE_ERROR),
            message=f"{service_name} service error: {message}",
            details=details
        )


class EmailServiceException(AppException):
    """Email sending failed."""
    
    def __init__(self, message: str = "Failed to send email"):
        super().__init__(
            error_code=ErrorCode.EXTERNAL_EMAIL_UNAVAILABLE,
            message=message,
        )


class RazorpayException(AppException):
    """Razorpay API error."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_code=error_code or ErrorCode.PAYMENT_RAZORPAY_ERROR,
            message=message,
            details=details
        )


# Generic Server Error

class InternalServerException(AppException):
    """Unexpected internal server error."""
    
    def __init__(self, message: str = "Internal server error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_code=ErrorCode.INTERNAL_ERROR,
            message=message,
            details=details
        )
