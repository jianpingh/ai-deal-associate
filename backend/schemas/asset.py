"""
Asset Schemas

Pydantic models for Asset API operations.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from .base import Response


class AssetCreate(BaseModel):
    """Schema for creating a new asset"""
    deal_id: int
    name: str
    asset_type: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    valuation: Optional[float] = None


class AssetUpdate(BaseModel):
    """Schema for updating an asset"""
    name: Optional[str] = None
    asset_type: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    valuation: Optional[float] = None


class AssetData(BaseModel):
    """Schema for asset response data"""
    id: int
    deal_id: int
    name: str
    asset_type: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    valuation: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True  # Allow conversion from ORM model


# Concrete response types for Swagger documentation
class AssetResponse(Response[AssetData]):
    """Response with single asset"""
    pass


class AssetListResponse(Response[List[AssetData]]):
    """Response with list of assets"""
    pass
