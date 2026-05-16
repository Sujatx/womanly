"""
Wishlist endpoints: GET, POST, DELETE.
The Wishlist and WishlistItem models already exist; this adds the API layer.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from app.db import get_session
from app.deps import get_current_user
from app.models import User, Wishlist, WishlistItem, Product, WishlistItemRead, WishlistAddRequest, WishlistRead
from app.core.logging import get_structured_logger
from app.di_container import get as di_get

router = APIRouter()
logger = get_structured_logger(__name__)


# ─────────────────────────── Helpers ───────────────────────────

def _get_or_create_wishlist(session: Session, user_id: int) -> Wishlist:
    return di_get("wishlist_repo").get_or_create(session, user_id)


def _enrich_items(session: Session, items: List[WishlistItem]) -> List[WishlistItemRead]:
    """Attach product title/thumbnail/price from the Product table."""
    product_ids = [i.product_id for i in items]
    if not product_ids:
        return []
    product_repo = di_get("product_repo")
    products = []
    for pid in product_ids:
        p = product_repo.get_by_id(session, pid)
        if p and getattr(p, "deleted_at", None) is None:
            products.append(p)
    product_map = {p.id: p for p in products}
    result = []
    for item in items:
        p = product_map.get(item.product_id)
        result.append(WishlistItemRead(
            id=item.id,
            product_id=item.product_id,
            title=p.title if p else None,
            thumbnail=p.thumbnail if p else None,
            price=p.price if p else None,
        ))
    return result


# ─────────────────────────── Endpoints ───────────────────────────

@router.get("/", response_model=WishlistRead)
def get_wishlist(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Return the current user's wishlist with product details."""
    wishlist = _get_or_create_wishlist(session, current_user.id)
    enriched = _enrich_items(session, wishlist.items)
    return WishlistRead(id=wishlist.id, items=enriched, count=len(enriched))


@router.post("/", response_model=WishlistRead, status_code=status.HTTP_201_CREATED)
def add_to_wishlist(
    body: WishlistAddRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Add a product to the wishlist. Idempotent — adding an already-wishlisted product returns 200."""
    # Verify product exists
    product = di_get("product_repo").get_by_id(session, body.product_id)
    if not product or getattr(product, "deleted_at", None) is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    wishlist = _get_or_create_wishlist(session, current_user.id)

    # Check if already in wishlist
    already_exists = any(i.product_id == body.product_id for i in wishlist.items)
    if not already_exists:
        di_get("wishlist_repo").add_item(session, wishlist.id, body.product_id)
        session.commit()
        # Re-fetch
        wishlist = _get_or_create_wishlist(session, current_user.id)

    enriched = _enrich_items(session, wishlist.items)
    logger.info("Product added to wishlist", user_id=current_user.id, product_id=body.product_id)
    return WishlistRead(id=wishlist.id, items=enriched, count=len(enriched))


@router.delete("/{product_id}", response_model=WishlistRead)
def remove_from_wishlist(
    product_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Remove a product from the wishlist."""
    wishlist = _get_or_create_wishlist(session, current_user.id)

    item = next((i for i in wishlist.items if i.product_id == product_id), None)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not in wishlist")

    di_get("wishlist_repo").remove_item(session, wishlist.id, product_id)
    session.commit()

    # Re-fetch updated wishlist
    wishlist = _get_or_create_wishlist(session, current_user.id)
    enriched = _enrich_items(session, wishlist.items)
    logger.info("Product removed from wishlist", user_id=current_user.id, product_id=product_id)
    return WishlistRead(id=wishlist.id, items=enriched, count=len(enriched))
