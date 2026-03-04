"""
Text sanitization utilities to prevent XSS and HTML injection attacks.
"""

import html
import re
import logging

logger = logging.getLogger(__name__)

# Try to import bleach for HTML sanitization
try:
    import bleach
    BLEACH_AVAILABLE = True
except ImportError:
    BLEACH_AVAILABLE = False
    logger.warning("bleach not installed. Using html.escape only for sanitization.")


# Allowed HTML tags and attributes for rich text (conservative list)
ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'a']
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title']
}


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    if not isinstance(text, str):
        return text
    return html.escape(text)


def sanitize_text(text: str, allow_html: bool = False) -> str:
    """
    Sanitize text input to prevent XSS/HTML injection.
    
    Args:
        text: Text to sanitize
        allow_html: If True, allow safe HTML tags; if False, escape all HTML
    
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return text
    
    # Remove null characters
    text = text.replace('\x00', '')
    
    if not allow_html:
        # Escape all HTML
        return escape_html(text)
    
    # Allow safe HTML tags
    if BLEACH_AVAILABLE:
        return bleach.clean(
            text,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            strip=True  # Strip disallowed tags instead of escaping
        )
    else:
        # Fallback to escaping if bleach not available
        logger.warning("bleach not available, escaping HTML")
        return escape_html(text)


def sanitize_json_field(data: dict, field_name: str, allow_html: bool = False) -> None:
    """
    Sanitize a specific field in a dictionary.
    Modifies the dictionary in place.
    
    Args:
        data: Dictionary to sanitize
        field_name: Name of field to sanitize
        allow_html: If True, allow safe HTML tags
    """
    if field_name in data and isinstance(data[field_name], str):
        data[field_name] = sanitize_text(data[field_name], allow_html=allow_html)


def sanitize_product_description(description: str) -> str:
    """Sanitize product description - allow limited HTML for formatting."""
    return sanitize_text(description, allow_html=True)


def sanitize_user_name(name: str) -> str:
    """Sanitize user name - no HTML allowed."""
    return sanitize_text(name, allow_html=False)


def sanitize_address(address: str) -> str:
    """Sanitize address - no HTML allowed."""
    return sanitize_text(address, allow_html=False)


def sanitize_email(email: str) -> str:
    """Sanitize email - no HTML allowed, basic validation."""
    email = escape_html(email).strip().lower()
    
    # Basic email validation pattern
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        logger.warning(f"Invalid email format detected: {email[:20]}...")
    
    return email


def sanitize_phone(phone: str) -> str:
    """Sanitize phone number - only allow digits and plus sign."""
    phone = phone.strip()
    
    # Remove any characters except digits, spaces, dashes, and plus
    phone = re.sub(r'[^\d\s\-\+]', '', phone)
    
    # Remove spaces
    phone = phone.replace(' ', '')
    
    return phone


def sanitize_all_text_fields(data: dict, text_fields: list) -> dict:
    """
    Sanitize multiple text fields in a dictionary.
    Returns a new dictionary with sanitized values.
    
    Args:
        data: Dictionary to sanitize
        text_fields: List of field names to sanitize
    
    Returns:
        New dictionary with sanitized fields
    """
    sanitized = data.copy()
    
    for field in text_fields:
        if field in sanitized and isinstance(sanitized[field], str):
            sanitized[field] = sanitize_text(sanitized[field])
    
    return sanitized


def test_xss_payload(text: str) -> bool:
    """
    Test if text contains potential XSS payloads.
    Returns True if potential XSS detected.
    """
    xss_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',  # Event handlers like onclick=
        r'<iframe',
        r'<embed',
        r'<object',
    ]
    
    text_lower = text.lower()
    for pattern in xss_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL):
            return True
    
    return False
