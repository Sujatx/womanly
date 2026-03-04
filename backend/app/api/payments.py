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
from app.services.razorpay_service import create_razorpay_order, verify_payment_signature
from app.services.email_service import send_order_confirmation
from app.api.cart import get_cart_with_items
from app.middleware.idempotency import get_idempotency_key_from_request, store_idempotency_key, get_cached_response
from app.core.exceptions import (
    InsufficientStockException,
    CartNotFoundException,
    PaymentFailedException,
    OrderNotFoundException,
    InvalidSignatureException
)
from app.core.logging import get_structured_logger
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import json

router = APIRouter()
logger = get_structured_logger(__name__)

class PaymentVerify(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

@router.post("/create-order")
async def create_order(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    request: Request = None,
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
    cached = await get_cached_response(session, idempotency_key, "/payments/create-order", current_user.id)
    if cached:
        return JSONResponse(
            status_code=cached.response_status_code,
            content=cached.get_response()
        )
    
    # ========== BEGIN ATOMIC CHECKOUT TRANSACTION ==========
    try:
        # 1. Get Cart with items
        cart = get_cart_with_items(session, current_user.id)
        if not cart or not cart.items:
            raise CartNotFoundException(current_user.id)
        
        # 2. Validate stock availability and calculate total
        total_amount = 0.0
        variant_checks = []  # Store variant checks for later stock deduction
        
        for item in cart.items:
            # Get variant with FOR UPDATE lock and eagerly load product to prevent N+1
            variant_stmt = (
                select(ProductVariant)
                .where(ProductVariant.id == item.variant_id)
                .options(selectinload(ProductVariant.product))
                .with_for_update()
            )
            variant = session.exec(variant_stmt).first()
            
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
            "/payments/create-order",
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
    statement = select(Order).where(
        Order.razorpay_order_id == data.razorpay_order_id,
        Order.deleted_at.is_(None)  # Exclude soft-deleted orders
    )
    order = session.exec(statement).first()
    
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
    
    # 3. Clear Cart
    cart_statement = select(Cart).where(Cart.user_id == current_user.id)
    cart = session.exec(cart_statement).first()
    if cart:
        session.delete(cart)
        
    session.commit()
    
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

@router.get("/orders/me", response_model=List[Order])
def get_my_orders(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    statement = (
        select(Order)
        .where(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
        .options(selectinload(Order.items))
    )
    return session.exec(statement).all()