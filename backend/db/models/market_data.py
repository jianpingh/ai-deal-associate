"""
Market Data Model
"""

from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON


class MarketData(SQLModel, table=True):
    """Market data database model"""
    __tablename__ = "market_data"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    deal_id: int = Field(index=True)
    
    # Location
    market: Optional[str] = None  # e.g., "Dallas-Fort Worth"
    submarket: Optional[str] = None  # e.g., "Uptown Dallas"
    
    # Data type and value
    data_type: str  # rent_growth, cap_rate, vacancy, rent_psf, absorption
    value: Decimal = Field(max_digits=10, decimal_places=4)
    unit: Optional[str] = None  # %, $/SF, units
    
    # Time period
    effective_date: date
    period: Optional[str] = None  # Q1 2025, 2024, etc.
    
    # Asset type specific
    asset_type: Optional[str] = None  # Multifamily, Office, etc.
    property_class: Optional[str] = None  # A, B, C
    
    # Source
    source: Optional[str] = None  # CoStar, CBRE, Marcus & Millichap, Manual
    source_report: Optional[str] = None  # Report name/link
    
    # Additional context
    notes: Optional[str] = None
    raw_data: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
