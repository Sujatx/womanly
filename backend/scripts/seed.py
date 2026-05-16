"""Seed the database with a curated MVP catalog.

This keeps the storefront usable without depending on external product APIs.
Run after migrations:

    c:/Users/sujat/Desktop/repos/womanly/.venv/Scripts/python.exe backend/scripts/seed.py
"""

from __future__ import annotations

import os
import re
import sys

# Add backend to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import engine
from app.models import Category, Product
from app.models.product import ProductImage, ProductVariant
from sqlmodel import Session, SQLModel, select

MVP_PRODUCTS = [
    {
        "title": "Silk Slip Dress",
        "collection": "Evening",
        "price": 385,
        "brand": "Womanly Atelier",
        "description": "Luxurious silk slip dress with delicate bias cut. Crafted from 100% mulberry silk with adjustable straps and a flowing silhouette. Perfect for evening occasions.",
        "images": [
            "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=800&q=90",
            "https://images.unsplash.com/photo-1539008835657-9e8e9680c956?w=800&q=90",
        ],
        "sizes": ["XS", "S", "M", "L", "XL"],
        "colors": ["Ivory", "Black", "Champagne"],
        "in_stock": True,
    },
    {
        "title": "Cashmere Wrap Coat",
        "collection": "Outerwear",
        "price": 795,
        "brand": "Womanly Atelier",
        "description": "Double-faced cashmere coat with an elegant wrap silhouette. Features wide lapels, self-tie belt, and Italian-crafted construction.",
        "images": [
            "https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=800&q=90",
            "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=800&q=90",
        ],
        "sizes": ["XS", "S", "M", "L", "XL"],
        "colors": ["Camel", "Charcoal", "Cream"],
        "in_stock": True,
    },
    {
        "title": "Linen Shirt Dress",
        "collection": "Summer",
        "price": 185,
        "brand": "Womanly Atelier",
        "description": "Relaxed linen shirt dress with mother-of-pearl buttons. Classic collar and bracelet-length sleeves. Pre-washed for softness.",
        "images": [
            "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=800&q=90",
            "https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=800&q=90",
        ],
        "sizes": ["XS", "S", "M", "L", "XL"],
        "colors": ["White", "Sand", "Olive"],
        "in_stock": True,
    },
    {
        "title": "Tailored Wool Trousers",
        "collection": "Essentials",
        "price": 295,
        "brand": "Womanly Atelier",
        "description": "High-waisted wool trousers with a tailored fit. Features pressed creases, side pockets, and a concealed zip closure.",
        "images": [
            "https://images.unsplash.com/photo-1594633313593-bab3825d0caf?w=800&q=90",
            "https://images.unsplash.com/photo-1624206112918-f140f087f9b5?w=800&q=90",
        ],
        "sizes": ["24", "26", "28", "30", "32"],
        "colors": ["Black", "Navy", "Grey"],
        "in_stock": True,
    },
    {
        "title": "Merino Knit Turtleneck",
        "collection": "Knitwear",
        "price": 185,
        "brand": "Womanly Atelier",
        "description": "Fine gauge merino wool turtleneck. Lightweight yet warm with a slim fit. Ideal for layering or wearing alone.",
        "images": [
            "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=800&q=90",
            "https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?w=800&q=90",
        ],
        "sizes": ["XS", "S", "M", "L", "XL"],
        "colors": ["Black", "Ivory", "Camel", "Navy"],
        "in_stock": True,
    },
    {
        "title": "Leather Midi Skirt",
        "collection": "Modern Classic",
        "price": 495,
        "brand": "Womanly Atelier",
        "description": "Butter-soft lambskin leather skirt with an A-line silhouette. Features a concealed side zip and fully lined interior.",
        "images": [
            "https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?w=800&q=90",
            "https://images.unsplash.com/photo-1581044777550-4cfa60707c03?w=800&q=90",
        ],
        "sizes": ["XS", "S", "M", "L", "XL"],
        "colors": ["Black", "Chocolate"],
        "in_stock": False,
    },
    {
        "title": "Cotton Poplin Blouse",
        "collection": "Essentials",
        "price": 165,
        "brand": "Womanly Atelier",
        "description": "Classic white poplin blouse with French cuffs and a relaxed fit. Crafted from 100% Egyptian cotton.",
        "images": [
            "https://images.unsplash.com/photo-1564257577-49e8f72d7f0d?w=800&q=90",
            "https://images.unsplash.com/photo-1591369822096-ffd140ec948f?w=800&q=90",
        ],
        "sizes": ["XS", "S", "M", "L", "XL"],
        "colors": ["White", "Ivory"],
        "in_stock": True,
    },
    {
        "title": "Wide Leg Denim",
        "collection": "Denim",
        "price": 225,
        "brand": "Womanly Atelier",
        "description": "High-rise wide leg jeans in Japanese selvedge denim. Classic five-pocket styling with a full-length inseam.",
        "images": [
            "https://images.unsplash.com/photo-1582418702059-97ebafb35d09?w=800&q=90",
            "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=800&q=90",
        ],
        "sizes": ["24", "26", "28", "30", "32"],
        "colors": ["Indigo", "Black", "Ecru"],
        "in_stock": True,
    },
]


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "item"


def upsert_category(session: Session, collection: str) -> Category:
    category_slug = slugify(collection)
    category = session.exec(select(Category).where(Category.slug == category_slug)).first()

    if category:
        return category

    category = Category(name=collection, slug=category_slug)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def upsert_product(session: Session, product_data: dict, category: Category) -> Product:
    product = session.exec(select(Product).where(Product.title == product_data["title"])).first()
    thumbnail = product_data["images"][0] if product_data.get("images") else None

    if product is None:
        product = Product(
            title=product_data["title"],
            description=product_data["description"],
            price=float(product_data["price"]),
            brand=product_data.get("brand"),
            thumbnail=thumbnail,
            category_slug=category.slug,
            category_id=category.id,
        )
        session.add(product)
    else:
        product.description = product_data["description"]
        product.price = float(product_data["price"])
        product.brand = product_data.get("brand")
        product.thumbnail = thumbnail
        product.category_slug = category.slug
        product.category_id = category.id
        session.add(product)

    session.commit()
    session.refresh(product)
    return product


def ensure_images(session: Session, product: Product, image_urls: list[str]) -> None:
    existing_urls = {
        image.image_url
        for image in session.exec(select(ProductImage).where(ProductImage.product_id == product.id)).all()
    }

    changed = False
    for index, image_url in enumerate(image_urls):
        if image_url in existing_urls:
            continue

        session.add(
            ProductImage(
                product_id=product.id,
                image_url=image_url,
                alt_text=f"{product.title} image {index + 1}",
                display_order=index,
                is_primary=index == 0,
            )
        )
        changed = True

    if changed:
        session.commit()


def ensure_variants(session: Session, product: Product, sizes: list[str], colors: list[str], in_stock: bool) -> None:
    existing_skus = {
        variant.sku
        for variant in session.exec(select(ProductVariant).where(ProductVariant.product_id == product.id)).all()
    }

    stock_quantity = 12 if in_stock else 0
    is_available = bool(in_stock)

    changed = False
    for size in sizes:
        for color in colors:
            sku = f"{slugify(product.title)}-{slugify(size)}-{slugify(color)}"
            if sku in existing_skus:
                continue

            session.add(
                ProductVariant(
                    product_id=product.id,
                    sku=sku,
                    size=size,
                    color=color,
                    stock_quantity=stock_quantity,
                    reserved_quantity=0,
                    is_available=is_available,
                    price_adjustment=0.0,
                )
            )
            changed = True

    if changed:
        session.commit()


def seed() -> None:
    SQLModel.metadata.create_all(engine)
    print("Seeding curated MVP catalog...")

    with Session(engine) as session:
        for product_data in MVP_PRODUCTS:
            category = upsert_category(session, product_data["collection"])
            product = upsert_product(session, product_data, category)
            ensure_images(session, product, product_data["images"])
            ensure_variants(
                session,
                product,
                product_data["sizes"],
                product_data["colors"],
                product_data["in_stock"],
            )

    print(f"Seeded {len(MVP_PRODUCTS)} MVP products.")


if __name__ == "__main__":
    seed()
