from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlmodel import Session, select
from app.db import get_session
from app.models import Cart, Order, OrderItem, User
from app.deps import get_current_user
from app.services.stripe_service import create_payment_intent, construct_event
from app.api.cart import get_cart_with_items

router = APIRouter()

@router.post("/create-payment-intent")
def create_intent(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # 1. Get Cart
    cart = get_cart_with_items(session, current_user.id)
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
        
    # 2. Calculate Total
    total_amount = 0.0
    for item in cart.items:
        if item.product:
            total_amount += item.product.price * item.quantity
            
    # Stripe expects integer cents
    amount_cents = int(total_amount * 100)
    
    # 3. Create Pending Order
    # Check if we already have a pending order for this cart/session? 
    # For simplicity, create new one.
    
    order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        status="pending"
    )
    session.add(order)
    session.commit()
    session.refresh(order)
    
    # Add items to order
    for item in cart.items:
        if item.product:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=item.product.price
            )
            session.add(order_item)
    
    session.commit()
    
    # 4. Create Stripe Intent
    try:
        intent = create_payment_intent(
            amount=amount_cents,
            metadata={"order_id": str(order.id), "user_id": str(current_user.id)}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # 5. Update Order with Intent ID
    order.stripe_payment_intent_id = intent["id"]
    session.add(order)
    session.commit()
    
    return {"clientSecret": intent["client_secret"], "orderId": order.id}

@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None), session: Session = Depends(get_session)):
    payload = await request.body()
    
    try:
        event = construct_event(payload, stripe_signature)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except Exception as e: # stripe.error.SignatureVerificationError
        raise HTTPException(status_code=400, detail="Invalid signature")
        
    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        order_id = intent["metadata"].get("order_id")
        user_id = intent["metadata"].get("user_id")
        
        if order_id:
            order = session.get(Order, int(order_id))
            if order:
                order.status = "paid"
                session.add(order)
                
                # Clear Cart
                if user_id:
                    # We need to find the cart for this user and clear items
                    # Using exec(select) inside webhook might need careful session handling if async
                    # But FastAPI dependency handles session per request.
                    
                    cart = session.exec(select(Cart).where(Cart.user_id == int(user_id))).first()
                    if cart:
                        # Delete all items
                        # session.delete(cart) # Or just items.
                        # Deleting cart is easier, next get_cart will create new one.
                        session.delete(cart) 
                        
                session.commit()
                
    return {"status": "success"}
