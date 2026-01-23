from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.db import get_session
from app.models import Cart, CartItem, CartRead, CartItemCreate, User, CartItemRead
from app.deps import get_current_user

router = APIRouter()

def get_cart_with_items(session: Session, user_id: int):
    statement = (
        select(Cart)
        .where(Cart.user_id == user_id)
        .options(selectinload(Cart.items).selectinload(CartItem.product))
    )
    return session.exec(statement).first()

@router.get("/", response_model=CartRead)
def get_cart(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    cart = get_cart_with_items(session, current_user.id)
    if not cart:
        cart = Cart(user_id=current_user.id)
        session.add(cart)
        session.commit()
        session.refresh(cart)
        # Re-fetch to get empty items list properly
        cart = get_cart_with_items(session, current_user.id)
    
    # Calculate totals
    subtotal = 0.0
    count = 0
    # Provide explicit list for Pydantic validation if needed, 
    # but CartRead items type matches relationship.
    
    # We need to manually calculate subtotal for the response 
    # because it's not a database field
    for item in cart.items:
        if item.product:
            subtotal += item.product.price * item.quantity
        count += item.quantity
        
    return CartRead(id=cart.id, items=cart.items, count=count, subtotal=subtotal)

@router.post("/items", response_model=CartRead)
def add_to_cart(
    item_in: CartItemCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    cart = get_cart_with_items(session, current_user.id)
    if not cart:
        cart = Cart(user_id=current_user.id)
        session.add(cart)
        session.commit()
        session.refresh(cart)
        cart = get_cart_with_items(session, current_user.id)
        
    # Check if item exists
    # Since we eager loaded, we can iterate
    existing_item = next((i for i in cart.items if i.product_id == item_in.product_id), None)
    
    if existing_item:
        existing_item.quantity += item_in.quantity
        session.add(existing_item)
    else:
        new_item = CartItem(
            cart_id=cart.id,
            product_id=item_in.product_id,
            quantity=item_in.quantity,
            selected_options=item_in.selected_options
        )
        session.add(new_item)
        
    session.commit()
    # Return full cart
    return get_cart(current_user, session)

@router.delete("/items/{item_id}", response_model=CartRead)
def remove_from_cart(
    item_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    item = session.get(CartItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    # Verify ownership
    # We can load cart or just check cart_id if we trust the flow.
    # But better to check.
    cart = session.get(Cart, item.cart_id)
    if not cart or cart.user_id != current_user.id:
         raise HTTPException(status_code=403, detail="Not authorized")
        
    session.delete(item)
    session.commit()
    return get_cart(current_user, session)
