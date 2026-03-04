"""
Health check endpoints for monitoring and load balancing.

Provides three levels of health checks:
1. Basic health check - just confirms the service is running
2. Deep health check - tests all critical dependencies
3. Readiness check - determines if the service is ready to accept traffic
"""

from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, Response, status
from sqlalchemy import text
from app.db import get_session, get_pool_status
from app.config import settings
from app.core.logging import get_structured_logger
import asyncio

logger = get_structured_logger(__name__)

router = APIRouter()


class HealthCheckResult:
    """Result of a health check."""
    
    def __init__(self, name: str, status: str, response_time_ms: float, message: Optional[str] = None):
        self.name = name
        self.status = status  # "healthy", "degraded", "unhealthy"
        self.response_time_ms = response_time_ms
        self.message = message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "name": self.name,
            "status": self.status,
            "response_time_ms": round(self.response_time_ms, 2)
        }
        if self.message:
            result["message"] = self.message
        return result


async def check_database() -> HealthCheckResult:
    """Check database connectivity."""
    start_time = datetime.now()
    
    try:
        session = next(get_session())
        # Simple query to test connection
        result = session.exec(text("SELECT 1")).first()
        
        elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        if result and result[0] == 1:
            return HealthCheckResult("database", "healthy", elapsed_ms)
        else:
            return HealthCheckResult("database", "unhealthy", elapsed_ms, "Unexpected query result")
    
    except Exception as e:
        elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
        logger.error("Database health check failed", error=str(e), exc_info=True)
        return HealthCheckResult("database", "unhealthy", elapsed_ms, str(e))


async def check_razorpay() -> HealthCheckResult:
    """Check Razorpay API connectivity."""
    start_time = datetime.now()
    
    try:
        # For now, just check if credentials are configured
        # In a real scenario, you might ping Razorpay's API
        from app.services.razorpay_service import razorpay_client
        
        if razorpay_client:
            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
            # TODO: Add actual Razorpay API ping when implementing
            return HealthCheckResult("razorpay", "healthy", elapsed_ms, "Configuration OK")
        else:
            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
            return HealthCheckResult("razorpay", "degraded", elapsed_ms, "Client not configured")
    
    except Exception as e:
        elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
        logger.error("Razorpay health check failed", error=str(e))
        return HealthCheckResult("razorpay", "unhealthy", elapsed_ms, str(e))


async def check_email_service() -> HealthCheckResult:
    """Check email service connectivity."""
    start_time = datetime.now()
    
    try:
        # Check if email credentials are configured
        # In production, you might test SMTP connection
        if settings.MAIL_USERNAME and settings.MAIL_PASSWORD:
            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
            return HealthCheckResult("email", "healthy", elapsed_ms, "Configuration OK")
        else:
            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
            return HealthCheckResult("email", "degraded", elapsed_ms, "Email not configured")
    
    except Exception as e:
        elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
        logger.error("Email service health check failed", error=str(e))
        return HealthCheckResult("email", "unhealthy", elapsed_ms, str(e))


async def check_connection_pool() -> HealthCheckResult:
    """Check database connection pool status."""
    start_time = datetime.now()
    
    try:
        pool_status = get_pool_status()
        elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        # Determine health based on pool utilization
        utilization = pool_status["utilization_percent"]
        
        if utilization >= 90:
            # Critical: pool nearly exhausted
            return HealthCheckResult(
                "connection_pool",
                "unhealthy",
                elapsed_ms,
                f"Pool {utilization}% full - risk of exhaustion"
            )
        elif utilization >= 75:
            # Warning: high utilization
            return HealthCheckResult(
                "connection_pool",
                "degraded",
                elapsed_ms,
                f"Pool {utilization}% full - high utilization"
            )
        else:
            # Healthy
            return HealthCheckResult(
                "connection_pool",
                "healthy",
                elapsed_ms,
                f"{pool_status['checked_in']}/{pool_status['pool_size']} connections available"
            )
    
    except Exception as e:
        elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
        logger.error("Connection pool health check failed", error=str(e))
        return HealthCheckResult("connection_pool", "unhealthy", elapsed_ms, str(e))


@router.get("/health")
def basic_health_check():
    """
    Basic health check - just confirms the service is running.
    
    Returns 200 if the service is up.
    Used by monitoring systems to detect if the process is alive.
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "womanly-api",
        "environment": settings.ENV_NAME
    }


@router.get("/health/deep")
async def deep_health_check(response: Response):
    """
    Deep health check - tests all critical dependencies.
    
    Checks:
    - Database connectivity
    - Connection pool status
    - Razorpay API access
    - Email service configuration
    
    Returns 200 if all services are healthy.
    Returns 503 if any critical service is unhealthy.
    """
    start_time = datetime.now()
    
    # Run all checks in parallel for speed
    checks = await asyncio.gather(
        check_database(),
        check_connection_pool(),
        check_razorpay(),
        check_email_service(),
        return_exceptions=True
    )
    
    # Convert any exceptions to unhealthy results
    results = []
    for check in checks:
        if isinstance(check, Exception):
            results.append(HealthCheckResult("unknown", "unhealthy", 0, str(check)))
        else:
            results.append(check)
    
    # Determine overall status
    unhealthy_count = sum(1 for r in results if r.status == "unhealthy")
    degraded_count = sum(1 for r in results if r.status == "degraded")
    
    if unhealthy_count > 0:
        overall_status = "unhealthy"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif degraded_count > 0:
        overall_status = "degraded"
        response.status_code = status.HTTP_200_OK
    else:
        overall_status = "healthy"
        response.status_code = status.HTTP_200_OK
    
    elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
    
    # Log unhealthy services
    if overall_status != "healthy":
        logger.warning(
            "Health check detected issues",
            overall_status=overall_status,
            unhealthy_count=unhealthy_count,
            degraded_count=degraded_count
        )
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "total_time_ms": round(elapsed_ms, 2),
        "checks": [r.to_dict() for r in results]
    }


@router.get("/health/ready")
async def readiness_check(response: Response):
    """
    Readiness check - determines if the service is ready to accept traffic.
    
    Used by load balancers and orchestrators (Kubernetes) to determine
    if the service should receive traffic.
    
    Returns 200 if ready to accept traffic.
    Returns 503 if not ready (during startup, maintenance, etc.).
    """
    # For now, just check database connectivity (most critical)
    db_check = await check_database()
    
    if db_check.status == "healthy":
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
    else:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "not_ready",
            "timestamp": datetime.utcnow().isoformat(),
            "reason": "Database not accessible"
        }
