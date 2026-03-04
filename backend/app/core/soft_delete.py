"""
Soft Delete Utilities

Provides helper functions for working with soft-deleted records.
"""

from typing import Optional, Type, TypeVar
from datetime import datetime
from sqlmodel import SQLModel, select, Session
from sqlalchemy import Select

T = TypeVar('T', bound=SQLModel)


def exclude_deleted(query: Select, model: Type[T]) -> Select:
    """
    Add filter to exclude soft-deleted records.
    
    Args:
        query: SQLModel select query
        model: Model class to filter
        
    Returns:
        Modified query with deleted_at IS NULL filter
    """
    if hasattr(model, 'deleted_at'):
        return query.where(model.deleted_at.is_(None))
    return query


def only_deleted(query: Select, model: Type[T]) -> Select:
    """
    Add filter to only include soft-deleted records.
    
    Args:
        query: SQLModel select query
        model: Model class to filter
        
    Returns:
        Modified query with deleted_at IS NOT NULL filter
    """
    if hasattr(model, 'deleted_at'):
        return query.where(model.deleted_at.isnot(None))
    return query


def get_active_record(session: Session, model: Type[T], record_id: int) -> Optional[T]:
    """
    Get a non-deleted record by ID.
    
    Args:
        session: Database session
        model: Model class
        record_id: Record ID
        
    Returns:
        Record if found and not deleted, None otherwise
    """
    query = select(model).where(model.id == record_id)
    query = exclude_deleted(query, model)
    return session.exec(query).first()


def soft_delete_record(session: Session, record: SQLModel) -> None:
    """
    Soft delete a record.
    
    Args:
        session: Database session
        record: Record to soft delete
    """
    if hasattr(record, 'soft_delete'):
        record.soft_delete()
        session.add(record)
        session.commit()
    else:
        raise ValueError(f"{type(record).__name__} does not support soft delete")


def restore_record(session: Session, record: SQLModel) -> None:
    """
    Restore a soft-deleted record.
    
    Args:
        session: Database session
        record: Record to restore
    """
    if hasattr(record, 'deleted_at'):
        record.deleted_at = None
        if hasattr(record, 'is_active'):
            record.is_active = True
        session.add(record)
        session.commit()
    else:
        raise ValueError(f"{type(record).__name__} does not support soft delete")


def hard_delete_record(session: Session, record: SQLModel) -> None:
    """
    Permanently delete a record (for GDPR compliance).
    
    ⚠️ WARNING: This permanently removes data from the database.
    Only use this for compliance reasons (e.g., GDPR right to be forgotten).
    
    Args:
        session: Database session
        record: Record to permanently delete
    """
    session.delete(record)
    session.commit()
