from app.db import engine
from sqlmodel import Session, delete
from app.models import Product
from app.models.product import ProductImage, ProductVariant

session = Session(engine)

# Delete in order of dependencies
session.exec(delete(ProductVariant))
session.exec(delete(ProductImage))
session.exec(delete(Product))

session.commit()
print("Database cleared")
