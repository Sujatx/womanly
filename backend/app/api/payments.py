from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.db import get_session
from app.models import Cart, Order, OrderItem, User
from app.deps import get_current_user
from app.services.razorpay_service import create_razorpay_order, verify_payment_signature
from app.services.email_service import send_order_confirmation
from app.api.cart import get_cart_with_items
from pydantic import BaseModel

router = APIRouter()

class PaymentVerify(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

@router.post("/create-order")
def create_order(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # ... (rest of create_order logic remains the same)
    # 1. Get Cart
    cart = get_cart_with_items(session, current_user.id)
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
        
    # 2. Calculate Total
    total_amount = 0.0
    for item in cart.items:
        if item.product:
            total_amount += item.product.price * item.quantity
            
    # Razorpay expects amount in paise (integers)
    # Assuming price is in INR or we convert it. DummyJSON is USD, 
    # but let's assume INR for Razorpay demo.
    amount_paise = int(total_amount * 100)
    
    # 3. Create Pending Order in DB
    db_order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        status="pending"
    )
    session.add(db_order)
    session.commit()
    session.refresh(db_order)
    
    # Add items to order
    for item in cart.items:
        if item.product:
            order_item = OrderItem(
                order_id=db_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=item.product.price
            )
            session.add(order_item)
    
    session.commit()
    
    # 4. Create Razorpay Order
    try:
        rzp_order = create_razorpay_order(
            amount=amount_paise,
            notes={"db_order_id": str(db_order.id), "user_id": str(current_user.id)}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # 5. Update Order with Razorpay Order ID
    db_order.razorpay_order_id = rzp_order["id"]
    session.add(db_order)
    session.commit()
    
    return {
        "id": rzp_order["id"],
        "amount": rzp_order["amount"],
        "currency": rzp_order["currency"],
        "db_order_id": db_order.id
    }

@router.post("/verify")
async def verify_payment(
    data: PaymentVerify,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # 1. Verify Signature
    is_valid = verify_payment_signature(
        data.razorpay_order_id,
        data.razorpay_payment_id,
        data.razorpay_signature
    )
    
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid payment signature")
        
    # 2. Update Order Status
    statement = select(Order).where(Order.razorpay_order_id == data.razorpay_order_id)
    order = session.exec(statement).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    order.status = "paid"
    order.razorpay_payment_id = data.razorpay_payment_id
    session.add(order)
    
    # 3. Clear Cart
    cart_statement = select(Cart).where(Cart.user_id == current_user.id)
    cart = session.exec(cart_statement).first()
    if cart:
        session.delete(cart)
        
    session.commit()

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