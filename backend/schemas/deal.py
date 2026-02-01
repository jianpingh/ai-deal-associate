"""
Deal Schemas

Pydantic models for Deal API operations.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from .base import Response


class DealCreate(BaseModel):
    """Schema for creating a new deal"""
    name: str
    client_name: Optional[str] = None
    status: str = "New"


class DealUpdate(BaseModel):
    """Schema for updating a deal"""
    name: Optional[str] = None
    client_name: Optional[str] = None
    status: Optional[str] = None


class DealData(BaseModel):
    """Schema for deal response data"""
    id: int
    name: str
    client_name: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Allow conversion from ORM model


# Concrete response types for Swagger documentation
class DealResponse(Response[DealData]):
    """Response with single deal"""
    pass


class DealListResponse(Response[List[DealData]]):
    """Response with list of deals"""
    pass
