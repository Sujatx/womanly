"""
Idempotency key storage for payment requests.
Prevents duplicate orders from repeated requests.
"""

from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
import json


class IdempotencyKey(SQLModel, table=True):
    """
    Stores idempotency keys and their responses.
    Prevents duplicate payment processing from retried requests.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    idempotency_key: str = Field(unique=True, index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    endpoint: str = Field(index=True)  # e.g., "/api/v1/payments/create-order"
    request_hash: str  # Hash of request body
    response_json: str  # Stored as JSON string
    response_status_code: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime  # TTL for cleanup
    
    def get_response(self):
        """Deserialize stored response."""
        return json.loads(self.response_json)
    
    def is_expired(self) -> bool:
        """Check if idempotency key has expired."""
        expires_at = self.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) > expires_at
