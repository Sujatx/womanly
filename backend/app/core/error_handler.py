"""
Centralized error handling middleware.
Converts AppException instances to standardized response envelope format.
"""

import json
import logging
import traceback
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.error_codes import ErrorCode
from app.core.exceptions import AppException, InternalServerException
from app.core.logging import get_structured_logger, reset_request_id, set_request_id

logger = get_structured_logger(__name__)

CORRELATION_ID_HEADER = "X-Correlation-ID"


def create_success_response(
    data: Any,
    correlation_id: str,
    pagination: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create a success response envelope."""
    return {
        "status": "success",
        "data": data,
        "error": None,
        "metadata": {
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": correlation_id,
            "pagination": pagination,
        },
    }


def create_error_response(
    code: str,
    message: str,
    correlation_id: str,
    details: Optional[Dict[str, Any]] = None,
    suggestion: Optional[str] = None,
) -> Dict[str, Any]:
    """Create an error response envelope."""
    return {
        "status": "error",
        "data": None,
        "error": {
            "code": code,
            "message": message,
            "details": details,
            "suggestion": suggestion,
        },
        "metadata": {
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": correlation_id,
            "pagination": None,
        },
    }


class ResponseEnvelopeMiddleware(BaseHTTPMiddleware):
    """Wrap JSON responses in the standard response envelope."""

    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get(CORRELATION_ID_HEADER) or str(uuid.uuid4())
        request.state.correlation_id = correlation_id

        try:
            response = await call_next(request)
        except Exception as exc:
            logger.error(
                "Unhandled exception in request",
                correlation_id=correlation_id,
                error=str(exc),
                exc_info=True,
            )
            return JSONResponse(
                status_code=500,
                content=create_error_response(
                    code=ErrorCode.INTERNAL_ERROR,
                    message="Internal server error",
                    correlation_id=correlation_id,
                    details={"type": type(exc).__name__},
                ),
                headers={CORRELATION_ID_HEADER: correlation_id},
            )

        if response.headers.get("content-type", "").startswith("application/json"):
            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            try:
                data = json.loads(body) if body else None
            except json.JSONDecodeError:
                response.headers[CORRELATION_ID_HEADER] = correlation_id
                return response

            if response.status_code >= 400:
                if isinstance(data, dict) and "detail" in data:
                    data = create_error_response(
                        code=data.get("code", f"E-HTTP-{response.status_code}"),
                        message=data.get("detail", "Error"),
                        correlation_id=correlation_id,
                        details=data if "detail" in data else None,
                    )
            else:
                data = create_success_response(
                    data=data,
                    correlation_id=correlation_id,
                )

            response = JSONResponse(
                status_code=response.status_code,
                content=data,
                headers={CORRELATION_ID_HEADER: correlation_id},
            )
        else:
            response.headers[CORRELATION_ID_HEADER] = correlation_id

        return response


def add_error_handlers(app: FastAPI) -> None:
    """Register all error handlers with the FastAPI app."""
    
    @app.middleware("http")
    async def add_correlation_id_middleware(request: Request, call_next):
        """Add correlation ID to request state for use in error handlers."""
        incoming_correlation_id = request.headers.get("X-Correlation-ID", "").strip()
        correlation_id = incoming_correlation_id if incoming_correlation_id else str(uuid.uuid4())

        request.state.correlation_id = correlation_id
        token = set_request_id(correlation_id)

        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id

        reset_request_id(token)
        return response
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        """Handle custom AppException instances."""
        correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
        
        # Prepare log context
        log_context = {
            "correlation_id": correlation_id,
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "user_id": getattr(request.state, "user_id", None),
            "path": request.url.path
        }
        
        if exc.status_code >= 500:
            logger.error(f"Server error: {exc.error_code}", exc_info=True, **log_context)
        elif exc.status_code >= 400:
            logger.warning(f"Client error: {exc.error_code}", **log_context)
        
        error_response = create_error_response(
            code=exc.error_code,
            message=exc.message,
            correlation_id=correlation_id,
            details=exc.details,
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response,
            headers={"X-Correlation-ID": correlation_id}
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle Pydantic validation errors."""
        correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
        
        # Extract field-level validation details
        details_list = []
        for error in exc.errors():
            field = ".".join(str(x) for x in error["loc"][1:])  # Skip "body" prefix
            details_list.append({
                "field": field,
                "issue": error["msg"],
                "type": error["type"]
            })
        
        error_response = create_error_response(
            code=ErrorCode.VALIDATION_INVALID_FORMAT,
            message="Request validation failed",
            correlation_id=correlation_id,
            details={"fields": details_list},
        )
        
        logger.warning(
            "Validation error",
            correlation_id=correlation_id,
            path=request.url.path,
            error_count=len(details_list)
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response,
            headers={"X-Correlation-ID": correlation_id}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions."""
        correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
        
        # Log full traceback for unexpected errors
        logger.error(
            f"Unexpected error: {type(exc).__name__}: {str(exc)}",
            correlation_id=correlation_id,
            path=request.url.path,
            user_id=getattr(request.state, "user_id", None),
            exc_info=True
        )
        
        # Return generic error to client (don't expose internals)
        error_response = create_error_response(
            code=ErrorCode.INTERNAL_ERROR,
            message="An unexpected error occurred. Please try again later.",
            correlation_id=correlation_id,
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response,
            headers={"X-Correlation-ID": correlation_id}
        )
