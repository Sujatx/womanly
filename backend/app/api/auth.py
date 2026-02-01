from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.db import get_session
from app.models import User, UserCreate, UserRead, Token
from app.models.user import EmailVerificationToken
from app.security.hashing import get_password_hash, verify_password
from app.security.token import create_access_token
from app.deps import get_current_user
from app.services.email_service import send_verification_email
import uuid
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/signup", response_model=Token)
async def signup(user_in: UserCreate, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == user_in.email)).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        is_verified=False
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Generate verification token
    token_str = str(uuid.uuid4())
    verification_token = EmailVerificationToken(
        user_id=user.id,
        token=token_str,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    session.add(verification_token)
    session.commit()
    
    # REAL: Send email via Mailtrap
    try:
        await send_verification_email(user.email, token_str)
    except Exception as e:
        print(f"ERROR: Failed to send verification email: {e}")
        # We don't fail signup if email fails, but we should log it
    
    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@router.post("/verify-email")
def verify_email(token: str, session: Session = Depends(get_session)):
    db_token = session.exec(
        select(EmailVerificationToken)
        .where(EmailVerificationToken.token == token)
        .where(EmailVerificationToken.is_used == False)
        .where(EmailVerificationToken.expires_at > datetime.utcnow())
    ).first()
    
    if not db_token:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
        
    user = session.get(User, db_token.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.is_verified = True
    db_token.is_used = True
    session.add(user)
    session.add(db_token)
    session.commit()
    
    return {"status": "success", "message": "Email verified successfully"}

@router.post("/login", response_model=Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@router.get("/me", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user