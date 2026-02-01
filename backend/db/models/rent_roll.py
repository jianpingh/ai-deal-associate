"""
Rent Roll Model
"""

from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from sqlmodel import SQLModel, Field


class RentRoll(SQLModel, table=True):
    """Rent roll detail database model"""
    __tablename__ = "rent_rolls"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    asset_id: int = Field(index=True)
    
    # Unit Info
    unit_number: str
    unit_type: Optional[str] = None  # Studio, 1BR, 2BR, 3BR, etc.
    floor: Optional[int] = None
    square_feet: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    bedrooms: Optional[int] = None
    bathrooms: Optional[Decimal] = Field(default=None, max_digits=3, decimal_places=1)
    
    # Rent Info
    market_rent: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    current_rent: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    rent_per_sf: Optional[Decimal] = Field(default=None, max_digits=8, decimal_places=2)
    concessions: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    
    # Lease Info
    tenant_name: Optional[str] = None
    lease_start: Optional[date] = None
    lease_end: Optional[date] = None
    move_in_date: Optional[date] = None
    
    # Status
    status: str = Field(default="occupied")  # occupied, vacant, notice, down
    is_mtm: bool = Field(default=False)  # Month-to-month
    
    # Other income
    other_income: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    
    # Source document
    source_doc_id: Optional[int] = None  # FK → documents
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
