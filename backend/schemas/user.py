"""
User Schemas

API request/response schemas for User.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr
from schemas.base import Response


# ============================================================
# Request Schemas
# ============================================================

class UserCreate(BaseModel):
    """Schema for creating a user"""
    email: EmailStr
    name: str
    password: Optional[str] = None
    role: str = "analyst"  # admin, manager, analyst


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


# ============================================================
# Response Schemas
# ============================================================

class UserData(BaseModel):
    """User data for API responses (excludes password_hash)"""
    id: int
    email: str
    name: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Concrete response types
class UserResponse(Response[UserData]):
    """Response with single user"""
    pass


class UserListResponse(Response[List[UserData]]):
    """Response with list of users"""
    pass
