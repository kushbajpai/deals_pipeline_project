"""User schemas for API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserSchema(BaseModel):
    """User response schema."""

    id: int
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: str = Field(description="User role (admin, analyst, or partner)")
    is_active: bool
    email_verified: bool = False
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserUpdateSchema(BaseModel):
    """User update schema."""

    is_active: Optional[bool] = None
    full_name: Optional[str] = None

    class Config:
        from_attributes = True
