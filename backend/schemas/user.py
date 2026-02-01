"""
User Schemas

API request/response schemas for User.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from schemas.base import Response


# ============================================================
# Request Schemas
# ============================================================

class UserCreate(BaseModel):
    """Schema for creating a user"""
    email: EmailStr = Field(..., description="User's email address (required, must be unique)")
    name: str = Field(..., min_length=1, max_length=100, description="User's full name (required)")
    password: Optional[str] = Field(None, description="User's password (optional)")
    role: str = Field("analyst", pattern="^(admin|manager|analyst)$", description="User's role - admin, manager, or analyst (default: analyst)")


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = Field(None, description="User's email address")
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="User's full name")
    role: Optional[str] = Field(None, pattern="^(admin|manager|analyst)$", description="User's role")
    is_active: Optional[bool] = Field(None, description="Whether user is active")


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
