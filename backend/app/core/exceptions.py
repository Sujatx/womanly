"""
Centralized exception classes for the application.
All exceptions should inherit from AppException for consistent error handling.
"""

from typing import Any, Dict, Optional


class AppException(Exception):
    """Base application exception."""
    
    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


# Authentication & Security Exceptions

class InvalidCredentialsException(AppException):
    """Invalid email or password."""
    
    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(
            error_code="INVALID_CREDENTIALS",
            message=message,
            status_code=401
        )


class UserAlreadyExistsException(AppException):
    """User with this email already exists."""
    
    def __init__(self, email: str):
        super().__init__(
            error_code="USER_ALREADY_EXISTS",
            message=f"User with email {email} already exists",
            status_code=409,
            details={"field": "email", "value": email}
        )


class InvalidTokenException(AppException):
    """Token is invalid or expired."""
    
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(
            error_code="INVALID_TOKEN",
            message=message,
            status_code=401
        )


class TokenExpiredException(AppException):
    """Token has expired."""
    
    def __init__(self, message: str = "Token has expired"):
        super().__init__(
            error_code="TOKEN_EXPIRED",
            message=message,
            status_code=401
        )


class UnauthorizedException(AppException):
    """User is not authenticated."""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            error_code="UNAUTHORIZED",
            message=message,
            status_code=401
        )


class ForbiddenException(AppException):
    """User is authenticated but not authorized to access this resource."""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            error_code="FORBIDDEN",
            message=message,
            status_code=403
        )


# Resource Exceptions

class ProductNotFoundException(AppException):
    """Product not found."""
    
    def __init__(self, product_id: int):
        super().__init__(
            error_code="PRODUCT_NOT_FOUND",
            message=f"Product with ID {product_id} not found",
            status_code=404,
            details={"resource": "product", "id": product_id}
        )


class CategoryNotFoundException(AppException):
    """Category not found."""
    
    def __init__(self, category_slug: str):
        super().__init__(
            error_code="CATEGORY_NOT_FOUND",
            message=f"Category '{category_slug}' not found",
            status_code=404,
            details={"resource": "category", "slug": category_slug}
        )


class OrderNotFoundException(AppException):
    """Order not found."""
    
    def __init__(self, order_id: int):
        super().__init__(
            error_code="ORDER_NOT_FOUND",
            message=f"Order with ID {order_id} not found",
            status_code=404,
            details={"resource": "order", "id": order_id}
        )


class UserNotFoundException(AppException):
    """User not found."""
    
    def __init__(self, user_id: int):
        super().__init__(
            error_code="USER_NOT_FOUND",
            message=f"User with ID {user_id} not found",
            status_code=404,
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
            error_code="VALIDATION_ERROR",
            message=message,
            status_code=422,
            details=details or ({"field": field} if field else {})
        )


class InvalidPriceException(AppException):
    """Price validation failed."""
    
    def __init__(self, message: str = "Price must be greater than 0"):
        super().__init__(
            error_code="INVALID_PRICE",
            message=message,
            status_code=422
        )


class InvalidStockQuantityException(AppException):
    """Stock quantity validation failed."""
    
    def __init__(self, message: str = "Stock quantity must be non-negative"):
        super().__init__(
            error_code="INVALID_STOCK_QUANTITY",
            message=message,
            status_code=422
        )


class InvalidPaginationException(AppException):
    """Pagination parameters are invalid."""
    
    def __init__(self, field: str, min_val: int, max_val: int):
        super().__init__(
            error_code="INVALID_PAGINATION",
            message=f"{field} must be between {min_val} and {max_val}",
            status_code=422,
            details={"field": field, "min": min_val, "max": max_val}
        )


# Payment Exceptions

class PaymentFailedException(AppException):
    """Payment processing failed."""
    
    def __init__(self, message: str = "Payment processing failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_code="PAYMENT_FAILED",
            message=message,
            status_code=402,  # Payment Required
            details=details
        )


class InvalidSignatureException(AppException):
    """Payment signature verification failed."""
    
    def __init__(self, message: str = "Invalid payment signature"):
        super().__init__(
            error_code="INVALID_SIGNATURE",
            message=message,
            status_code=400
        )


class DuplicatePaymentException(AppException):
    """Duplicate payment request detected."""
    
    def __init__(self, message: str = "Duplicate payment request"):
        super().__init__(
            error_code="DUPLICATE_PAYMENT",
            message=message,
            status_code=409  # Conflict
        )


# Stock Exceptions

class InsufficientStockException(AppException):
    """Product variant is out of stock."""
    
    def __init__(self, variant_id: int, available: int = 0, requested: int = 1):
        super().__init__(
            error_code="INSUFFICIENT_STOCK",
            message=f"Insufficient stock for variant {variant_id}. Available: {available}, Requested: {requested}",
            status_code=409,  # Conflict
            details={"variant_id": variant_id, "available": available, "requested": requested}
        )


class OutOfStockException(AppException):
    """Product variant is completely out of stock."""
    
    def __init__(self, variant_id: int):
        super().__init__(
            error_code="OUT_OF_STOCK",
            message=f"Variant {variant_id} is out of stock",
            status_code=409,
            details={"variant_id": variant_id}
        )


# Order Exceptions

class InvalidOrderTransitionException(AppException):
    """Invalid order status transition."""
    
    def __init__(self, current_status: str, requested_status: str):
        super().__init__(
            error_code="INVALID_ORDER_TRANSITION",
            message=f"Cannot transition from '{current_status}' to '{requested_status}'",
            status_code=400,
            details={"current_status": current_status, "requested_status": requested_status}
        )


class OrderAlreadyCanceledException(AppException):
    """Order has already been cancelled."""
    
    def __init__(self, order_id: int):
        super().__init__(
            error_code="ORDER_ALREADY_CANCELLED",
            message=f"Order {order_id} has already been cancelled",
            status_code=400,
            details={"order_id": order_id}
        )


# Configuration Exceptions

class ConfigurationException(AppException):
    """Application configuration error."""
    
    def __init__(self, message: str):
        super().__init__(
            error_code="CONFIGURATION_ERROR",
            message=message,
            status_code=500
        )


# External Service Exceptions

class ExternalServiceException(AppException):
    """External service (Razorpay, Email, etc.) failed."""
    
    def __init__(self, service_name: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_code=f"{service_name.upper()}_ERROR",
            message=f"{service_name} service error: {message}",
            status_code=503,  # Service Unavailable
            details=details
        )


class EmailServiceException(AppException):
    """Email sending failed."""
    
    def __init__(self, message: str = "Failed to send email"):
        super().__init__(
            error_code="EMAIL_SERVICE_ERROR",
            message=message,
            status_code=503
        )


class RazorpayException(AppException):
    """Razorpay API error."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_code=error_code or "RAZORPAY_ERROR",
            message=message,
            status_code=502,  # Bad Gateway
            details=details
        )


# Generic Server Error

class InternalServerException(AppException):
    """Unexpected internal server error."""
    
    def __init__(self, message: str = "Internal server error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_code="INTERNAL_SERVER_ERROR",
            message=message,
            status_code=500,
            details=details
        )
