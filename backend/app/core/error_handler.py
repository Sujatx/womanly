"""
Centralized error handling middleware.
Converts AppException instances to standardized JSON responses.
"""

import logging
import traceback
import uuid
from typing import Any, Dict
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.exceptions import AppException, InternalServerException
from app.core.logging import get_structured_logger, reset_request_id, set_request_id

logger = get_structured_logger(__name__)


class ErrorResponse:
    """Standardized error response format."""
    
    def __init__(
        self,
        error_code: str,
        message: str,
        request_id: str,
        details: Dict[str, Any] = None,
        status_code: int = 500
    ):
        self.error_code = error_code
        self.message = message
        self.request_id = request_id
        self.details = details or {}
        self.status_code = status_code
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response."""
        response = {
            "error": {
                "code": self.error_code,
                "message": self.message
            },
            "request_id": self.request_id
        }
        if self.details:
            response["error"]["details"] = self.details
        return response


def add_error_handlers(app: FastAPI) -> None:
    """Register all error handlers with the FastAPI app."""
    
    @app.middleware("http")
    async def add_request_id_middleware(request: Request, call_next):
        """Add request ID to request state for use in error handlers."""
        incoming_request_id = request.headers.get("X-Request-ID", "").strip()
        request_id = incoming_request_id if incoming_request_id else str(uuid.uuid4())

        request.state.request_id = request_id
        token = set_request_id(request_id)

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        reset_request_id(token)
        return response
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        """Handle custom AppException instances."""
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        
        # Prepare log context
        log_context = {
            "request_id": request_id,
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "user_id": getattr(request.state, "user_id", None),
            "path": request.url.path
        }
        
        if exc.status_code >= 500:
            logger.error(f"Server error: {exc.error_code}", exc_info=True, **log_context)
        elif exc.status_code >= 400:
            logger.warning(f"Client error: {exc.error_code}", **log_context)
        
        error_response = ErrorResponse(
            error_code=exc.error_code,
            message=exc.message,
            request_id=request_id,
            details=exc.details,
            status_code=exc.status_code
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.to_dict(),
            headers={"X-Request-ID": request_id}
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle Pydantic validation errors."""
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        
        # Extract field-level validation details
        details_list = []
        for error in exc.errors():
            field = ".".join(str(x) for x in error["loc"][1:])  # Skip "body" prefix
            details_list.append({
                "field": field,
                "issue": error["msg"],
                "type": error["type"]
            })
        
        error_response = ErrorResponse(
            error_code="VALIDATION_ERROR",
            message="Request validation failed",
            request_id=request_id,
            details={"fields": details_list},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        
        logger.warning(
            "Validation error",
            request_id=request_id,
            path=request.url.path,
            error_count=len(details_list)
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.to_dict(),
            headers={"X-Request-ID": request_id}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions."""
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        
        # Log full traceback for unexpected errors
        logger.error(
            f"Unexpected error: {type(exc).__name__}: {str(exc)}",
            request_id=request_id,
            path=request.url.path,
            user_id=getattr(request.state, "user_id", None),
            exc_info=True
        )
        
        # Return generic error to client (don't expose internals)
        error_response = ErrorResponse(
            error_code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred. Please try again later.",
            request_id=request_id,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.to_dict(),
            headers={"X-Request-ID": request_id}
        )
