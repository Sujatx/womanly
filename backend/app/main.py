from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import products, auth, cart, payments, addresses
from app.db import engine
from sqlmodel import SQLModel

app = FastAPI(title="Womanly API", version="1.0.0")

@app.on_event("startup")
def on_startup():
    # Automatically create tables/columns if they don't exist
    SQLModel.metadata.create_all(engine)

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router, tags=["products"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(cart.router, prefix="/cart", tags=["cart"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])
app.include_router(addresses.router, prefix="/addresses", tags=["addresses"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Womanly API", "env": settings.ENV_NAME}

@app.get("/health")
def health_check():
    return {"status": "ok"}