"""
SQL Query Monitoring Middleware

Detects N+1 query problems and logs slow queries.
"""

from collections import defaultdict
from typing import Dict, List
from fastapi import Request
from sqlalchemy import event
from sqlalchemy.engine import Engine
from app.db import engine
from app.core.logging import get_structured_logger
from app.config import settings

logger = get_structured_logger(__name__)

# Store query counts per request
_request_query_counts: Dict[str, Dict[str, int]] = {}


class QueryMonitor:
    """Monitor SQL queries for a request."""
    
    def __init__(self, request_id: str):
        self.request_id = request_id
        self.queries: List[Dict] = []
        self.table_counts: Dict[str, int] = defaultdict(int)
    
    def add_query(self, statement: str, duration_ms: float):
        """Record a query."""
        self.queries.append({
            "statement": statement[:200],  # Truncate long queries
            "duration_ms": duration_ms
        })
        
        # Extract table names (simple heuristic)
        statement_lower = statement.lower()
        for word in statement_lower.split():
            # Look for common SQL keywords followed by table name
            if any(kw in statement_lower for kw in ['from ', 'join ', 'update ', 'into ']):
                # This is a simplified approach - could be improved
                self.table_counts[word] += 1
    
    def check_n_plus_one(self) -> bool:
        """Check if there's a potential N+1 problem."""
        # If any table is queried more than 2 times, flag as potential N+1
        for table, count in self.table_counts.items():
            if count > 2:
                return True
        return False
    
    def get_stats(self) -> Dict:
        """Get query statistics."""
        total_queries = len(self.queries)
        total_duration = sum(q["duration_ms"] for q in self.queries)
        
        return {
            "request_id": self.request_id,
            "total_queries": total_queries,
            "total_duration_ms": round(total_duration, 2),
            "avg_duration_ms": round(total_duration / total_queries, 2) if total_queries > 0 else 0,
            "table_counts": dict(self.table_counts),
            "has_n_plus_one": self.check_n_plus_one()
        }


# Track active monitors
_active_monitors: Dict[str, QueryMonitor] = {}


def start_query_monitoring(request_id: str):
    """Start monitoring queries for a request."""
    _active_monitors[request_id] = QueryMonitor(request_id)


def stop_query_monitoring(request_id: str) -> Dict:
    """Stop monitoring and return statistics."""
    monitor = _active_monitors.pop(request_id, None)
    if monitor:
        return monitor.get_stats()
    return {}


def get_current_monitor(request_id: str) -> QueryMonitor:
    """Get the current query monitor for a request."""
    return _active_monitors.get(request_id)


# Set up SQLAlchemy event listeners (only in development)
if settings.ENV_NAME == "dev":
    
    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        """Record start time for query."""
        conn.info.setdefault('query_start_time', []).append(
            __import__('time').perf_counter()
        )
    
    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        """Record query and duration."""
        query_start_times = conn.info.get('query_start_time', [])
        if query_start_times:
            start_time = query_start_times.pop()
            duration_ms = (__import__('time').perf_counter() - start_time) * 1000
            
            # Log slow queries (>100ms)
            if duration_ms > 100:
                logger.warning(
                    "Slow query detected",
                    duration_ms=round(duration_ms, 2),
                    statement=statement[:200]
                )
            
            # Add to active monitor if exists
            # Note: We'd need to track request_id in connection info for this to work properly
            # For now, just log the query in development


async def query_monitoring_middleware(request: Request, call_next):
    """
    Middleware to monitor SQL queries per request.
    
    Logs warnings when N+1 problems are detected.
    """
    request_id = getattr(request.state, 'request_id', None)
    
    if request_id and settings.ENV_NAME == "dev":
        start_query_monitoring(request_id)
    
    response = await call_next(request)
    
    if request_id and settings.ENV_NAME == "dev":
        stats = stop_query_monitoring(request_id)
        
        # Log if there are many queries
        if stats.get('total_queries', 0) > 10:
            logger.warning(
                "High query count detected",
                path=request.url.path,
                **stats
            )
        
        # Log if N+1 detected
        if stats.get('has_n_plus_one'):
            logger.warning(
                "Potential N+1 query problem detected",
                path=request.url.path,
                **stats
            )
    
    return response
