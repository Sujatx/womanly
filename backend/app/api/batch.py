"""Batch API endpoints for reducing HTTP round trips."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import BaseModel

from app.db import get_session
from app.models.product import Product
from app.api.products import _build_product_detail, ProductDetail
from app.middleware.validation import validate_phone, validate_postal_code

router = APIRouter(prefix="/api/v1/batch", tags=["batch"])


class ProductBatchRequest(BaseModel):
    """Request multiple products by ID in a single call."""
    product_ids: List[int]
    include_variants: bool = True
    include_images: bool = True


class ProductBatchResponse(BaseModel):
    """Response with multiple products."""
    products: List[ProductDetail]
    not_found: List[int] = []


class AddressValidationInput(BaseModel):
    full_name: str
    phone: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str = "India"


class AddressValidationResult(BaseModel):
    index: int
    is_valid: bool
    errors: List[str] = []


class AddressBatchValidateRequest(BaseModel):
    addresses: List[AddressValidationInput]


class AddressBatchValidateResponse(BaseModel):
    results: List[AddressValidationResult]


@router.post("/products", response_model=ProductBatchResponse)
async def batch_get_products(
    request: ProductBatchRequest,
    session: Session = Depends(get_session),
):
    """
    Fetch multiple products in a single request.
    
    Reduces N API calls to 1 for improved performance.
    Max 50 products per batch.
    """
    if len(request.product_ids) > 50:
        raise HTTPException(
            status_code=400,
            detail="Maximum 50 products per batch request"
        )
    
    if not request.product_ids:
        return ProductBatchResponse(products=[], not_found=[])
    
    # Single optimized query
    from sqlmodel import selectinload
    
    query = select(Product).where(
        Product.id.in_(request.product_ids),
        Product.deleted_at.is_(None)
    )
    
    if request.include_variants:
        query = query.options(selectinload(Product.variants))
    
    if request.include_images:
        query = query.options(selectinload(Product.product_images))
    
    products = session.exec(query).all()
    
    # Find which IDs were not found
    found_ids = {p.id for p in products}
    not_found_ids = [pid for pid in request.product_ids if pid not in found_ids]
    
    return ProductBatchResponse(
        products=[_build_product_detail(p) for p in products],
        not_found=not_found_ids
    )


@router.post("/addresses", response_model=AddressBatchValidateResponse)
async def batch_validate_addresses(request: AddressBatchValidateRequest):
    """Validate multiple addresses in a single request."""
    if len(request.addresses) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 addresses per batch request")

    results: List[AddressValidationResult] = []
    for index, address in enumerate(request.addresses):
        errors: List[str] = []

        if not address.full_name.strip():
            errors.append("Full name is required")
        if not address.address_line1.strip():
            errors.append("Address line 1 is required")
        if not address.city.strip():
            errors.append("City is required")
        if not address.state.strip():
            errors.append("State is required")
        if not validate_phone(address.phone):
            errors.append("Invalid phone format")
        if not validate_postal_code(address.postal_code):
            errors.append("Invalid postal code format")

        results.append(
            AddressValidationResult(
                index=index,
                is_valid=len(errors) == 0,
                errors=errors,
            )
        )

    return AddressBatchValidateResponse(results=results)
