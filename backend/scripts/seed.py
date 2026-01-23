import json
import urllib.request
import sys
import os

# Add backend to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, select
from app.db import engine
from app.models import Product, Category

def slugify(text: str) -> str:
    return text.lower().replace(" ", "-").replace("'", "")

def seed():
    print("Fetching data from DummyJSON...")
    url = "https://dummyjson.com/products?limit=100"
    try:
        with urllib.request.urlopen(url) as response:
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
        
        # Get existing categories to avoid duplicates if re-running (naive check)
        existing_cats = session.exec(select(Category)).all()
        for c in existing_cats:
            cat_map[c.slug] = c

        for p_data in products_data:
            cat_name = p_data['category']
            cat_slug = slugify(cat_name) # DummyJSON categories are slugs mostly, but let's be safe
            
            # In DummyJSON, 'category' is a slug-like string (e.g. 'beauty', 'fragrances')
            # We'll use it as both name (capitalized) and slug for simplicity if needed
            # But wait, DummyJSON 'category' is strictly the slug/id. 
            # We can capitalize it for the name.
            
            if cat_slug not in cat_map:
                category = Category(name=cat_name.title().replace("-", " "), slug=cat_name)
                session.add(category)
                session.commit()
                session.refresh(category)
                cat_map[cat_name] = category
                print(f"Created category: {category.name}")

        # 2. Handle Products
        print("Processing products...")
        for p_data in products_data:
            # Check if product exists
            existing = session.exec(select(Product).where(Product.title == p_data['title'])).first()
            if existing:
                continue

            cat_slug = p_data['category']
            category = cat_map.get(cat_slug)
            
            if not category:
                # Fallback if slugify logic differed
                category = session.exec(select(Category).where(Category.slug == cat_slug)).first()

            product = Product(
                title=p_data['title'],
                description=p_data['description'],
                price=float(p_data['price']),
                brand=p_data.get('brand'),
                thumbnail=p_data.get('thumbnail'),
                images=p_data.get('images', []),
                tags=p_data.get('tags', []),
                category_slug=cat_slug,
                category_id=category.id if category else None
            )
            session.add(product)
        
        session.commit()
        print("Seeding complete.")

if __name__ == "__main__":
    seed()
