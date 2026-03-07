from sqlmodel import SQLModel, create_engine, Session
from app.config import settings
from app.core.logging import get_structured_logger

logger = get_structured_logger(__name__)

# Connection pool configuration for production
# - pool_size: Number of connections to maintain in the pool
# - max_overflow: Additional connections that can be created beyond pool_size
# - pool_recycle: Recycle connections after this many seconds (prevents stale connections)
# - pool_pre_ping: Test connections before using them (detect dead connections)
POOL_SIZE = 20 if settings.ENV_NAME == "prod" else 5
MAX_OVERFLOW = 40 if settings.ENV_NAME == "prod" else 10
POOL_RECYCLE = 3600  # 1 hour

# Create the engine with connection pooling
engine = create_engine(
    settings.sync_database_url,
    echo=settings.ENV_NAME == "dev",  # Only log queries in development
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_recycle=POOL_RECYCLE,
    pool_pre_ping=True,  # Test connections before using
)

# Optional read replica engine (falls back to primary URL if READ_DATABASE_URL is not set)
read_engine = create_engine(
    settings.sync_read_database_url,
    echo=settings.ENV_NAME == "dev",
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_recycle=POOL_RECYCLE,
    pool_pre_ping=True,
)

logger.info(
    "Database engine configured",
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_recycle=POOL_RECYCLE,
    environment=settings.ENV_NAME
)

def get_session():
    with Session(engine) as session:
        yield session


def get_read_session():
    with Session(read_engine) as session:
        yield session

def get_pool_status():
    """Get current connection pool status for monitoring."""
    pool = engine.pool
    return {
        "size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "total_connections": pool.size() + pool.overflow()
    }
