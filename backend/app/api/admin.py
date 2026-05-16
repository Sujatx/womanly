"""
Admin API endpoints for managing soft deletes and GDPR compliance.

These endpoints should only be accessible to admin users.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, or_
from typing import List, Literal
from datetime import datetime

from app.db import get_session
from app.models.user import User
from app.models.order import Order
from app.models.product import Product
from app.core import (
    soft_delete_record,
    restore_record,
    hard_delete_record,
    only_deleted,
)
from app.core.exceptions import ForbiddenException
from app.core.logging import StructuredLogger
from app.di_container import get as di_get
from app.deps import get_current_user

logger = StructuredLogger(__name__)
router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

# Type alias for entity types
EntityType = Literal["user", "order", "product"]


def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Verify the current user is an admin.
    """
    if not current_user.is_superuser:
        raise ForbiddenException("Admin privileges are required")
    return current_user


def get_entity_model(entity_type: EntityType):
    """Get the SQLModel class for a given entity type."""
    models = {
        "user": User,
        "order": Order,
        "product": Product,
    }
    return models[entity_type]


@router.post("/soft-delete/{entity_type}/{entity_id}")
async def soft_delete_entity(
    entity_type: EntityType,
    entity_id: int,
    session: Session = Depends(get_session),
    admin: User = Depends(get_current_admin_user),
):
    """
    Soft delete an entity by marking it as deleted.
    
    This operation is reversible with the restore endpoint.
    """
    model = get_entity_model(entity_type)
    
    try:
        entity = soft_delete_record(session, model, entity_id)
        logger.info(
            f"Admin {admin.email} soft deleted {entity_type}",
            extra={"entity_type": entity_type, "entity_id": entity_id, "admin_email": admin.email}
        )
        return {
            "message": f"{entity_type.capitalize()} soft deleted successfully",
            "entity_id": entity_id,
            "deleted_at": entity.deleted_at.isoformat() if entity.deleted_at else None,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/restore/{entity_type}/{entity_id}")
async def restore_entity(
    entity_type: EntityType,
    entity_id: int,
    session: Session = Depends(get_session),
    admin: User = Depends(get_current_admin_user),
):
    """
    Restore a soft-deleted entity.
    
    This makes the entity active again by removing the deleted_at timestamp.
    """
    model = get_entity_model(entity_type)
    
    try:
        entity = restore_record(session, model, entity_id)
        logger.info(
            f"Admin {admin.email} restored {entity_type}",
            extra={"entity_type": entity_type, "entity_id": entity_id, "admin_email": admin.email}
        )
        return {
            "message": f"{entity_type.capitalize()} restored successfully",
            "entity_id": entity_id,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/hard-delete/{entity_type}/{entity_id}")
async def hard_delete_entity(
    entity_type: EntityType,
    entity_id: int,
    confirm: bool = Query(False, description="Must be true to confirm permanent deletion"),
    session: Session = Depends(get_session),
    admin: User = Depends(get_current_admin_user),
):
    """
    Permanently delete an entity from the database.
    
    ⚠️ WARNING: This operation is IRREVERSIBLE!
    
    This should only be used for:
    - GDPR "right to be forgotten" requests
    - Test data cleanup
    - Compliance with data retention policies
    
    Requires explicit confirmation via the confirm query parameter.
    """
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Hard delete requires explicit confirmation. Set confirm=true query parameter."
        )
    
    model = get_entity_model(entity_type)
    
    try:
        hard_delete_record(session, model, entity_id)
        logger.warning(
            f"Admin {admin.email} PERMANENTLY deleted {entity_type}",
            extra={"entity_type": entity_type, "entity_id": entity_id, "admin_email": admin.email}
        )
        return {
            "message": f"{entity_type.capitalize()} permanently deleted",
            "entity_id": entity_id,
            "warning": "This operation is irreversible",
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/deleted/{entity_type}")
async def list_deleted_entities(
    entity_type: EntityType,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
    admin: User = Depends(get_current_admin_user),
):
    """
    List all soft-deleted entities of a given type.
    
    Useful for auditing and recovery operations.
    """
    repo = di_get(f"{entity_type}_repo")
    entities = repo.list_deleted(session, skip=skip, limit=limit)
    
    return {
        "entity_type": entity_type,
        "count": len(entities),
        "items": [
            {
                "id": entity.id,
                "deleted_at": entity.deleted_at.isoformat() if entity.deleted_at else None,
                # Add basic info based on entity type
                **({"email": entity.email} if entity_type == "user" else {}),
                **({"status": entity.status} if entity_type == "order" else {}),
                **({"name": entity.name} if entity_type == "product" else {}),
            }
            for entity in entities
        ],
    }


@router.get("/audit/deletion-stats")
async def get_deletion_stats(
    session: Session = Depends(get_session),
    admin: User = Depends(get_current_admin_user),
):
    """
    Get statistics on soft-deleted entities.
    
    Useful for monitoring and compliance reporting.
    """
    stats = {}
    
    for entity_type in ["user", "order", "product"]:
        repo_name = f"{entity_type}_repo"
        repo = di_get(repo_name)
        active_count = repo.count_active(session) if repo else 0
        deleted_count = repo.count_deleted(session) if repo else 0
        stats[entity_type] = {
            "active": active_count,
            "soft_deleted": deleted_count,
            "total": active_count + deleted_count,
        }
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "stats": stats,
    }
