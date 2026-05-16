"""
Structured error codes for the Womanly API.

Error code format: E-{DOMAIN}-{NUMBER}
- E-AUTH-* : Authentication & authorization errors
- E-ORDER-* : Order operation errors
- E-PAYMENT-* : Payment processing errors
- E-INVENTORY-* : Stock & inventory errors
- E-VALIDATION-* : Input validation errors
- E-EXTERNAL-* : Third-party service errors
- E-INTERNAL-* : Server errors
"""

from enum import Enum
from typing import Dict, Tuple

# Map error code to (HTTP status, message, suggestion)
ERROR_CODES: Dict[str, Tuple[int, str, str]] = {
    # Authentication & Authorization (401, 403)
    "E-AUTH-001": (401, "Invalid credentials", "Check your email and password"),
    "E-AUTH-002": (401, "Token expired", "Please log in again"),
    "E-AUTH-003": (401, "Token invalid", "Please log in again"),
    "E-AUTH-004": (403, "Insufficient permissions", "Contact support for access"),
    "E-AUTH-005": (401, "Email not verified", "Check your email for verification link"),
    "E-AUTH-006": (401, "Account disabled", "Contact support"),
    
    # User Operations (400, 409)
    "E-USER-001": (409, "User already exists", "Use a different email or log in"),
    "E-USER-002": (404, "User not found", "Check the user ID"),
    "E-USER-003": (400, "Cannot delete own account", "Use settings page instead"),
    
    # Orders (400, 404, 409)
    "E-ORDER-001": (404, "Order not found", "Check the order ID"),
    "E-ORDER-002": (409, "Order already confirmed", "Cannot modify confirmed orders"),
    "E-ORDER-003": (400, "Invalid order state transition", "Check allowed transitions"),
    "E-ORDER-004": (400, "Order contains no items", "Add items before checkout"),
    "E-ORDER-005": (409, "Order already cancelled", "Cannot operate on cancelled orders"),
    "E-ORDER-006": (400, "Order state invalid for refund", "Check order status"),
    "E-ORDER-007": (400, "Refund amount exceeds order total", "Check refund amount"),
    
    # Payments (400, 402, 409)
    "E-PAYMENT-001": (402, "Payment failed", "Try a different payment method"),
    "E-PAYMENT-002": (400, "Invalid payment method", "Select a valid payment method"),
    "E-PAYMENT-003": (400, "Payment amount mismatch", "Restart the checkout process"),
    "E-PAYMENT-004": (409, "Duplicate payment attempt", "Please wait before retrying"),
    "E-PAYMENT-005": (400, "Razorpay error", "Try again or contact support"),
    "E-PAYMENT-006": (400, "Refund failed", "Contact support"),
    
    # Inventory & Stock (400, 409)
    "E-INVENTORY-001": (400, "Product out of stock", "Choose a different product"),
    "E-INVENTORY-002": (400, "Insufficient stock", "Reduce quantity or choose different variant"),
    "E-INVENTORY-003": (404, "Product not found", "Check the product ID"),
    "E-INVENTORY-004": (404, "Product variant not found", "Check the variant ID"),
    "E-INVENTORY-005": (409, "Cannot reserve stock", "Product may be out of stock"),
    "E-INVENTORY-006": (400, "Stock reservation expired", "Re-add items to cart"),
    
    # Cart (400, 404)
    "E-CART-001": (404, "Cart item not found", "Check the item ID"),
    "E-CART-002": (400, "Cart is empty", "Add items before checkout"),
    "E-CART-003": (400, "Invalid quantity", "Quantity must be positive"),
    
    # Addresses (400, 404)
    "E-ADDRESS-001": (404, "Address not found", "Check the address ID"),
    "E-ADDRESS-002": (400, "Cannot delete default address", "Set another address as default first"),
    
    # Discounts & Coupons (400, 404, 409)
    "E-DISCOUNT-001": (404, "Coupon not found", "Check the coupon code"),
    "E-DISCOUNT-002": (400, "Coupon expired", "The coupon is no longer valid"),
    "E-DISCOUNT-003": (400, "Coupon already used", "Each coupon can be used once"),
    "E-DISCOUNT-004": (400, "Coupon minimum order not met", "Increase order amount"),
    "E-DISCOUNT-005": (400, "Coupon not applicable", "Check coupon restrictions"),
    "E-DISCOUNT-006": (409, "Coupon usage limit exceeded", "Coupon limit reached"),
    
    # Validation (400)
    "E-VALIDATION-001": (400, "Invalid email format", "Enter a valid email address"),
    "E-VALIDATION-002": (400, "Invalid phone format", "Enter a valid phone number"),
    "E-VALIDATION-003": (400, "Password too weak", "Use at least 8 characters with mixed case"),
    "E-VALIDATION-004": (400, "Required field missing", "Fill all required fields"),
    "E-VALIDATION-005": (400, "Invalid input format", "Check the request format"),
    "E-VALIDATION-006": (400, "Invalid pagination parameters", "Check skip and limit values"),
    "E-VALIDATION-007": (400, "Invalid sort parameter", "Check the sort field name"),
    
    # External Services (503, 502, 500)
    "E-EXTERNAL-001": (503, "Email service unavailable", "Try again in a few moments"),
    "E-EXTERNAL-002": (503, "Payment provider unavailable", "Try again in a few moments"),
    "E-EXTERNAL-003": (503, "Shipping provider unavailable", "Try again in a few moments"),
    "E-EXTERNAL-004": (502, "External service error", "Try again later"),
    
    # Database & Server (500)
    "E-INTERNAL-001": (500, "Internal server error", "Contact support"),
    "E-INTERNAL-002": (500, "Database error", "Try again later"),
    "E-INTERNAL-003": (500, "Configuration error", "Contact support"),
}


class ErrorCode(str, Enum):
    """Typed error codes for IDE autocomplete."""
    # Auth
    AUTH_INVALID_CREDENTIALS = "E-AUTH-001"
    AUTH_TOKEN_EXPIRED = "E-AUTH-002"
    AUTH_TOKEN_INVALID = "E-AUTH-003"
    AUTH_INSUFFICIENT_PERMISSIONS = "E-AUTH-004"
    AUTH_EMAIL_NOT_VERIFIED = "E-AUTH-005"
    AUTH_ACCOUNT_DISABLED = "E-AUTH-006"
    
    # User
    USER_ALREADY_EXISTS = "E-USER-001"
    USER_NOT_FOUND = "E-USER-002"
    USER_CANNOT_DELETE_SELF = "E-USER-003"
    
    # Orders
    ORDER_NOT_FOUND = "E-ORDER-001"
    ORDER_ALREADY_CONFIRMED = "E-ORDER-002"
    ORDER_INVALID_STATE_TRANSITION = "E-ORDER-003"
    ORDER_EMPTY = "E-ORDER-004"
    ORDER_ALREADY_CANCELLED = "E-ORDER-005"
    ORDER_INVALID_FOR_REFUND = "E-ORDER-006"
    ORDER_REFUND_EXCEEDS_TOTAL = "E-ORDER-007"
    
    # Payments
    PAYMENT_FAILED = "E-PAYMENT-001"
    PAYMENT_INVALID_METHOD = "E-PAYMENT-002"
    PAYMENT_AMOUNT_MISMATCH = "E-PAYMENT-003"
    PAYMENT_DUPLICATE = "E-PAYMENT-004"
    PAYMENT_RAZORPAY_ERROR = "E-PAYMENT-005"
    PAYMENT_REFUND_FAILED = "E-PAYMENT-006"
    
    # Inventory
    INVENTORY_OUT_OF_STOCK = "E-INVENTORY-001"
    INVENTORY_INSUFFICIENT = "E-INVENTORY-002"
    INVENTORY_PRODUCT_NOT_FOUND = "E-INVENTORY-003"
    INVENTORY_VARIANT_NOT_FOUND = "E-INVENTORY-004"
    INVENTORY_RESERVATION_FAILED = "E-INVENTORY-005"
    INVENTORY_RESERVATION_EXPIRED = "E-INVENTORY-006"
    
    # Cart
    CART_ITEM_NOT_FOUND = "E-CART-001"
    CART_EMPTY = "E-CART-002"
    CART_INVALID_QUANTITY = "E-CART-003"
    
    # Addresses
    ADDRESS_NOT_FOUND = "E-ADDRESS-001"
    ADDRESS_CANNOT_DELETE_DEFAULT = "E-ADDRESS-002"
    
    # Discounts
    DISCOUNT_NOT_FOUND = "E-DISCOUNT-001"
    DISCOUNT_EXPIRED = "E-DISCOUNT-002"
    DISCOUNT_ALREADY_USED = "E-DISCOUNT-003"
    DISCOUNT_MINIMUM_NOT_MET = "E-DISCOUNT-004"
    DISCOUNT_NOT_APPLICABLE = "E-DISCOUNT-005"
    DISCOUNT_USAGE_LIMIT_EXCEEDED = "E-DISCOUNT-006"
    
    # Validation
    VALIDATION_INVALID_EMAIL = "E-VALIDATION-001"
    VALIDATION_INVALID_PHONE = "E-VALIDATION-002"
    VALIDATION_WEAK_PASSWORD = "E-VALIDATION-003"
    VALIDATION_REQUIRED_FIELD = "E-VALIDATION-004"
    VALIDATION_INVALID_FORMAT = "E-VALIDATION-005"
    VALIDATION_INVALID_PAGINATION = "E-VALIDATION-006"
    VALIDATION_INVALID_SORT = "E-VALIDATION-007"
    
    # External
    EXTERNAL_EMAIL_UNAVAILABLE = "E-EXTERNAL-001"
    EXTERNAL_PAYMENT_UNAVAILABLE = "E-EXTERNAL-002"
    EXTERNAL_SHIPPING_UNAVAILABLE = "E-EXTERNAL-003"
    EXTERNAL_SERVICE_ERROR = "E-EXTERNAL-004"
    
    # Internal
    INTERNAL_ERROR = "E-INTERNAL-001"
    INTERNAL_DB_ERROR = "E-INTERNAL-002"
    INTERNAL_CONFIG_ERROR = "E-INTERNAL-003"


def get_error_info(code: str) -> Tuple[int, str, str]:
    """
    Get HTTP status, message, and suggestion for an error code.
    
    Returns:
        (status_code, message, suggestion)
    """
    return ERROR_CODES.get(code, (500, "Internal server error", "Contact support"))
