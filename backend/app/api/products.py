from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import Session, select, col, func, SQLModel
from sqlalchemy.orm import selectinload
from app.db import get_session
from app.models import Product, Category
from app.models.product import ProductVariant, ProductImage
from app.models.search import SearchLog
from app.deps import get_current_user_optional
from app.core.logging import get_structured_logger

router = APIRouter()
logger = get_structured_logger(__name__)

# Pagination constants
MIN_SKIP = 0
MAX_SKIP = 100000
MIN_LIMIT = 1
MAX_LIMIT = 500
DEFAULT_LIMIT = 20

# Schema for detail view including variants and images
class ProductVariantRead(SQLModel):
    id: int
    sku: str
    size: Optional[str]
    color: Optional[str]
    material: Optional[str]
    price_adjustment: float
    stock_quantity: int
    reserved_quantity: int
    available_stock: int
    is_available: bool
    estimated_total: Optional[float] = None  # Populated by the endpoint when base_price is known

class ProductImageRead(SQLModel):
    id: int
    image_url: str
    alt_text: Optional[str]
    display_order: int
    is_primary: bool

class ProductDetail(SQLModel):
    id: int
    title: str
    description: str
    price: float
    brand: Optional[str]
    thumbnail: Optional[str]
    category_slug: str
    variants: List[ProductVariantRead]
    product_images: List[ProductImageRead]

class PaginationMeta(SQLModel):
    """Pagination metadata."""
    total: int
    skip: int
    limit: int
    has_more: bool

class ProductList(SQLModel):
    data: List[ProductDetail]
    pagination: PaginationMeta


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
def get_products(
    session: Session = Depends(get_session),
    skip: int = Query(default=0, ge=MIN_SKIP, le=MAX_SKIP),
    limit: int = Query(default=DEFAULT_LIMIT, ge=MIN_LIMIT, le=MAX_LIMIT),
    category: Optional[str] = None,
    q: Optional[str] = None,
    min_price: Optional[float] = Query(default=None, ge=0),
    max_price: Optional[float] = Query(default=None, ge=0),
    in_stock: Optional[bool] = None,
    current_user=Depends(get_current_user_optional),
):
    query = select(Product).options(
        selectinload(Product.variants),
        selectinload(Product.product_images)
    ).where(Product.deleted_at.is_(None))

    if category:
        query = query.where(Product.category_slug == category)
    if q:
        query = query.where(col(Product.title).ilike(f"%{q}%"))
    if min_price is not None:
        query = query.where(Product.price >= min_price)
    if max_price is not None:
        query = query.where(Product.price <= max_price)

    count_query = select(func.count()).select_from(query.subquery())
    total = session.exec(count_query).one()

    results = session.exec(query.offset(skip).limit(limit)).all()

    # Apply in_stock filter after fetch (requires variant data)
    if in_stock is not None:
        if in_stock:
            results = [p for p in results if any(v.available_stock > 0 and v.is_available for v in p.variants)]
        else:
            results = [p for p in results if all(v.available_stock == 0 or not v.is_available for v in p.variants)]
        total = len(results)

    # Log search if query was provided
    if q:
        user_id = current_user.id if current_user else None
        _log_search(session, q, total, user_id)

    has_more = (skip + limit) < total

    return ProductList(
        data=[_build_product_detail(p) for p in results],
        pagination=PaginationMeta(total=total, skip=skip, limit=limit, has_more=has_more)
    )


@router.get("/search", response_model=ProductList)
def search_products(
    q: str = Query(min_length=1, description="Search query"),
    category: Optional[str] = None,
    min_price: Optional[float] = Query(default=None, ge=0),
    max_price: Optional[float] = Query(default=None, ge=0),
    in_stock: Optional[bool] = None,
    skip: int = Query(default=0, ge=MIN_SKIP, le=MAX_SKIP),
    limit: int = Query(default=DEFAULT_LIMIT, ge=MIN_LIMIT, le=MAX_LIMIT),
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user_optional),
):
    """
    Full-text product search with filters.
    Searches title AND description for relevance.
    """
    base_query = select(Product).options(
        selectinload(Product.variants),
        selectinload(Product.product_images)
    ).where(
        Product.deleted_at.is_(None),
        col(Product.title).ilike(f"%{q}%") |
        col(Product.description).ilike(f"%{q}%")
    )

    if category:
        base_query = base_query.where(Product.category_slug == category)
    if min_price is not None:
        base_query = base_query.where(Product.price >= min_price)
    if max_price is not None:
        base_query = base_query.where(Product.price <= max_price)

    total_raw = session.exec(select(func.count()).select_from(base_query.subquery())).one()
    results = session.exec(base_query.offset(skip).limit(limit)).all()

    if in_stock is not None:
        if in_stock:
            results = [p for p in results if any(v.available_stock > 0 and v.is_available for v in p.variants)]
        else:
            results = [p for p in results if all(v.available_stock == 0 or not v.is_available for v in p.variants)]

    total = len(results) if in_stock is not None else total_raw

    user_id = current_user.id if current_user else None
    _log_search(session, q, total, user_id)

    has_more = (skip + limit) < total
    return ProductList(
        data=[_build_product_detail(p) for p in results],
        pagination=PaginationMeta(total=total, skip=skip, limit=limit, has_more=has_more)
    )


@router.get("/{product_id}", response_model=ProductDetail)
def get_product(product_id: int, session: Session = Depends(get_session)):
    statement = select(Product).where(
        Product.id == product_id,
        Product.deleted_at.is_(None)
    ).options(
        selectinload(Product.variants),
        selectinload(Product.product_images)
    )
    product = session.exec(statement).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return _build_product_detail(product)


@router.get("/{product_id}/available-variants", response_model=List[ProductVariantRead])
def get_available_variants(product_id: int, session: Session = Depends(get_session)):
    """Return only available (in-stock, is_available=True) variants for a product."""
    product = session.exec(
        select(Product).where(
            Product.id == product_id,
            Product.deleted_at.is_(None)
        ).options(selectinload(Product.variants))
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    available = [v for v in product.variants if v.is_available and v.available_stock > 0]
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
def get_categories(session: Session = Depends(get_session)):
    return session.exec(select(Category)).all()