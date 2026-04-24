from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from app.config import settings
from app.api import health, admin, metrics
from app.api.v1 import v1_router
from app.core.logging import setup_logging, get_structured_logger
from app.core.error_handler import add_error_handlers
from app.core.versioning import deprecation_middleware, get_api_version_info
from app.core.query_monitor import query_monitoring_middleware
from app.middleware.metrics import metrics_middleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.csrf import CSRFProtectionMiddleware
from app.middleware.validation import RequestValidationMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.cache_headers import CacheControlMiddleware

# Initialize Sentry for error monitoring (optional, only if DSN is configured)
if settings.SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        # Send user context in errors
        send_default_pii=False,  # Don't send PII by default
    )

# Initialize structured logging first
setup_logging()
logger = get_structured_logger(__name__)

app = FastAPI(title="Womanly API", version="1.0.0")

# Register centralized error handlers
add_error_handlers(app)

@app.on_event("startup")
def on_startup():
    # Validate that SECRET_KEY is properly set (not the default unsafe value)
    if not settings.SECRET_KEY or settings.SECRET_KEY.get_secret_value() == "unsafe_default":
        raise ValueError(
            "CRITICAL: SECRET_KEY environment variable must be set to a secure value. "
            "Set it in your .env file or environment before running the application."
        )
    
    logger.info("Application startup complete", environment=settings.ENV_NAME)

# Add Gzip compression (compress responses > 500 bytes)
app.add_middleware(GZipMiddleware, minimum_size=500)

# Add Cache-Control headers
app.add_middleware(CacheControlMiddleware)

# Add rate limiting middleware - early in chain
app.add_middleware(RateLimitMiddleware)

# Add query monitoring middleware (development only)
app.middleware("http")(query_monitoring_middleware)

# Add metrics middleware for request throughput, latency, and error rates
app.middleware("http")(metrics_middleware)

# Add deprecation middleware to flag unexpected non-versioned requests
app.middleware("http")(deprecation_middleware)

# CORS Configuration - Must be early to handle preflight requests
cors_origins = settings.get_cors_origins()

# Log CORS configuration (but not sensitive data)
if settings.ENV_NAME == "prod":
    logger.info("Production mode: CORS origins configured", cors_origins=cors_origins)
else:
    logger.info("Development mode: CORS origins configured", cors_origins=cors_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add CSRF protection middleware (after CORS to allow preflight)
app.add_middleware(CSRFProtectionMiddleware)

# Add request validation middleware
app.add_middleware(RequestValidationMiddleware)

# ========== API VERSION 1 (Recommended) ==========
app.include_router(v1_router)

# ========== ADMIN ENDPOINTS ==========
app.include_router(admin.router, tags=["admin"])

# ========== HEALTH CHECK ENDPOINTS ==========
app.include_router(health.router, tags=["health"])

# ========== METRICS ENDPOINT ==========
app.include_router(metrics.router, tags=["metrics"])



@app.get("/")
def read_root():
    return {
        "message": "Welcome to Womanly API",
        "env": settings.ENV_NAME,
        "api_version": "v1",
        "docs": "/docs",
        "version_info": "/api/version"
    }

@app.get("/api/version")
def get_version():
    """Get API version information and migration guide."""
    return get_api_version_info()