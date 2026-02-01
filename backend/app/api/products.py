from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select, col, func, SQLModel
from sqlalchemy.orm import selectinload
from app.db import get_session
from app.models import Product, Category
from app.models.product import ProductVariant, ProductImage

router = APIRouter()

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

class ProductList(SQLModel):
    items: List[ProductDetail]
    total: int
    skip: int
    limit: int

@router.get("/products", response_model=ProductList)
def get_products(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 24,
    category: Optional[str] = None,
    q: Optional[str] = None
):
    query = select(Product).options(
        selectinload(Product.variants),
        selectinload(Product.product_images)
    )
    
    if category:
        query = query.where(Product.category_slug == category)
    if q:
        query = query.where(col(Product.title).ilike(f"%{q}%"))
        
    count_query = select(func.count()).select_from(query.subquery())
    total = session.exec(count_query).one()

    results = session.exec(query.offset(skip).limit(limit)).all()
    
    return ProductList(items=results, total=total, skip=skip, limit=limit)

@router.get("/products/{product_id}", response_model=ProductDetail)
def get_product(product_id: int, session: Session = Depends(get_session)):
    statement = select(Product).where(Product.id == product_id).options(
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