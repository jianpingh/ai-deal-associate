"""
Deal Model
"""

from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from sqlmodel import SQLModel, Field


class Deal(SQLModel, table=True):
    """Deal/Project database model"""
    __tablename__ = "deals"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    
    # Client & Ownership
    client_name: Optional[str] = None
    user_id: Optional[int] = Field(default=None, index=True)  # FK → users (owner)
    
    # Deal classification
    deal_type: str = Field(default="Acquisition")  # Acquisition, Disposition, Refinance
    asset_type: Optional[str] = None  # Multifamily, Office, Retail, Industrial
    
    # Status & Stage
    status: str = Field(default="New")  # New, Active, On Hold, Closed, Cancelled
    stage: Optional[str] = None  # Sourcing, Due Diligence, LOI, Under Contract, Closing
    
    # Financial targets
    target_price: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    target_irr: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    
    # Dates
    target_close_date: Optional[date] = None
    actual_close_date: Optional[date] = None
    
    # Location summary
    market: Optional[str] = None  # e.g., "Dallas-Fort Worth"
    
    # Notes
    description: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
