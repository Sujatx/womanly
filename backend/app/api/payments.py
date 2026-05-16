from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks, Header, status
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from sqlalchemy import text
from app.db import get_session
from app.models import Cart, Order, OrderItem, User
from app.models.product import ProductVariant
from app.models.idempotency import IdempotencyKey
from app.models.inventory import deduct_stock_for_order
from app.deps import get_current_user
from app.services.razorpay_service import create_razorpay_order, verify_payment_signature, verify_webhook_signature
from app.services import send_order_confirmation
from app.api.cart import get_cart_with_items
from app.middleware import get_idempotency_key_from_request, store_idempotency_key, get_cached_response
from app.core.exceptions import (
    InsufficientStockException,
    CartNotFoundException,
    PaymentFailedException,
    OrderNotFoundException,
    InvalidSignatureException,
    ExternalServiceException,
)
from app.core.logging import get_structured_logger
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import json
from app.di_container import get as di_get

router = APIRouter()
logger = get_structured_logger(__name__)

class PaymentVerify(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class CheckoutItemInput(BaseModel):
    variant_id: int
    quantity: int = Field(ge=1)


class CheckoutRequest(BaseModel):
    items: list[CheckoutItemInput] | None = None


class RazorpayWebhookPayload(BaseModel):
    event: str
    payload: dict


def _get_webhook_order_info(payload: dict) -> tuple[str | None, str | None]:
    payment = payload.get("payment", {}).get("entity", {})
    order = payload.get("order", {}).get("entity", {})
    razorpay_order_id = payment.get("order_id") or order.get("id")
    razorpay_payment_id = payment.get("id")
    return razorpay_order_id, razorpay_payment_id


def _apply_razorpay_webhook(session: Session, event_name: str, payload: dict) -> dict:
    razorpay_order_id, razorpay_payment_id = _get_webhook_order_info(payload)

    if not razorpay_order_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook payload missing Razorpay order reference",
        )

    order = session.exec(select(Order).where(Order.razorpay_order_id == razorpay_order_id)).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order not found for Razorpay order {razorpay_order_id}",
        )

    if event_name in {"payment.captured", "order.paid"}:
        if order.status != "paid":
            order.update_status("paid", notes="Payment confirmed via Razorpay webhook", session=session)
            order.razorpay_payment_id = razorpay_payment_id or order.razorpay_payment_id
            session.add(order)
            session.commit()
            session.refresh(order)
        return {
            "status": "processed",
            "order_id": order.id,
            "order_status": order.status,
            "event": event_name,
        }

    if event_name == "payment.failed":
        return {
            "status": "ignored",
            "order_id": order.id,
            "order_status": order.status,
            "event": event_name,
        }

    return {
        "status": "ignored",
        "order_id": order.id,
        "order_status": order.status,
        "event": event_name,
    }

@router.post("/create-order")
async def create_order(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    request: Request = None,
    payload: CheckoutRequest | None = None,
    idempotency_key: str = Header(None, alias="Idempotency-Key")
):
    """
    Create an order with atomic checkout transaction.
    
    This endpoint:
    1. Checks stock availability for all cart items
    2. Deducts inventory atomically
    3. Creates order
    4. All steps are wrapped in a database transaction
    
    If any step fails, the entire transaction is rolled back.
    """
    # Validate idempotency key
    if not idempotency_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Idempotency-Key header is required"
        )
    
    # Check if we've already processed this request
    cached = await get_cached_response(session, idempotency_key, "/api/v1/payments/create-order", current_user.id)
    if cached:
        return JSONResponse(
            status_code=cached.response_status_code,
            content=cached.get_response()
        )
    
    # ========== BEGIN ATOMIC CHECKOUT TRANSACTION ==========
    try:
        # 1. Resolve checkout items from explicit payload or the user's cart
        checkout_items = payload.items if payload and payload.items else None
        cart = None
        if checkout_items is None:
            cart = get_cart_with_items(session, current_user.id)
            if not cart or not cart.items:
                raise CartNotFoundException(current_user.id)
            checkout_items = [CheckoutItemInput(variant_id=item.variant_id, quantity=item.quantity) for item in cart.items]
        elif len(checkout_items) == 0:
            raise CartNotFoundException(current_user.id)
        
        # 2. Validate stock availability and calculate total
        total_amount = 0.0
        variant_checks = []  # Store variant checks for later stock deduction
        
        for item in checkout_items:
            # Get variant with FOR UPDATE lock and eagerly load product to prevent N+1
            product_repo = di_get("product_repo")
            variant = product_repo.get_variant_for_update(session, item.variant_id)
            
            if not variant:
                logger.error("Variant not found in checkout", variant_id=item.variant_id)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Variant {item.variant_id} not found"
                )
            
            # Check if variant is available
            if not variant.is_available:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Variant {variant.sku} is no longer available"
                )
            
            # Check stock availability
            if variant.stock_quantity < item.quantity:
                logger.warning(
                    "Insufficient stock during checkout",
                    variant_id=variant.id,
                    sku=variant.sku,
                    available=variant.stock_quantity,
                    requested=item.quantity,
                    user_id=current_user.id
                )
                raise InsufficientStockException(
                    variant_id=variant.id,
                    available=variant.stock_quantity,
                    requested=item.quantity
                )
            
            # Access product via relationship (no additional query needed)
            product = variant.product
            
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product for variant {variant.id} not found"
                )
            
            # Calculate price: base price + variant adjustment
            item_price = product.price + variant.price_adjustment
            total_amount += item_price * item.quantity
            
            # Store for stock deduction
            variant_checks.append({
                'variant': variant,
                'quantity': item.quantity,
                'price': item_price,
                'product_id': product.id
            })
        
        # 3. Create pending order in DB
        db_order = Order(
            user_id=current_user.id,
            total_amount=total_amount,
            status="pending"
        )
        session.add(db_order)
        session.flush()  # Get the order ID without committing
        
        # 4. Deduct stock and add order items
        for check in variant_checks:
            variant = check['variant']
            
            # Deduct stock atomically using inventory management system
            deduct_stock_for_order(
                session=session,
                variant=variant,
                quantity=check['quantity'],
                order_id=db_order.id,
                user_id=current_user.id
            )
            
            # Create order item
            order_item = OrderItem(
                order_id=db_order.id,
                product_id=check['product_id'],
                quantity=check['quantity'],
                price_at_purchase=check['price']
            )
            session.add(order_item)
        
        # 5. Create Razorpay order
        amount_paise = int(total_amount * 100)  # Convert to paise
        
        try:
            rzp_order = create_razorpay_order(
                amount=amount_paise,
                notes={"db_order_id": str(db_order.id), "user_id": str(current_user.id)}
            )
        except ExternalServiceException:
            session.rollback()
            raise
        except Exception as e:
            logger.error(
                "Razorpay order creation failed",
                order_id=db_order.id,
                amount=total_amount,
                error=str(e),
                exc_info=True
            )
            # Rollback will happen automatically when exception is raised
            raise PaymentFailedException(
                message="Failed to create payment order",
                details={"error": str(e)}
            )
        
        # 6. Update order with Razorpay order ID
        db_order.razorpay_order_id = rzp_order["id"]
        session.add(db_order)
        
        # 7. Commit the entire transaction
        session.commit()
        session.refresh(db_order)
        
        logger.info(
            "Order created successfully",
            order_id=db_order.id,
            user_id=current_user.id,
            total_amount=total_amount,
            item_count=len(variant_checks),
            razorpay_order_id=rzp_order["id"]
        )
        
        # ========== END ATOMIC CHECKOUT TRANSACTION ==========
        
        response_data = {
            "id": rzp_order["id"],
            "amount": rzp_order["amount"],
            "currency": rzp_order["currency"],
            "db_order_id": db_order.id
        }
        
        # Store idempotency key for future identical requests
        await store_idempotency_key(
            session,
            idempotency_key,
            current_user.id,
            "/api/v1/payments/create-order",
            await request.body(),
            json.dumps(response_data),
            200
        )
        
        return response_data
    
    except (InsufficientStockException, CartNotFoundException, PaymentFailedException) as e:
        # These are expected exceptions - let them propagate to error handler
        session.rollback()
        raise
    
    except Exception as e:
        # Unexpected error - rollback and log
        session.rollback()
        logger.error(
            "Unexpected error during checkout",
            user_id=current_user.id,
            error=str(e),
            exc_info=True
        )
        raise PaymentFailedException(
            message="An unexpected error occurred during checkout",
            details={"error": str(type(e).__name__)}
        )

@router.post("/verify")
async def verify_payment(
    data: PaymentVerify,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Verify payment signature and complete the order.
    
    This endpoint:
    1. Verifies Razorpay payment signature
    2. Updates order status to 'paid'
    3. Clears user's cart
    4. Sends order confirmation email
    """
    # 1. Verify Signature
    is_valid = verify_payment_signature(
        data.razorpay_order_id,
        data.razorpay_payment_id,
        data.razorpay_signature
    )
    
    if not is_valid:
        logger.warning(
            "Invalid payment signature",
            razorpay_order_id=data.razorpay_order_id,
            user_id=current_user.id
        )
        raise InvalidSignatureException()
        
    # 2. Update Order Status
    order = di_get("order_repo").get_by_razorpay_order_id(session, data.razorpay_order_id)
    
    if not order:
        logger.error(
            "Order not found for payment verification",
            razorpay_order_id=data.razorpay_order_id,
            user_id=current_user.id
        )
        raise OrderNotFoundException(0)  # We don't have the order ID
        
    # Verify order belongs to current user
    if order.user_id != current_user.id:
        logger.warning(
            "User attempted to verify payment for another user's order",
            order_id=order.id,
            order_user_id=order.user_id,
            current_user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to verify this payment"
        )
    
    # Update order status using state machine
    order.update_status("paid", updated_by=current_user.id, notes="Payment verified via Razorpay")
    order.razorpay_payment_id = data.razorpay_payment_id
    session.add(order)
    
    # 3. Clear Cart using repository
    cart_repo = di_get("cart_repo")
    cart_repo.clear_cart(session, current_user.id)
    
    logger.info(
        "Payment verified successfully",
        order_id=order.id,
        razorpay_order_id=data.razorpay_order_id,
        razorpay_payment_id=data.razorpay_payment_id,
        user_id=current_user.id
    )

    # 4. Send Confirmation Email (Background)
    background_tasks.add_task(send_order_confirmation, current_user.email, order.id, order.total_amount)
    
    return {"status": "success", "order_id": order.id}


@router.post("/webhooks/razorpay", status_code=status.HTTP_200_OK)
async def razorpay_webhook(
    request: Request,
    session: Session = Depends(get_session),
    razorpay_signature: str = Header(None, alias="X-Razorpay-Signature"),
):
    """Process Razorpay webhook events and finalize payment state."""
    if not razorpay_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X-Razorpay-Signature header",
        )

    raw_body = await request.body()
    if not verify_webhook_signature(raw_body, razorpay_signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Razorpay webhook signature",
        )

    try:
        payload = RazorpayWebhookPayload.model_validate_json(raw_body)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Razorpay webhook payload",
        )

    return _apply_razorpay_webhook(session, payload.event, payload.payload)

@router.get("/orders/me", response_model=List[Order])
def get_my_orders(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    order_repo = di_get("order_repo")
    orders, _ = order_repo.get_orders_by_user(session=session, user_id=current_user.id)
    return orders