"""Product repository for data access operations."""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlmodel import select
from app.models import Product
from app.repositories.base import BaseRepository, PaginationParams, SortParams
from app.core.logging import get_structured_logger

logger = get_structured_logger(__name__)


class ProductRepository(BaseRepository[Product]):
    """Repository for Product entity operations."""
    
    def __init__(self):
        super().__init__(Product)
    
    def get_by_sku(self, session: Session, sku: str) -> Optional[Product]:
        """Get product by SKU (product code)."""
        return session.exec(
            select(Product).where(Product.sku == sku)
        ).first()
    
    def get_by_category(
        self,
        session: Session,
        category_id: int,
        pagination: Optional[PaginationParams] = None,
        sort: Optional[SortParams] = None,
    ) -> Tuple[List[Product], int]:
        """Get products by category with pagination."""
        return self.find(
            session,
            filters={"category_id": category_id, "is_active": True},
            sort=sort or SortParams("created_at", "desc"),
            pagination=pagination,
        )
    
    def search(
        self,
        session: Session,
        query: str,
        pagination: Optional[PaginationParams] = None,
        include_variants: bool = True,
        include_images: bool = True,
    ) -> Tuple[List[Product], int]:
        """Search products by name or description."""
        from sqlalchemy.orm import selectinload

        search_query = select(Product).where(
            (Product.name.ilike(f"%{query}%")) |
            (Product.description.ilike(f"%{query}%"))
        ).where(Product.is_active == True)

        if include_variants:
            search_query = search_query.options(selectinload(Product.variants))
        if include_images:
            search_query = search_query.options(selectinload(Product.product_images))

        total_count = len(session.exec(search_query).all())

        if pagination:
            search_query = search_query.offset(pagination.offset).limit(pagination.page_size)

        products = session.exec(search_query).all()
        return products, total_count
    
    def get_featured_products(
        self,
        session: Session,
        limit: int = 10,
    ) -> List[Product]:
        """Get featured products."""
        return session.exec(
            select(Product)
            .where(Product.is_featured == True)
            .where(Product.is_active == True)
            .limit(limit)
        ).all()

    def get_many_by_ids(
        self,
        session: Session,
        ids: List[int],
        include_variants: bool = True,
        include_images: bool = True,
    ) -> List[Product]:
        """Fetch multiple products by IDs with optional eager loads."""
        from sqlalchemy.orm import selectinload

        query = select(Product).where(Product.id.in_(ids), Product.deleted_at.is_(None))
        if include_variants:
            query = query.options(selectinload(Product.variants))
        if include_images:
            query = query.options(selectinload(Product.product_images))

        return session.exec(query).all()

    def get_variant_for_update(self, session: Session, variant_id: int):
        """Fetch a ProductVariant by id with FOR UPDATE lock and product eagerly loaded."""
        from app.models.product import ProductVariant
        from sqlalchemy.orm import selectinload

        stmt = (
            select(ProductVariant)
            .where(ProductVariant.id == variant_id)
            .options(selectinload(ProductVariant.product))
            .with_for_update()
        )
        return session.exec(stmt).first()

    def get_first_variant_for_product(self, session: Session, product_id: int):
        """Return the first variant for a product (ordered by id)."""
        from app.models.product import ProductVariant

        stmt = select(ProductVariant).where(ProductVariant.product_id == product_id).order_by(ProductVariant.id).limit(1)
        return session.exec(stmt).first()

    def list_products(
        self,
        session: Session,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        q: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock: Optional[bool] = None,
    ) -> Tuple[List[Product], int]:
        """List products with filters and eager-loaded relationships."""
        from sqlalchemy.orm import selectinload

        query = select(Product).options(
            selectinload(Product.variants),
            selectinload(Product.product_images),
        ).where(Product.deleted_at.is_(None))

        if category:
            query = query.where(Product.category_slug == category)
        if q:
            query = query.where((Product.title.ilike(f"%{q}%")) | (Product.description.ilike(f"%{q}%")))
        if min_price is not None:
            query = query.where(Product.price >= min_price)
        if max_price is not None:
            query = query.where(Product.price <= max_price)

        total_count = len(session.exec(query).all())
        results = session.exec(query.offset(skip).limit(limit)).all()

        if in_stock is not None:
            if in_stock:
                results = [p for p in results if any(v.available_stock > 0 and v.is_available for v in p.variants)]
            else:
                results = [p for p in results if all(v.available_stock == 0 or not v.is_available for v in p.variants)]
            total_count = len(results)
        return results, total_count

    def search_products(
        self,
        session: Session,
        query_text: str,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock: Optional[bool] = None,
    ) -> Tuple[List[Product], int]:
        """Search products with filters and eager-loaded relationships."""
        from sqlalchemy.orm import selectinload

        query = select(Product).options(
            selectinload(Product.variants),
            selectinload(Product.product_images),
        ).where(
            Product.deleted_at.is_(None),
            (Product.title.ilike(f"%{query_text}%")) | (Product.description.ilike(f"%{query_text}%")),
        )

        if category:
            query = query.where(Product.category_slug == category)
        if min_price is not None:
            query = query.where(Product.price >= min_price)
        if max_price is not None:
            query = query.where(Product.price <= max_price)

        total_count = len(session.exec(query).all())
        results = session.exec(query.offset(skip).limit(limit)).all()
        if in_stock is not None:
            if in_stock:
                results = [p for p in results if any(v.available_stock > 0 and v.is_available for v in p.variants)]
            else:
                results = [p for p in results if all(v.available_stock == 0 or not v.is_available for v in p.variants)]
            total_count = len(results)
        return results, total_count
    
    def get_low_stock_products(
        self,
        session: Session,
        threshold: int = 10,
        pagination: Optional[PaginationParams] = None,
    ) -> Tuple[List[Product], int]:
        """Get products with stock below threshold."""
        query = select(Product).where(
            (Product.quantity <= threshold) & (Product.is_active == True)
        )
        
        total_count = len(session.exec(query).all())
        
        if pagination:
            query = query.offset(pagination.offset).limit(pagination.page_size)
        
        products = session.exec(query).all()
        return products, total_count
    
    def update_stock(
        self,
        session: Session,
        product_id: int,
        quantity_change: int,
    ) -> Product:
        """Update product stock quantity."""
        product = self.get_by_id_or_raise(session, product_id)
        product.quantity = max(0, product.quantity + quantity_change)
        session.flush()
        logger.debug(f"Updated product stock", product_id=product_id, new_quantity=product.quantity)
        return product
    
    def get_active_products(
        self,
        session: Session,
        pagination: Optional[PaginationParams] = None,
    ) -> Tuple[List[Product], int]:
        """Get all active products."""
        return self.find(
            session,
            filters={"is_active": True},
            pagination=pagination,
            sort=SortParams("created_at", "desc"),
        )
