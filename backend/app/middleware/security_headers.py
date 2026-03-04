"""
Security headers middleware for FastAPI.
Adds security headers to all responses.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        
        # Strict-Transport-Security: Enforce HTTPS
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # X-Content-Type-Options: Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # X-Frame-Options: Prevent clickjacking attacks
        response.headers["X-Frame-Options"] = "DENY"
        
        # Content-Security-Policy: Restrict resources
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;"
        
        # Referrer-Policy: Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # X-XSS-Protection: Legacy XSS protection (for older browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Remove server header to hide implementation details
        if "server" in response.headers:
            del response.headers["server"]
        
        return response
