from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
from datetime import datetime, timedelta

class AddressBase(SQLModel):
    full_name: str
    phone: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str = Field(default="India")
    is_default: bool = Field(default=False)
    address_type: str = Field(default="home") # home, work, other

class Address(AddressBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    
    user: "User" = Relationship(back_populates="addresses")

class EmailVerificationToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    token: str = Field(unique=True, index=True)
    expires_at: datetime
    is_used: bool = Field(default=False)

class RefreshToken(SQLModel, table=True):
    """Refresh tokens for issuing new access tokens."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    token: str = Field(unique=True, index=True)
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    rotated_at: Optional[datetime] = None
    is_revoked: bool = Field(default=False)

class BlacklistedToken(SQLModel, table=True):
    """Blacklisted tokens that have been revoked/logged out."""
    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(unique=True, index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    expires_at: datetime
    blacklisted_at: datetime = Field(default_factory=datetime.utcnow)
    revocation_reason: str = Field(default="logout")

class CSRFToken(SQLModel, table=True):
    """CSRF tokens for protecting state-changing requests."""
    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(unique=True, index=True)
    session_id: str = Field(index=True)  # Can be associated with user session or request
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    is_used: bool = Field(default=False)

class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True)
    full_name: Optional[str] = None
    is_active: bool = True
    is_verified: bool = Field(default=False)
    is_superuser: bool = False

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    
    # Soft delete support
    deleted_at: Optional[datetime] = Field(default=None, index=True)
    
    addresses: List[Address] = Relationship(back_populates="user")
    
    def soft_delete(self):
        """Mark user as deleted (soft delete)."""
        self.deleted_at = datetime.utcnow()
        self.is_active = False
    
    def is_deleted(self) -> bool:
        """Check if user is soft deleted."""
        return self.deleted_at is not None

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int

class AddressRead(AddressBase):
    id: int

class Token(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserRead
