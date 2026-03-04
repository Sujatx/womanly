from app.db import engine
from sqlmodel import Session, select
from app.models import Product

session = Session(engine)
products = session.exec(select(Product)).all()
print(f"Total products: {len(products)}")
if products:
    print(f"First product: {products[0].title}")
