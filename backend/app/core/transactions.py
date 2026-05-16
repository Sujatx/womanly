"""
Transaction management utilities for atomic multi-table operations.

Provides context managers for explicit transaction boundaries, rollback
handling, and nested transaction support.
"""

from contextlib import contextmanager
from typing import Generator, Optional, Callable, Any
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlmodel import Session as SQLModelSession
from app.core.logging import get_structured_logger
from app.core.exceptions import AppException
from app.core.error_codes import ErrorCode

logger = get_structured_logger(__name__)


@contextmanager
def atomic_transaction(
    session: Session,
    savepoint_name: Optional[str] = None,
) -> Generator[Session, None, None]:
    """
    Context manager for atomic transactions with automatic rollback.
    
    Usage:
        with atomic_transaction(session) as txn:
            order = Order(...)
            session.add(order)
            inventory.quantity -= 1  # Update inventory
            session.flush()  # Flush to get order ID
            payment = Payment(order_id=order.id, ...)
            session.add(payment)
            # Automatic commit on exit, or rollback on exception
    
    Args:
        session: SQLAlchemy session
        savepoint_name: Optional savepoint name for nested transactions
        
    Yields:
        The session (for use in context)
        
    Raises:
        Any exception will trigger automatic rollback
    """
    savepoint = None
    try:
        if savepoint_name:
            savepoint = session.begin_nested()
            logger.debug(f"Started nested transaction (savepoint: {savepoint_name})")
        
        yield session
        
        # Auto-commit on successful exit
        if savepoint:
            savepoint.commit()
            logger.debug(f"Committed nested transaction (savepoint: {savepoint_name})")
        else:
            session.commit()
            logger.debug("Transaction committed")
            
    except Exception as e:
        # Auto-rollback on any exception
        if savepoint:
            savepoint.rollback()
            logger.warning(
                f"Rolled back nested transaction (savepoint: {savepoint_name})",
                error=str(e)
            )
        else:
            session.rollback()
            logger.warning("Transaction rolled back", error=str(e))
        raise


@contextmanager
def transaction_with_retry(
    session: Session,
    max_retries: int = 3,
    savepoint_name: Optional[str] = None,
) -> Generator[Session, None, None]:
    """
    Context manager for transactions with automatic retry on deadlock/conflict.
    
    Usage:
        with transaction_with_retry(session, max_retries=3) as txn:
            # Operations that might deadlock
            update_inventory(txn)
            update_order(txn)
    
    Args:
        session: SQLAlchemy session
        max_retries: Number of retry attempts
        savepoint_name: Optional savepoint name
        
    Yields:
        The session
        
    Raises:
        Exception if retries exhausted
    """
    last_error = None
    
    for attempt in range(max_retries):
        try:
            with atomic_transaction(session, savepoint_name):
                yield session
            return  # Success
            
        except AppException as e:
            # Don't retry application errors
            raise
            
        except Exception as e:
            last_error = e
            # Check if it's a retryable error (deadlock, serialization conflict)
            error_str = str(e).lower()
            if any(msg in error_str for msg in ["deadlock", "serialization", "conflict"]):
                logger.warning(
                    f"Retryable error in transaction, attempt {attempt + 1}/{max_retries}",
                    error=str(e)
                )
                if attempt == max_retries - 1:
                    raise  # Last attempt failed
            else:
                raise  # Not retryable


def readonly_transaction(session: Session) -> Generator[Session, None, None]:
    """
    Context manager for read-only transactions.
    
    Sets the transaction to read-only mode for better query optimization.
    
    Usage:
        with readonly_transaction(session) as txn:
            product = txn.query(Product).filter(...).first()
    
    Args:
        session: SQLAlchemy session
        
    Yields:
        The read-only session
    """
    try:
        # PostgreSQL specific: set transaction to read-only
        session.execute(text("SET TRANSACTION READ ONLY"))
        logger.debug("Started read-only transaction")
        yield session
        session.commit()
        
    except Exception as e:
        session.rollback()
        logger.warning("Read-only transaction rolled back", error=str(e))
        raise


@contextmanager
def pessimistic_lock_transaction(
    session: Session,
    entity_type: type,
    entity_id: Any,
    savepoint_name: Optional[str] = None,
) -> Generator[Session, None, None]:
    """
    Context manager for pessimistic locking (row-level locks).
    
    Acquires a FOR UPDATE lock on an entity before operations,
    preventing concurrent modifications.
    
    Usage:
        with pessimistic_lock_transaction(session, Order, order_id) as txn:
            order = txn.query(Order).filter(Order.id == order_id).with_for_update().first()
            order.status = "shipped"
            # Lock held until transaction commits/rollbacks
    
    Args:
        session: SQLAlchemy session
        entity_type: SQLModel entity class
        entity_id: ID of entity to lock
        savepoint_name: Optional savepoint name
        
    Yields:
        The session with lock acquired
        
    Raises:
        Exception if entity not found or transaction fails
    """
    try:
        with atomic_transaction(session, savepoint_name):
            # Query with FOR UPDATE lock
            entity = session.query(entity_type).filter(
                entity_type.id == entity_id
            ).with_for_update().first()
            
            if not entity:
                logger.warning(f"{entity_type.__name__} not found for locking", id=entity_id)
                raise AppException(
                    code="E-VALIDATION-999",
                    message=f"{entity_type.__name__} not found",
                    status_code=404
                )
            
            logger.debug(f"Acquired pessimistic lock on {entity_type.__name__}({entity_id})")
            yield session
            
    except Exception as e:
        logger.warning(f"Pessimistic lock transaction failed", error=str(e))
        raise


def run_in_transaction(
    session: Session,
    func: Callable,
    *args,
    **kwargs
) -> Any:
    """
    Execute a function within an atomic transaction.
    
    Convenience wrapper for functions that need transaction management.
    
    Usage:
        result = run_in_transaction(
            session,
            create_order_with_payment,
            order_data,
            payment_data
        )
    
    Args:
        session: SQLAlchemy session
        func: Function to execute
        *args: Positional arguments for function
        **kwargs: Keyword arguments for function
        
    Returns:
        Result of function execution
        
    Raises:
        Exception will trigger rollback
    """
    with atomic_transaction(session):
        return func(session, *args, **kwargs)
