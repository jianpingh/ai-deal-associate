"""
Deal Schemas

Pydantic models for Deal API operations.
"""

from typing import Optional, List, Literal
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from .base import Response


# Valid options for enums
DEAL_TYPES = ("Acquisition", "Disposition", "Refinance")
ASSET_TYPES = ("Multifamily", "Office", "Retail", "Industrial", "Logistics", "Mixed-Use", "Other")
DEAL_STATUSES = ("New", "Active", "On Hold", "Closed", "Cancelled")
DEAL_STAGES = ("Sourcing", "Due Diligence", "LOI", "Under Contract", "Closing")


class DealCreate(BaseModel):
    """Schema for creating a new deal"""
    name: str = Field(..., min_length=1, max_length=200, description="Name of the deal")
    client_name: Optional[str] = Field(None, max_length=200, description="Name of the client")
    user_id: Optional[str] = Field(None, description="Owner user UUID", examples=["550e8400-e29b-41d4-a716-446655440000"])
    
    # Deal classification
    deal_type: str = Field(
        default="Acquisition", 
        description="Type of deal: Acquisition, Disposition, Refinance"
    )
    asset_type: Optional[str] = Field(
        None, 
        description="Type of asset: Multifamily, Office, Retail, Industrial, Logistics, Mixed-Use, Other"
    )
    
    # Status & Stage
    status: str = Field(
        default="New", 
        description="Deal status: New, Active, On Hold, Closed, Cancelled"
    )
    stage: Optional[str] = Field(
        None, 
        description="Deal stage: Sourcing, Due Diligence, LOI, Under Contract, Closing"
    )
    
    # Financial targets
    target_price: Optional[Decimal] = Field(
        None, 
        ge=0, 
        max_digits=15, 
        decimal_places=2,
        description="Target acquisition/sale price",
        examples=[10000000.00]
    )
    target_irr: Optional[Decimal] = Field(
        None, 
        ge=0, 
        le=100, 
        max_digits=5, 
        decimal_places=2,
        description="Target IRR percentage (0-100)",
        examples=[15.50]
    )
    
    # Dates
    target_close_date: Optional[date] = Field(None, description="Expected closing date")
    
    # Location & Notes
    market: Optional[str] = Field(None, max_length=100, description="Market/location (e.g., Dallas-Fort Worth)")
    description: Optional[str] = Field(None, max_length=2000, description="Deal notes/description")
    
    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            import uuid
            try:
                uuid.UUID(v)
            except ValueError:
                raise ValueError("user_id must be a valid UUID")
        return v
    
    @field_validator('deal_type')
    @classmethod
    def validate_deal_type(cls, v: str) -> str:
        if v not in DEAL_TYPES:
            raise ValueError(f"deal_type must be one of: {', '.join(DEAL_TYPES)}")
        return v
    
    @field_validator('asset_type')
    @classmethod
    def validate_asset_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ASSET_TYPES:
            raise ValueError(f"asset_type must be one of: {', '.join(ASSET_TYPES)}")
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in DEAL_STATUSES:
            raise ValueError(f"status must be one of: {', '.join(DEAL_STATUSES)}")
        return v
    
    @field_validator('stage')
    @classmethod
    def validate_stage(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in DEAL_STAGES:
            raise ValueError(f"stage must be one of: {', '.join(DEAL_STAGES)}")
        return v


class DealUpdate(BaseModel):
    """Schema for updating a deal"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    client_name: Optional[str] = Field(None, max_length=200)
    user_id: Optional[str] = Field(None, description="Owner user UUID", examples=["550e8400-e29b-41d4-a716-446655440000"])
    
    # Deal classification
    deal_type: Optional[str] = None
    asset_type: Optional[str] = None
    
    # Status & Stage
    status: Optional[str] = None
    stage: Optional[str] = None
    
    # Financial targets
    target_price: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2, examples=[10000000.00])
    target_irr: Optional[Decimal] = Field(None, ge=0, le=100, max_digits=5, decimal_places=2, examples=[15.50])
    
    # Dates
    target_close_date: Optional[date] = None
    actual_close_date: Optional[date] = None
    
    # Location & Notes
    market: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    
    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            import uuid
            try:
                uuid.UUID(v)
            except ValueError:
                raise ValueError("user_id must be a valid UUID")
        return v
    
    @field_validator('deal_type')
    @classmethod
    def validate_deal_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in DEAL_TYPES:
            raise ValueError(f"deal_type must be one of: {', '.join(DEAL_TYPES)}")
        return v
    
    @field_validator('asset_type')
    @classmethod
    def validate_asset_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ASSET_TYPES:
            raise ValueError(f"asset_type must be one of: {', '.join(ASSET_TYPES)}")
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in DEAL_STATUSES:
            raise ValueError(f"status must be one of: {', '.join(DEAL_STATUSES)}")
        return v
    
    @field_validator('stage')
    @classmethod
    def validate_stage(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in DEAL_STAGES:
            raise ValueError(f"stage must be one of: {', '.join(DEAL_STAGES)}")
        return v
    
    @field_validator('actual_close_date')
    @classmethod
    def validate_actual_close_date(cls, v: Optional[date], info) -> Optional[date]:
        # actual_close_date should only be set when deal is closed
        return v


class DealData(BaseModel):
    """Schema for deal response data"""
    id: str = Field(..., description="Deal UUID", examples=["550e8400-e29b-41d4-a716-446655440000"])
    name: str
    client_name: Optional[str] = None
    user_id: Optional[str] = Field(None, description="Owner user UUID", examples=["550e8400-e29b-41d4-a716-446655440000"])
    
    # Deal classification
    deal_type: str
    asset_type: Optional[str] = None
    
    # Status & Stage
    status: str
    stage: Optional[str] = None
    
    # Financial targets
    target_price: Optional[Decimal] = Field(None, examples=[10000000.00])
    target_irr: Optional[Decimal] = Field(None, examples=[15.50])
    
    # Dates
    target_close_date: Optional[date] = None
    actual_close_date: Optional[date] = None
    
    # Location & Notes
    market: Optional[str] = None
    description: Optional[str] = None
    
    # Timestamps
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
