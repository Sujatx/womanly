from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import Session, select, col, func, SQLModel
from sqlalchemy.orm import selectinload
from app.db import get_session
from app.models import Product, Category
from app.models.product import ProductVariant, ProductImage

router = APIRouter()

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
    is_available: bool

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

@router.get("/products", response_model=ProductList)
def get_products(
    session: Session = Depends(get_session),
    skip: int = Query(
        default=0,
        ge=MIN_SKIP,
        le=MAX_SKIP,
        description="Number of items to skip (pagination offset)"
    ),
    limit: int = Query(
        default=DEFAULT_LIMIT,
        ge=MIN_LIMIT,
        le=MAX_LIMIT,
        description=f"Number of items to return (max {MAX_LIMIT})"
    ),
    category: Optional[str] = None,
    q: Optional[str] = None
):
    # Validate pagination parameters
    if skip < MIN_SKIP or skip > MAX_SKIP:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"skip must be between {MIN_SKIP} and {MAX_SKIP}"
        )
    
    if limit < MIN_LIMIT or limit > MAX_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"limit must be between {MIN_LIMIT} and {MAX_LIMIT}"
        )
    
    query = select(Product).options(
        selectinload(Product.variants),
        selectinload(Product.product_images)
    ).where(Product.deleted_at.is_(None))  # Exclude soft-deleted products
    
    if category:
        query = query.where(Product.category_slug == category)
    if q:
        query = query.where(col(Product.title).ilike(f"%{q}%"))
        
    count_query = select(func.count()).select_from(query.subquery())
    total = session.exec(count_query).one()

    results = session.exec(query.offset(skip).limit(limit)).all()
    
    has_more = (skip + limit) < total
    
    return ProductList(
        data=results,
        pagination=PaginationMeta(
            total=total,
            skip=skip,
            limit=limit,
            has_more=has_more
        )
    )

@router.get("/products/{product_id}", response_model=ProductDetail)
def get_product(product_id: int, session: Session = Depends(get_session)):
    statement = select(Product).where(
        Product.id == product_id,
        Product.deleted_at.is_(None)  # Exclude soft-deleted products
    ).options(
        selectinload(Product.variants),
        selectinload(Product.product_images)
    )
    product = session.exec(statement).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/categories", response_model=List[Category])
def get_categories(session: Session = Depends(get_session)):
    return session.exec(select(Category)).all()