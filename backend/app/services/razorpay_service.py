import razorpay
from app.config import settings
from sqlmodel import Session, select
from app.models.payment import PaymentVerificationLog
from app.models import Order
import logging
from datetime import datetime
import hmac
import hashlib
from app.core.circuit_breaker import CircuitBreaker
from app.core.exceptions import ExternalServiceException

logger = logging.getLogger(__name__)

RAZORPAY_BREAKER = CircuitBreaker("razorpay", "razorpay", failure_threshold=3, recovery_timeout=60)

# Initialize Razorpay client with secured credentials
try:
    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID.get_secret_value(),
            settings.RAZORPAY_KEY_SECRET.get_secret_value()
        )
    )
except Exception as e:
    logger.error("Failed to initialize Razorpay client. Check credentials.")
    client = None

# Maximum verification attempts per order
MAX_VERIFICATION_ATTEMPTS = 3


def create_razorpay_order(amount: int, currency: str = "INR", notes: dict = None):
    """
    Create a Razorpay order.
    Amount should be in the smallest currency unit (e.g., paise for INR).
    """
    data = {
        "amount": amount,
        "currency": currency,
        "notes": notes or {},
        "payment_capture": 1  # Auto-capture
    }
    def _create():
        if not client:
            raise RuntimeError("Razorpay client not initialized. Check credentials.")

        order = client.order.create(data=data)
        logger.info(f"Created Razorpay order: {order['id']}")
        return order

    try:
        return RAZORPAY_BREAKER.call(_create)
    except ExternalServiceException:
        raise
    except Exception as e:
        logger.error(f"Razorpay order creation failed: {str(e)}")
        raise ExternalServiceException("razorpay", str(e), {"operation": "create_order"}) from e


def verify_webhook_signature(payload: bytes, razorpay_signature: str) -> bool:
    """Verify a Razorpay webhook signature using the configured webhook secret."""
    secret = settings.RAZORPAY_WEBHOOK_SECRET.get_secret_value()
    if not secret:
        raise ExternalServiceException(
            "razorpay",
            "Razorpay webhook secret is not configured",
            {"operation": "verify_webhook_signature"},
        )

    digest = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, razorpay_signature)


def verify_payment_signature(
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
    session: Session = None,
    order_id: int = None,
    ip_address: str = None
) -> bool:
    """
    Verify payment signature with enhanced security logging.
    
    Args:
        razorpay_order_id: Razorpay order ID
        razorpay_payment_id: Razorpay payment ID
        razorpay_signature: Payment signature to verify
        session: Database session for logging
        order_id: Database order ID for audit trail
        ip_address: Client IP address for audit
    
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        
        # Verify signature with Razorpay
        is_valid = client.utility.verify_payment_signature(params_dict)
        
        # Log verification attempt (if session provided)
        if session and order_id:
            log_payment_verification(
                session=session,
                order_id=order_id,
                razorpay_order_id=razorpay_order_id,
                razorpay_payment_id=razorpay_payment_id,
                razorpay_signature=razorpay_signature,
                is_valid=is_valid,
                ip_address=ip_address
            )
        
        if is_valid:
            logger.info(f"Payment signature verified: {razorpay_order_id}")
        else:
            logger.warning(f"Payment signature verification failed: {razorpay_order_id}")
        
        return is_valid
        
    except Exception as e:
        logger.error(f"Signature verification error: {str(e)}")
        
        # Log the error even if exception occurs
        if session and order_id:
            log_payment_verification(
                session=session,
                order_id=order_id,
                razorpay_order_id=razorpay_order_id,
                razorpay_payment_id=razorpay_payment_id,
                razorpay_signature=razorpay_signature,
                is_valid=False,
                failed_at=str(e),
                ip_address=ip_address
            )
        
        return False


def log_payment_verification(
    session: Session,
    order_id: int,
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
    is_valid: bool,
    failed_at: str = None,
    ip_address: str = None
):
    """
    Log a payment verification attempt.
    Tracks all verification attempts to detect replay attacks and abuse.
    """
    # Get current attempt number
    attempt_count = session.exec(
        select(PaymentVerificationLog).where(
            PaymentVerificationLog.order_id == order_id
        )
    ).all()
    
    attempt_number = len(attempt_count) + 1
    
    # Create verification log
    log = PaymentVerificationLog(
        order_id=order_id,
        razorpay_order_id=razorpay_order_id,
        razorpay_payment_id=razorpay_payment_id,
        razorpay_signature=razorpay_signature,
        is_valid=is_valid,
        attempt_number=attempt_number,
        failed_at=failed_at,
        ip_address=ip_address
    )
    
    session.add(log)
    session.commit()
    
    # Alert if too many failed attempts
    if not is_valid and attempt_number >= MAX_VERIFICATION_ATTEMPTS:
        logger.critical(
            f"Payment verification failed {attempt_number} times for order {order_id}. "
            f"Blocking further attempts. IP: {ip_address}"
        )
    
    return log


def check_payment_verification_attempts(session: Session, order_id: int) -> bool:
    """
    Check if payment verification attempts have exceeded limit.
    Returns True if further verification attempts are allowed.
    """
    failed_attempts = session.exec(
        select(PaymentVerificationLog).where(
            PaymentVerificationLog.order_id == order_id,
            PaymentVerificationLog.is_valid == False
        )
    ).all()
    
    if len(failed_attempts) >= MAX_VERIFICATION_ATTEMPTS:
        logger.warning(f"Order {order_id} has exceeded max verification attempts")
        return False
    
    return True


def create_razorpay_refund(payment_id: str, amount: int, notes: dict = None) -> dict:
    """
    Issue a refund for a captured Razorpay payment.

    Args:
        payment_id: Razorpay payment ID to refund
        amount: Amount to refund in the smallest currency unit (paise)
        notes: Optional metadata for the refund

    Returns:
        Razorpay refund response dict
    """
    data = {
        "amount": amount,
        "notes": notes or {},
    }

    def _refund():
        if not client:
            raise RuntimeError("Razorpay client not initialized. Check credentials.")

        refund = client.payment.refund(payment_id, data)
        logger.info(f"Razorpay refund created: {refund.get('id')} for payment {payment_id}")
        return refund

    try:
        return RAZORPAY_BREAKER.call(_refund)
    except ExternalServiceException:
        raise
    except Exception as e:
        logger.error(f"Razorpay refund failed for payment {payment_id}: {str(e)}")
        raise ExternalServiceException("razorpay", str(e), {"operation": "refund", "payment_id": payment_id}) from e
