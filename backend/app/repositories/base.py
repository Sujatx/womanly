"""
Base repository pattern for data access.

Provides common CRUD operations, filtering, sorting, and pagination
for all entity repositories. Implements repository pattern to abstract
database access logic.
"""

from typing import Generic, TypeVar, List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, and_
from sqlmodel import select, SQLModel
from app.core.logging import get_structured_logger
from app.core.exceptions import AppException

logger = get_structured_logger(__name__)

T = TypeVar("T", bound=SQLModel)


class PaginationParams:
    """Pagination parameters."""
    
    def __init__(self, page: int = 1, page_size: int = 20):
        self.page = max(1, page)
        self.page_size = min(page_size, 100)  # Cap at 100 items per page
        self.offset = (self.page - 1) * self.page_size
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "page": self.page,
            "page_size": self.page_size,
            "offset": self.offset,
        }


class SortParams:
    """Sort parameters."""
    
    def __init__(self, sort_by: str = "id", sort_order: str = "asc"):
        self.sort_by = sort_by
        self.sort_order = sort_order.lower()
        if self.sort_order not in ("asc", "desc"):
            self.sort_order = "asc"


class BaseRepository(Generic[T]):
    """
    Base repository class providing common CRUD and query operations.
    
    Inherit from this class to create entity-specific repositories:
    
        class ProductRepository(BaseRepository[Product]):
            def get_by_sku(self, session: Session, sku: str) -> Optional[Product]:
                return session.exec(
                    select(Product).where(Product.sku == sku)
                ).first()
    """
    
    def __init__(self, entity_type: type[T]):
        self.entity_type = entity_type
    
    # ==================== Create ====================
    
    def create(self, session: Session, obj: T) -> T:
        """Create a new entity."""
        session.add(obj)
        session.flush()  # Flush to get ID
        logger.debug(f"Created {self.entity_type.__name__}", id=obj.id)
        return obj
    
    def create_many(self, session: Session, objects: List[T]) -> List[T]:
        """Create multiple entities."""
        session.add_all(objects)
        session.flush()
        logger.debug(f"Created {len(objects)} {self.entity_type.__name__} records")
        return objects
    
    # ==================== Read ====================
    
    def get_by_id(self, session: Session, entity_id: Any) -> Optional[T]:
        """Get entity by ID."""
        return session.exec(
            select(self.entity_type).where(self.entity_type.id == entity_id)
        ).first()
    
    def get_by_id_or_raise(self, session: Session, entity_id: Any) -> T:
        """Get entity by ID or raise exception."""
        entity = self.get_by_id(session, entity_id)
        if not entity:
            logger.warning(f"{self.entity_type.__name__} not found", id=entity_id)
            raise AppException(
                code="E-VALIDATION-999",
                message=f"{self.entity_type.__name__} not found",
                status_code=404,
            )
        return entity
    
    def get_all(
        self,
        session: Session,
        pagination: Optional[PaginationParams] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[T], int]:
        """
        Get all entities with optional filtering and pagination.
        
        Returns:
            Tuple of (entities, total_count)
        """
        query = select(self.entity_type)
        
        # Apply filters
        if filters:
            conditions = []
            for key, value in filters.items():
                if hasattr(self.entity_type, key):
                    conditions.append(getattr(self.entity_type, key) == value)
            if conditions:
                query = query.where(and_(*conditions))
        
        # Get total count
        total = session.exec(select(self.entity_type)).all()
        total_count = len(total)
        
        # Apply pagination
        if pagination:
            query = query.offset(pagination.offset).limit(pagination.page_size)
        
        entities = session.exec(query).all()
        return entities, total_count
    
    def find(
        self,
        session: Session,
        filters: Dict[str, Any],
        sort: Optional[SortParams] = None,
        pagination: Optional[PaginationParams] = None,
    ) -> Tuple[List[T], int]:
        """
        Find entities with filtering, sorting, and pagination.
        
        Args:
            session: Database session
            filters: Filter criteria (column_name -> value)
            sort: Sort parameters
            pagination: Pagination parameters
            
        Returns:
            Tuple of (entities, total_count)
        """
        query = select(self.entity_type)
        
        # Apply filters
        conditions = []
        for key, value in filters.items():
            if hasattr(self.entity_type, key):
                conditions.append(getattr(self.entity_type, key) == value)
        if conditions:
            query = query.where(and_(*conditions))
        
        # Count total before pagination
        total_query = select(self.entity_type)
        if conditions:
            total_query = total_query.where(and_(*conditions))
        total_count = len(session.exec(total_query).all())
        
        # Apply sorting
        if sort and hasattr(self.entity_type, sort.sort_by):
            sort_column = getattr(self.entity_type, sort.sort_by)
            if sort.sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        
        # Apply pagination
        if pagination:
            query = query.offset(pagination.offset).limit(pagination.page_size)
        
        entities = session.exec(query).all()
        return entities, total_count
    
    # ==================== Update ====================
    
    def update(self, session: Session, entity_id: Any, data: Dict[str, Any]) -> T:
        """Update an entity."""
        entity = self.get_by_id_or_raise(session, entity_id)
        for key, value in data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        session.flush()
        logger.debug(f"Updated {self.entity_type.__name__}", id=entity_id)
        return entity
    
    def update_many(self, session: Session, entities_data: List[Dict[str, Any]]) -> List[T]:
        """Update multiple entities."""
        updated = []
        for data in entities_data:
            entity_id = data.pop("id")
            entity = self.update(session, entity_id, data)
            updated.append(entity)
        session.flush()
        return updated
    
    # ==================== Delete ====================
    
    def delete(self, session: Session, entity_id: Any) -> None:
        """Hard delete an entity."""
        entity = self.get_by_id_or_raise(session, entity_id)
        session.delete(entity)
        session.flush()
        logger.debug(f"Deleted {self.entity_type.__name__}", id=entity_id)
    
    def delete_many(self, session: Session, entity_ids: List[Any]) -> int:
        """Hard delete multiple entities."""
        count = 0
        for entity_id in entity_ids:
            try:
                self.delete(session, entity_id)
                count += 1
            except Exception as e:
                logger.warning(f"Failed to delete entity", id=entity_id, error=str(e))
        session.flush()
        logger.debug(f"Deleted {count} {self.entity_type.__name__} records")
        return count
    
    # ==================== Soft Delete ====================
    
    def soft_delete(self, session: Session, entity_id: Any) -> T:
        """Soft delete an entity (mark as deleted)."""
        entity = self.get_by_id_or_raise(session, entity_id)
        if hasattr(entity, "deleted_at"):
            from datetime import datetime
            entity.deleted_at = datetime.utcnow()
            session.flush()
            logger.debug(f"Soft deleted {self.entity_type.__name__}", id=entity_id)
            return entity
        else:
            # Fall back to hard delete if soft delete not supported
            self.delete(session, entity_id)
            return entity
    
    def restore(self, session: Session, entity_id: Any) -> T:
        """Restore a soft-deleted entity."""
        # Need to query including soft-deleted records
        query = select(self.entity_type).where(self.entity_type.id == entity_id)
        entity = session.exec(query).first()
        
        if not entity:
            raise AppException(
                code="E-VALIDATION-999",
                message=f"{self.entity_type.__name__} not found",
                status_code=404,
            )
        
        if hasattr(entity, "deleted_at"):
            entity.deleted_at = None
            session.flush()
            logger.debug(f"Restored {self.entity_type.__name__}", id=entity_id)
        
        return entity
    
    # ==================== Utility ====================
    
    def exists(self, session: Session, entity_id: Any) -> bool:
        """Check if entity exists."""
        return self.get_by_id(session, entity_id) is not None
    
    def count(self, session: Session, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities with optional filters."""
        query = select(self.entity_type)
        if filters:
            conditions = []
            for key, value in filters.items():
                if hasattr(self.entity_type, key):
                    conditions.append(getattr(self.entity_type, key) == value)
            if conditions:
                query = query.where(and_(*conditions))
        
        return len(session.exec(query).all())

    def count_active(self, session: Session) -> int:
        """Count non-deleted entities (where deleted_at is NULL)."""
        if hasattr(self.entity_type, "deleted_at"):
            query = select(self.entity_type).where(self.entity_type.deleted_at.is_(None))
        else:
            query = select(self.entity_type)
        return len(session.exec(query).all())

    def count_deleted(self, session: Session) -> int:
        """Count soft-deleted entities (where deleted_at is NOT NULL)."""
        if hasattr(self.entity_type, "deleted_at"):
            query = select(self.entity_type).where(self.entity_type.deleted_at.isnot(None))
            return len(session.exec(query).all())
        return 0

    def list_deleted(self, session: Session, skip: int = 0, limit: int = 20):
        """Return soft-deleted entities with pagination."""
        if hasattr(self.entity_type, "deleted_at"):
            query = select(self.entity_type).where(self.entity_type.deleted_at.isnot(None)).offset(skip).limit(limit)
            return session.exec(query).all()
        return []
