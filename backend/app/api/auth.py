from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.db import get_session
from app.models import User, UserCreate, UserRead, Token
from app.models.user import EmailVerificationToken, RefreshToken, BlacklistedToken, CSRFToken
from app.security.hashing import get_password_hash, verify_password
from app.security.token import create_access_token, create_refresh_token, verify_refresh_token
from app.deps import get_current_user
from app.services.email_service import send_verification_email
from app.middleware.csrf import create_csrf_token_in_db
from jose import jwt
from pydantic import BaseModel
import uuid
from datetime import datetime, timedelta
from app.config import settings

router = APIRouter()

# Explicit login schema (instead of relying on OAuth2PasswordRequestForm field names)
class LoginRequest(BaseModel):
    email: str  # Explicitly named 'email' for clarity
    password: str


class LoginResponse(Token):
    """Login response with tokens and user info."""
    pass

@router.get("/csrf-token")
def get_csrf_token(session: Session = Depends(get_session)):
    """
    Get a CSRF token for protecting state-changing requests.
    
    This endpoint should be called before making POST/PUT/DELETE requests.
    Include the returned CSRF token in the X-CSRF-Token header.
    """
    csrf_token = create_csrf_token_in_db(session)
    return {"csrf_token": csrf_token, "expires_in": 3600}

@router.post("/signup", response_model=Token)
async def signup(user_in: UserCreate, session: Session = Depends(get_session)):
    user = session.exec(
        select(User).where(
            User.email == user_in.email,
            User.deleted_at.is_(None)  # Check for non-deleted users
        )
    ).first()
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
    
    # Create tokens
    access_token = create_access_token(subject=user.email)
    refresh_token = create_refresh_token(subject=user.email)
    
    # Store refresh token in database
    db_refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    session.add(db_refresh_token)
    session.commit()
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", "user": user}

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

@router.post("/login", response_model=LoginResponse)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Session = Depends(get_session)):
    """
    DEPRECATED: Use /login-email instead.
    
    This endpoint uses OAuth2 form format. For security clarity, use the /login-email endpoint instead.
    Accepts form data where field 'username' should contain the user email.
    """
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Create tokens
    access_token = create_access_token(subject=user.email)
    refresh_token = create_refresh_token(subject=user.email)
    
    # Store refresh token in database
    db_refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    session.add(db_refresh_token)
    session.commit()
    
    return LoginResponse(access_token=access_token, refresh_token=refresh_token, token_type="bearer", user=user)


@router.post("/login-email", response_model=LoginResponse)
def login_email(credentials: LoginRequest, session: Session = Depends(get_session)):
    """
    Login with email and password.
    
    This is the recommended login endpoint. Uses explicit email field instead of OAuth2 'username' field.
    
    Args:
        credentials: LoginRequest with 'email' and 'password'
    
    Returns:
        LoginResponse with access_token, refresh_token, and user info
    
    Raises:
        400: If email or password is incorrect
        401: If user is inactive
    """
    email = credentials.email.lower().strip()
    
    # Validate email format
    if not email or '@' not in email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email address"
        )
    
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        # Return generic error to prevent email enumeration
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    # Create tokens
    access_token = create_access_token(subject=user.email)
    refresh_token = create_refresh_token(subject=user.email)
    
    # Store refresh token in database
    db_refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    session.add(db_refresh_token)
    session.commit()
    
    return LoginResponse(access_token=access_token, refresh_token=refresh_token, token_type="bearer", user=user)

@router.get("/me", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/refresh", response_model=Token)
def refresh_access_token(refresh_token_str: str, session: Session = Depends(get_session)):
    """
    Refresh access token using a valid refresh token.
    
    Takes a refresh token and returns a new access token + new refresh token.
    """
    # Verify the refresh token
    payload = verify_refresh_token(refresh_token_str)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if refresh token exists in database and is not revoked
    db_token = session.exec(
        select(RefreshToken).where(RefreshToken.token == refresh_token_str)
    ).first()
    
    if not db_token or db_token.is_revoked or db_token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is revoked or expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create new tokens
    new_access_token = create_access_token(subject=user.email)
    new_refresh_token = create_refresh_token(subject=user.email)
    
    # Mark old refresh token as rotated and create new one
    db_token.rotated_at = datetime.utcnow()
    db_token.is_revoked = True  # Invalidate old token after rotation
    
    new_db_token = RefreshToken(
        user_id=user.id,
        token=new_refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    
    session.add(db_token)
    session.add(new_db_token)
    session.commit()
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/logout")
def logout(token: str, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """
    Logout user by blacklisting their access token.
    
    The Authorization header will be automatically passed as the token parameter.
    """
    try:
        # Decode token to get expiry time
        payload = jwt.decode(token, settings.SECRET_KEY.get_secret_value(), algorithms=[settings.ALGORITHM])
        
        # Convert exp timestamp to datetime
        exp_timestamp = payload.get("exp")
        if exp_timestamp:
            expires_at = datetime.fromtimestamp(exp_timestamp)
        else:
            # If no exp, set to 30 minutes from now (default token expiry)
            expires_at = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Add token to blacklist
        blacklisted_token = BlacklistedToken(
            token=token,
            user_id=current_user.id,
            expires_at=expires_at,
            revocation_reason="logout"
        )
        session.add(blacklisted_token)
        session.commit()
        
        return {"status": "success", "message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to logout",
            headers={"WWW-Authenticate": "Bearer"},
        )