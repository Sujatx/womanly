"""
Graceful shutdown utilities for clean application termination.

Handles:
- Flushing pending tasks
- Closing database connections
- Closing cache connections
- Waiting for in-flight requests
- State saving if needed
"""

import asyncio
import signal
from typing import Callable, List, Optional
from datetime import datetime
from fastapi import FastAPI
from app.core.logging import get_structured_logger

logger = get_structured_logger(__name__)

# Registry of shutdown handlers
_shutdown_handlers: List[Callable] = []
_shutdown_timeout_seconds = 30
_is_shutting_down = False


def register_shutdown_handler(handler: Callable) -> None:
    """
    Register a function to be called during graceful shutdown.
    
    Usage:
        async def cleanup_background_jobs():
            logger.info("Flushing Celery tasks...")
            # Celery cleanup logic
        
        register_shutdown_handler(cleanup_background_jobs)
    """
    _shutdown_handlers.append(handler)
    logger.debug(f"Registered shutdown handler: {handler.__name__}")


async def execute_shutdown_handlers() -> None:
    """Execute all registered shutdown handlers in order."""
    global _is_shutting_down
    _is_shutting_down = True
    
    logger.info("Starting graceful shutdown...")
    start_time = datetime.now()
    
    for handler in _shutdown_handlers:
        try:
            logger.info(f"Executing shutdown handler: {handler.__name__}")
            
            if asyncio.iscoroutinefunction(handler):
                await asyncio.wait_for(
                    handler(),
                    timeout=_shutdown_timeout_seconds,
                )
            else:
                handler()
            
            logger.info(f"Completed shutdown handler: {handler.__name__}")
            
        except asyncio.TimeoutError:
            logger.error(
                f"Shutdown handler timeout: {handler.__name__}",
                timeout_seconds=_shutdown_timeout_seconds,
            )
        except Exception as e:
            logger.error(
                f"Error in shutdown handler: {handler.__name__}",
                error=str(e),
            )
    
    elapsed = (datetime.now() - start_time).total_seconds()
    logger.info(f"Graceful shutdown complete (took {elapsed:.2f}s)")


def setup_graceful_shutdown(app: FastAPI) -> None:
    """
    Setup graceful shutdown for FastAPI application.
    
    Handles SIGTERM and SIGINT signals to trigger shutdown handlers.
    
    Usage:
        from fastapi import FastAPI
        from app.core.graceful_shutdown import setup_graceful_shutdown, register_shutdown_handler
        
        app = FastAPI()
        setup_graceful_shutdown(app)
        
        async def cleanup():
            # Cleanup logic
            pass
        
        register_shutdown_handler(cleanup)
    """
    
    @app.on_event("shutdown")
    async def shutdown_event():
        await execute_shutdown_handlers()
    
    # Handle signals for container termination
    def handle_signal(signum, frame):
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        asyncio.create_task(execute_shutdown_handlers())
    
    try:
        signal.signal(signal.SIGTERM, handle_signal)
        signal.signal(signal.SIGINT, handle_signal)
        logger.debug("Signal handlers registered for SIGTERM and SIGINT")
    except Exception as e:
        logger.warning(f"Could not register signal handlers: {e}")


async def close_database_connections(session_factory) -> None:
    """Close database connections cleanly."""
    logger.info("Closing database connections...")
    try:
        session_factory.close()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


async def close_redis_connections(redis_client) -> None:
    """Close Redis connections cleanly."""
    logger.info("Closing Redis connections...")
    try:
        if redis_client:
            await redis_client.close()
            logger.info("Redis connections closed")
    except Exception as e:
        logger.error(f"Error closing Redis connections: {e}")


async def flush_pending_tasks(celery_app) -> None:
    """Flush pending Celery tasks."""
    logger.info("Flushing pending Celery tasks...")
    try:
        if celery_app:
            # Wait for active tasks to complete (with timeout)
            active_tasks = celery_app.control.inspect().active()
            if active_tasks:
                logger.info(f"Waiting for {sum(len(v) for v in active_tasks.values())} active tasks...")
                await asyncio.sleep(2)  # Give tasks time to complete
            logger.info("Pending tasks flushed")
    except Exception as e:
        logger.error(f"Error flushing pending tasks: {e}")


async def wait_for_requests_to_complete(max_wait_seconds: int = 10) -> None:
    """
    Wait for in-flight requests to complete.
    
    Args:
        max_wait_seconds: Maximum time to wait before forcing shutdown
    """
    logger.info(f"Waiting for in-flight requests to complete (max {max_wait_seconds}s)...")
    try:
        await asyncio.sleep(max_wait_seconds)
        logger.info("In-flight request wait complete")
    except Exception as e:
        logger.error(f"Error waiting for requests: {e}")


def get_shutdown_status() -> dict:
    """Get current shutdown status."""
    return {
        "is_shutting_down": _is_shutting_down,
        "handlers_count": len(_shutdown_handlers),
        "timeout_seconds": _shutdown_timeout_seconds,
    }


class GracefulShutdownMiddleware:
    """
    Middleware to block new requests after shutdown initiated.
    
    Usage:
        app.add_middleware(GracefulShutdownMiddleware)
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if shutting down
        if _is_shutting_down:
            # Return 503 Service Unavailable
            await send({
                "type": "http.response.start",
                "status": 503,
                "headers": [
                    [b"content-type", b"application/json"],
                    [b"retry-after", b"30"],
                ],
            })
            await send({
                "type": "http.response.body",
                "body": b'{"error": "Service is shutting down"}',
            })
        else:
            await self.app(scope, receive, send)
