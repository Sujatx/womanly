import json
import urllib.request
import sys
import os

# Add backend to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, select
from app.db import engine
from app.models import Product, Category
from app.models.product import ProductImage, ProductVariant

def slugify(text: str) -> str:
    return text.lower().replace(" ", "-").replace("'", "")

def seed():
    # Ensure tables exist
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)
    
    print("Fetching data from DummyJSON...")
    url = "https://dummyjson.com/products?limit=100"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            products_data = data['products']
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    print(f"Fetched {len(products_data)} products.")

    with Session(engine) as session:
        # 1. Handle Categories
        print("Processing categories...")
        cat_map = {}
        
        for p_data in products_data:
            cat_name = p_data['category']
            if cat_name not in cat_map:
                category = session.exec(select(Category).where(Category.slug == cat_name)).first()
                if not category:
                    category = Category(name=cat_name.title().replace("-", " "), slug=cat_name)
                    session.add(category)
                    session.commit()
                    session.refresh(category)
                cat_map[cat_name] = category

        # 2. Handle Products
        print("Processing products...")
        for p_data in products_data:
            existing = session.exec(select(Product).where(Product.title == p_data['title'])).first()
            if existing:
                continue

            cat_slug = p_data['category']
            category = cat_map.get(cat_slug)
            
            product = Product(
                title=p_data['title'],
                description=p_data['description'],
                price=float(p_data['price']),
                brand=p_data.get('brand'),
                thumbnail=p_data.get('thumbnail'),
                category_slug=cat_slug,
                category_id=category.id if category else None
            )
            session.add(product)
            session.commit()
            session.refresh(product)

            # Add Images
            images = p_data.get('images', [])
            for i, img_url in enumerate(images):
                p_img = ProductImage(
                    product_id=product.id,
                    image_url=img_url,
                    display_order=i,
                    is_primary=(i == 0)
                )
                session.add(p_img)

            # Add Variants (Mocking some sizes/colors)
            sizes = ["S", "M", "L", "XL"]
            colors = ["Black", "Steel", "Ghost"]
            
            for size in sizes:
                for color in colors:
                    variant = ProductVariant(
                        product_id=product.id,
                        sku=f"{slugify(product.title)}-{size}-{color}",
                        size=size,
                        color=color,
                        stock_quantity=10,
                        price_adjustment=0.0
                    )
                    session.add(variant)
            
            session.commit()
        
        print("Seeding complete.")

if __name__ == "__main__":
    seed()