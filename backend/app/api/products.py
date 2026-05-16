from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import Session
from app.db import get_read_session
from app.models import Product, Category, ProductVariantRead, ProductDetail, PaginationMeta, ProductList
from app.models import SearchLog
from app.deps import get_current_user_optional
from app.core.logging import get_structured_logger
from app.services.cache_service import CacheService
from app.di_container import get as di_get
from app.repositories.base import PaginationParams
from pydantic import BaseModel, ConfigDict

router = APIRouter()
logger = get_structured_logger(__name__)

# Pagination constants
MIN_SKIP = 0
MAX_SKIP = 100000
MIN_LIMIT = 1
MAX_LIMIT = 500
DEFAULT_LIMIT = 20

def _enrich_variants(product: "Product") -> List[ProductVariantRead]:
    """Add estimated_total and available_stock to variant reads."""
    result = []
    for v in product.variants:
        result.append(ProductVariantRead(
            id=v.id,
            sku=v.sku,
            size=v.size,
            color=v.color,
            material=v.material,
            price_adjustment=v.price_adjustment,
            stock_quantity=v.stock_quantity,
            reserved_quantity=v.reserved_quantity,
            available_stock=v.available_stock,
            is_available=v.is_available,
            estimated_total=round(product.price + v.price_adjustment, 2),
        ))
    return result


def _build_product_detail(product: "Product") -> ProductDetail:
    return ProductDetail(
        id=product.id,
        title=product.title,
        description=product.description,
        price=product.price,
        brand=product.brand,
        thumbnail=product.thumbnail,
        category_slug=product.category_slug,
        variants=_enrich_variants(product),
        product_images=product.product_images,
    )


def _log_search(session: Session, query: str, results_count: int, user_id: Optional[int]):
    """Async-fire-and-forget: log a search query."""
    try:
        log = SearchLog(query=query, results_count=results_count, user_id=user_id)
        session.add(log)
        session.commit()
    except Exception:
        pass  # Never fail the request due to logging


@router.get("/", response_model=ProductList)
async def get_products(
    session: Session = Depends(get_read_session),
    skip: int = Query(default=0, ge=MIN_SKIP, le=MAX_SKIP),
    limit: int = Query(default=DEFAULT_LIMIT, ge=MIN_LIMIT, le=MAX_LIMIT),
    category: Optional[str] = None,
    q: Optional[str] = None,
    min_price: Optional[float] = Query(default=None, ge=0),
    max_price: Optional[float] = Query(default=None, ge=0),
    in_stock: Optional[bool] = None,
    current_user=Depends(get_current_user_optional),
):
    # PHASE 4: Check cache for unfiltered queries (improves response time for common cases)
    has_filters = bool(category or q or min_price is not None or max_price is not None or in_stock is not None)
    if not has_filters:
        cached_data = await CacheService.get_cached_products(skip, limit)
        if cached_data:
            logger.info(f"✓ Cache HIT: products (skip={skip}, limit={limit})")
            data = cached_data.get("data", [])
            total = cached_data.get("total", len(data))
            has_more = (skip + limit) < total
            return ProductList(
                data=[ProductDetail(**item) for item in data],
                pagination=PaginationMeta(total=total, skip=skip, limit=limit, has_more=has_more)
            )

    # Cache miss or filtered query: fetch from database via repository
    product_repo = di_get("product_repo")
    if not has_filters:
        results, total = product_repo.get_active_products(
            session=session,
            pagination=PaginationParams(offset=skip, page_size=limit),
        )
    else:
        results, total = product_repo.list_products(
            session=session,
            skip=skip,
            limit=limit,
            category=category,
            q=q,
            min_price=min_price,
            max_price=max_price,
            in_stock=in_stock,
        )

    # Log search if query was provided
    if q:
        user_id = current_user.id if current_user else None
        _log_search(session, q, total, user_id)

    # PHASE 4: Cache results only for unfiltered queries
    if not has_filters and len(results) > 0:
        cache_data = [_build_product_detail(p).dict() for p in results]
        await CacheService.set_cached_products(skip, limit, cache_data, total)
        logger.info(f"✓ Cached products (skip={skip}, limit={limit})")

    has_more = (skip + limit) < total

    return ProductList(
        data=[_build_product_detail(p) for p in results],
        pagination=PaginationMeta(total=total, skip=skip, limit=limit, has_more=has_more)
    )


class ProductUpdateItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int
    title: Optional[str] = None
    price: Optional[float] = None
    thumbnail: Optional[str] = None


@router.post("/batch-update", status_code=status.HTTP_200_OK)
def batch_update_products(
    items: List[ProductUpdateItem],
    session: Session = Depends(get_read_session),
):
    """Batch update multiple products using the ProductRepository.

    Each item must include `id`. Allowed fields: `title`, `price`, `thumbnail`, etc.
    The repository's `update_many` will be used inside a transaction.
    """
    product_repo = di_get("product_repo")
    payloads = [item.model_dump() for item in items]
    try:
        with session.begin():
            updated = product_repo.update_many(session, payloads)
            # Commit happens on context exit
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch update failed: {str(e)}")

    return {"updated_count": len(updated)}


@router.get("/search", response_model=ProductList)
def search_products(
    q: str = Query(min_length=1, description="Search query"),
    category: Optional[str] = None,
    min_price: Optional[float] = Query(default=None, ge=0),
    max_price: Optional[float] = Query(default=None, ge=0),
    in_stock: Optional[bool] = None,
    skip: int = Query(default=0, ge=MIN_SKIP, le=MAX_SKIP),
    limit: int = Query(default=DEFAULT_LIMIT, ge=MIN_LIMIT, le=MAX_LIMIT),
    session: Session = Depends(get_read_session),
    current_user=Depends(get_current_user_optional),
):
    """
    Full-text product search with filters.
    Searches title AND description for relevance.
    """
    product_repo = di_get("product_repo")
    results, total = product_repo.search_products(
        session=session,
        query_text=q,
        skip=skip,
        limit=limit,
        category=category,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
    )

    user_id = current_user.id if current_user else None
    _log_search(session, q, total, user_id)

    has_more = (skip + limit) < total
    return ProductList(
        data=[_build_product_detail(p) for p in results],
        pagination=PaginationMeta(total=total, skip=skip, limit=limit, has_more=has_more)
    )


@router.get("/{product_id}", response_model=ProductDetail)
def get_product(product_id: int, session: Session = Depends(get_read_session)):
    product_repo = di_get("product_repo")
    product = product_repo.get_by_id(session, product_id)
    if not product or getattr(product, "deleted_at", None) is not None:
        raise HTTPException(status_code=404, detail="Product not found")
    # ensure related attrs are available
    _ = getattr(product, "variants", None)
    _ = getattr(product, "product_images", None)
    return _build_product_detail(product)


@router.get("/{product_id}/available-variants", response_model=List[ProductVariantRead])
def get_available_variants(product_id: int, session: Session = Depends(get_read_session)):
    """Return only available (in-stock, is_available=True) variants for a product."""
    product_repo = di_get("product_repo")
    product = product_repo.get_by_id(session, product_id)
    if not product or getattr(product, "deleted_at", None) is not None:
        raise HTTPException(status_code=404, detail="Product not found")

    available = [v for v in getattr(product, "variants", []) if v.is_available and v.available_stock > 0]
    return [
        ProductVariantRead(
            id=v.id, sku=v.sku, size=v.size, color=v.color, material=v.material,
            price_adjustment=v.price_adjustment, stock_quantity=v.stock_quantity,
            reserved_quantity=v.reserved_quantity, available_stock=v.available_stock,
            is_available=v.is_available,
            estimated_total=round(product.price + v.price_adjustment, 2),
        )
        for v in available
    ]


@router.get("/categories", response_model=List[Category])
async def get_categories(session: Session = Depends(get_read_session)):
    cached_categories = await CacheService.get_cached_categories()
    if cached_categories:
        logger.info("✓ Cache HIT: categories")
        return [Category(**item) for item in cached_categories]

    category_repo = di_get("category_repo")
    categories = category_repo.list_all(session)
    if categories:
        await CacheService.set_cached_categories([category.model_dump() for category in categories])
        logger.info("✓ Cached categories")
    return categories