"""
Structured logging configuration.
Provides JSON-formatted logs with request tracing.
"""

import json
import logging
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, Optional
from app.config import settings


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for structured logging."""
    
    def __init__(self):
        super().__init__()
        self.service_name = "womanly-api"
        self.environment = settings.ENV_NAME
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "service": self.service_name,
            "environment": self.environment,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add request ID if available
        if hasattr(record, "request_id") and record.request_id:
            log_data["request_id"] = record.request_id
        
        # Add user ID if available
        if hasattr(record, "user_id") and record.user_id:
            log_data["user_id"] = record.user_id
        
        # Add custom extra fields
        if hasattr(record, "extra") and record.extra:
            log_data.update(record.extra)
        
        # Add other extra fields from LogRecord
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "healthCheck", "levelname", "levelno", "lineno", "module",
                "msecs", "message", "pathname", "process", "processName",
                "relativeCreated", "thread", "threadName", "exc_info",
                "exc_text", "stack_info", "extra", "request_id", "user_id"
            ]:
                value_str = str(value)
                if len(value_str) < 1000:  # Only include short values
                    log_data[key] = value
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }
        
        # Add source location
        log_data["source"] = {
            "file": record.filename,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        return json.dumps(log_data)


class RequestIdLogFilter(logging.Filter):
    """Add request ID from context to log records."""
    
    def __init__(self):
        super().__init__()
        self._request_id: Optional[str] = None
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add request ID if available."""
        # Will be set by middleware
        if not hasattr(record, "request_id"):
            record.request_id = self._request_id
        return True
    
    def set_request_id(self, request_id: str) -> None:
        """Set the current request ID."""
        self._request_id = request_id


def setup_logging() -> None:
    """Configure logging for the application."""
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if settings.ENV_NAME == "dev" else logging.INFO)
    
    # Remove any existing handlers
    root_logger.handlers.clear()
    
    # Create console handler with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = JSONFormatter()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Add request ID filter
    request_filter = RequestIdLogFilter()
    root_logger.addFilter(request_filter)
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO if settings.ENV_NAME == "dev" else logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    return logging.getLogger(name)


class StructuredLogger:
    """Helper class for structured logging with context."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def debug(self, message: str, **context) -> None:
        """Log debug message with context."""
        self.logger.debug(message, extra=context)
    
    def info(self, message: str, **context) -> None:
        """Log info message with context."""
        self.logger.info(message, extra=context)
    
    def warning(self, message: str, **context) -> None:
        """Log warning message with context."""
        self.logger.warning(message, extra=context)
    
    def error(self, message: str, exc_info: bool = False, **context) -> None:
        """Log error message with context."""
        self.logger.error(message, extra=context, exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = False, **context) -> None:
        """Log critical message with context."""
        self.logger.critical(message, extra=context, exc_info=exc_info)


def get_structured_logger(name: str) -> StructuredLogger:
    """Get a structured logger with the given name."""
    return StructuredLogger(get_logger(name))
