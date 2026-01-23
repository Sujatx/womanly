from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select, col, func
from pydantic import BaseModel
from app.db import get_session
from app.models import Product, Category

router = APIRouter()

class ProductList(BaseModel):
    items: List[Product]
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
    query = select(Product)
    
    if category:
        query = query.where(Product.category_slug == category)
    if q:
        query = query.where(col(Product.title).ilike(f"%{q}%"))
        
    # Count total matches
    # We need a separate query for count or use func.count()
    # Easiest is to execute count query
    count_query = select(func.count()).select_from(query.subquery())
    total = session.exec(count_query).one()

    # Pagination
    results = session.exec(query.offset(skip).limit(limit)).all()
    
    return ProductList(items=results, total=total, skip=skip, limit=limit)

@router.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/categories", response_model=List[Category])
def get_categories(session: Session = Depends(get_session)):
    return session.exec(select(Category)).all()
