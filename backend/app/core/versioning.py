"""
API Versioning Module

This module provides utilities for API versioning and helps manage
the transition from unversioned to versioned APIs.

VERSIONING STRATEGY:
====================

Current State:
- Legacy unversioned routes (/, /products, /auth, etc.)

Target State:
- Versioned routes (/api/v1/products, /api/v1/auth, etc.)
- Support for multiple API versions simultaneously

Migration Path:
1. Phase 1: Add v1 routes alongside legacy routes (both work)
2. Phase 2: Add deprecation warnings to legacy routes
3. Phase 3: Remove legacy routes (after 6-12 months)

Version Support Policy:
- Each major version supported for minimum 12 months
- Breaking changes only in major versions (v1 → v2)
- Deprecation warnings 6 months before removal
- Version sunset announced 3 months in advance
"""

from fastapi import APIRouter, Request, Response
from typing import Callable
import warnings
from datetime import datetime
from app.core.logging import get_structured_logger

logger = get_structured_logger(__name__)

# API version configuration
CURRENT_VERSION = "v1"
SUPPORTED_VERSIONS = ["v1"]
DEPRECATED_VERSIONS = []  # Will include v0 (unversioned) in future

# Deprecation dates
LEGACY_API_DEPRECATION_DATE = datetime(2026, 9, 1)  # 6 months from now
LEGACY_API_SUNSET_DATE = datetime(2027, 3, 1)  # 12 months from now


def create_versioned_router(prefix: str, version: str = "v1") -> APIRouter:
    """
    Create a versioned API router.
    
    Args:
        prefix: Route prefix (e.g., "products", "auth")
        version: API version (default: "v1")
    
    Returns:
        APIRouter with versioned prefix
    """
    return APIRouter(prefix=f"/api/{version}/{prefix}")


def add_deprecation_warning(response: Response, sunset_date: datetime) -> None:
    """
    Add deprecation warning headers to response.
    
    Args:
        response: FastAPI Response object
        sunset_date: Date when the endpoint will be removed
    """
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = sunset_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
    response.headers["Link"] = '<https://docs.womanly.com/api/migration>; rel="deprecation"'


async def deprecation_middleware(request: Request, call_next: Callable):
    """
    Middleware to add deprecation warnings to legacy (unversioned) routes.
    
    Logs deprecation usage and adds headers to inform clients.
    """
    path = request.url.path
    
    # Check if this is a legacy route (doesn't start with /api/v)
    is_legacy_route = (
        not path.startswith("/api/v") 
        and path not in ["/", "/health", "/docs", "/redoc", "/openapi.json"]
    )
    
    if is_legacy_route:
        # Log deprecation usage
        logger.warning(
            "Legacy API endpoint accessed",
            path=path,
            method=request.method,
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            deprecation_date=LEGACY_API_DEPRECATION_DATE.isoformat(),
            sunset_date=LEGACY_API_SUNSET_DATE.isoformat()
        )
    
    # Process the request
    response = await call_next(request)
    
    # Add deprecation headers to legacy routes
    if is_legacy_route:
        add_deprecation_warning(response, LEGACY_API_SUNSET_DATE)
    
    return response


def get_api_version_info() -> dict:
    """
    Get information about API versions.
    
    Returns:
        Dictionary with version info
    """
    return {
        "current_version": CURRENT_VERSION,
        "supported_versions": SUPPORTED_VERSIONS,
        "deprecated_versions": DEPRECATED_VERSIONS,
        "legacy_api_deprecation_date": LEGACY_API_DEPRECATION_DATE.isoformat(),
        "legacy_api_sunset_date": LEGACY_API_SUNSET_DATE.isoformat(),
        "migration_guide": "https://docs.womanly.com/api/migration"
    }
