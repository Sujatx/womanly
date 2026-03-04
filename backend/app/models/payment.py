"""
Payment verification logging and tracking.
Logs all payment verification attempts for audit and security.
"""

from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class PaymentVerificationLog(SQLModel, table=True):
    """
    Logs all payment verification attempts.
    Used to detect and prevent payment replay attacks.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id", index=True)
    razorpay_order_id: str = Field(index=True)
    razorpay_payment_id: str = Field(index=True)
    razorpay_signature: str
    
    # Verification result
    is_valid: bool  # True if signature was valid
    
    # Attempt tracking
    attempt_number: int  # Sequential attempt number
    max_attempts: int = 3  # Max allowed attempts before hard fail
    failed_at: Optional[str] = None  # Error message if failed
    
    # Audit trail
    verified_at: datetime = Field(default_factory=datetime.utcnow)
    verified_by: str = Field(default="payment_service")  # User/service that verified
    ip_address: Optional[str] = None  # Client IP for audit
