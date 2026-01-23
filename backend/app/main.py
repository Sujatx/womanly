from fastapi import FastAPI
from app.config import settings
from app.api import products, auth, cart, payments

app = FastAPI(title="Womanly API", version="1.0.0")

app.include_router(products.router, tags=["products"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(cart.router, prefix="/cart", tags=["cart"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Womanly API", "env": settings.ENV_NAME}

@app.get("/health")
def health_check():
    return {"status": "ok"}
