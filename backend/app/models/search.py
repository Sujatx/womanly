"""
Search analytics model.
"""

from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field


class SearchLog(SQLModel, table=True):
    """
    Records every product search query for analytics.
    Used to identify top searches and zero-result queries.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    query: str = Field(index=True, description="Search query string")
    results_count: int = Field(ge=0, description="Number of results returned")
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", description="Null for anonymous")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        index=True
    )
