"""
Query optimization utilities for performance monitoring and N+1 prevention.

Provides tools for:
- Query analysis and performance tracking
- N+1 detection and prevention
- Eager loading utilities
- Query result caching
"""

import time
import logging
from typing import Any, Callable, Optional, Dict, List, Tuple
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import event, select
from sqlalchemy.orm import Session
from sqlmodel import SQLModel
from app.core.logging import get_structured_logger

logger = get_structured_logger(__name__)

# Query execution statistics
query_stats: Dict[str, Dict[str, Any]] = {}

# Slow query threshold (milliseconds)
SLOW_QUERY_THRESHOLD_MS = 500

# Query cache for frequently accessed data
query_cache: Dict[str, Tuple[Any, datetime]] = {}
CACHE_TTL_SECONDS = 300  # 5 minutes default


def track_query_execution(session: Session, func: Callable):
    """
    Decorator to track query execution time and log slow queries.
    
    Usage:
        @track_query_execution(session)
        def get_user_with_orders(user_id: int):
            return session.exec(
                select(User).options(selectinload(User.orders))
                .where(User.id == user_id)
            ).first()
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time_ms = (time.time() - start_time) * 1000
            
            if execution_time_ms > SLOW_QUERY_THRESHOLD_MS:
                logger.warning(
                    f"Slow query detected",
                    function=func.__name__,
                    execution_time_ms=round(execution_time_ms, 2),
                    threshold_ms=SLOW_QUERY_THRESHOLD_MS,
                )
            else:
                logger.debug(
                    f"Query executed",
                    function=func.__name__,
                    execution_time_ms=round(execution_time_ms, 2),
                )
            
            # Track statistics
            if func.__name__ not in query_stats:
                query_stats[func.__name__] = {
                    "count": 0,
                    "total_time_ms": 0,
                    "avg_time_ms": 0,
                    "max_time_ms": 0,
                    "min_time_ms": float('inf'),
                }
            
            stats = query_stats[func.__name__]
            stats["count"] += 1
            stats["total_time_ms"] += execution_time_ms
            stats["avg_time_ms"] = stats["total_time_ms"] / stats["count"]
            stats["max_time_ms"] = max(stats["max_time_ms"], execution_time_ms)
            stats["min_time_ms"] = min(stats["min_time_ms"], execution_time_ms)
            
            return result
            
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Query execution failed",
                function=func.__name__,
                execution_time_ms=round(execution_time_ms, 2),
                error=str(e),
            )
            raise
    
    return wrapper


def cached_query(ttl_seconds: int = CACHE_TTL_SECONDS):
    """
    Decorator to cache query results.
    
    Usage:
        @cached_query(ttl_seconds=600)  # Cache for 10 minutes
        def get_featured_products(session: Session):
            return session.exec(
                select(Product).where(Product.is_featured == True)
            ).all()
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check if cached and not expired
            if cache_key in query_cache:
                result, cached_at = query_cache[cache_key]
                if datetime.now() - cached_at < timedelta(seconds=ttl_seconds):
                    logger.debug(f"Cache hit for {func.__name__}")
                    return result
            
            # Execute and cache result
            result = func(*args, **kwargs)
            query_cache[cache_key] = (result, datetime.now())
            logger.debug(f"Cached result for {func.__name__} (ttl={ttl_seconds}s)")
            
            return result
        
        return wrapper
    
    return decorator


def clear_query_cache(pattern: Optional[str] = None) -> int:
    """
    Clear query cache entries.
    
    Args:
        pattern: Optional pattern to match cache keys (e.g., 'get_products' clears all get_products* entries)
        
    Returns:
        Number of entries cleared
    """
    global query_cache
    
    if pattern is None:
        count = len(query_cache)
        query_cache.clear()
        logger.debug(f"Cleared entire query cache ({count} entries)")
        return count
    
    keys_to_delete = [k for k in query_cache.keys() if pattern in k]
    for key in keys_to_delete:
        del query_cache[key]
    
    logger.debug(f"Cleared query cache for pattern '{pattern}' ({len(keys_to_delete)} entries)")
    return len(keys_to_delete)


def get_query_statistics() -> Dict[str, Any]:
    """Get cumulative query execution statistics."""
    return query_stats.copy()


def reset_query_statistics() -> None:
    """Reset all query statistics."""
    global query_stats
    query_stats.clear()
    logger.debug("Query statistics reset")


class EagerLoadingHelper:
    """
    Helper class for eager loading relationships to prevent N+1 queries.
    
    Usage:
        from sqlalchemy.orm import selectinload
        
        # Instead of:
        # users = session.exec(select(User)).all()
        # for user in users:
        #     print(user.orders)  # N+1 queries!
        
        # Use eager loading:
        users = session.exec(
            select(User).options(selectinload(User.orders))
        ).all()
        for user in users:
            print(user.orders)  # No additional queries!
    """
    
    @staticmethod
    def selectinload_relationship(session: Session, model: type[SQLModel], relationship_name: str):
        """
        Load a relationship using selectinload (recommended for most cases).
        
        Selectinload uses a separate SELECT statement for the relationship,
        which is efficient for one-to-many and many-to-many relationships.
        """
        from sqlalchemy.orm import selectinload
        
        relationship = getattr(model, relationship_name)
        return select(model).options(selectinload(relationship))
    
    @staticmethod
    def joinedload_relationship(session: Session, model: type[SQLModel], relationship_name: str):
        """
        Load a relationship using joinedload.
        
        Joinedload uses a LEFT OUTER JOIN to load the relationship,
        which is efficient for many-to-one relationships.
        """
        from sqlalchemy.orm import joinedload
        
        relationship = getattr(model, relationship_name)
        return select(model).options(joinedload(relationship))
    
    @staticmethod
    def selectinload_multiple(
        session: Session,
        model: type[SQLModel],
        relationships: List[str],
    ):
        """
        Load multiple relationships using selectinload.
        
        Usage:
            users = session.exec(
                EagerLoadingHelper.selectinload_multiple(
                    User,
                    ["orders", "addresses"]
                )
            ).all()
        """
        from sqlalchemy.orm import selectinload
        
        query = select(model)
        for relationship_name in relationships:
            relationship = getattr(model, relationship_name)
            query = query.options(selectinload(relationship))
        
        return query


def detect_n_plus_one_queries(session: Session, enable: bool = True):
    """
    Enable N+1 query detection in development.
    
    Logs a warning when a query appears to trigger additional queries for
    loaded relationships (potential N+1 scenario).
    
    Usage:
        detect_n_plus_one_queries(session, enable=True)
        users = session.exec(select(User)).all()
        for user in users:
            _ = user.orders  # Logs warning about N+1
    """
    if not enable:
        return
    
    # Track previous query count
    prev_query_count = [0]
    detected_n_plus_one = []
    
    def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        prev_query_count[0] = conn.connection.queries.__len__() if hasattr(conn.connection, 'queries') else 0
    
    def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        # Check if query was in a loop (simplified detection)
        if "SELECT" in statement and statement.count("SELECT") > 1:
            logger.warning(f"Potential N+1 query detected: {statement[:100]}...")
    
    try:
        event.listen(session.connection(), "before_cursor_execute", receive_before_cursor_execute)
        event.listen(session.connection(), "after_cursor_execute", receive_after_cursor_execute)
    except Exception as e:
        logger.warning(f"Could not set up N+1 detection: {e}")


def profile_query_performance(func: Callable) -> Callable:
    """
    Decorator to profile query performance with detailed breakdown.
    
    Usage:
        @profile_query_performance
        def complex_report_query(session: Session):
            return session.exec(select(Order)).all()
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Starting profile for {func.__name__}")
        
        start_time = time.time()
        import gc
        gc.collect()
        
        result = func(*args, **kwargs)
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        logger.info(
            f"Profile complete for {func.__name__}",
            elapsed_time_ms=round(elapsed_ms, 2),
            result_count=len(result) if isinstance(result, list) else 1,
        )
        
        return result
    
    return wrapper
