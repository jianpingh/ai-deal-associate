"""
Comparable Model
"""

from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON


class Comparable(SQLModel, table=True):
    """Comparable transaction database model"""
    __tablename__ = "comps"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    deal_id: int = Field(index=True)
    property_name: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    asset_type: Optional[str] = None  # Multifamily, Office, Retail, Industrial
    sale_price: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    price_per_sf: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    price_per_unit: Optional[Decimal] = Field(default=None, max_digits=12, decimal_places=2)
    cap_rate: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    num_units: Optional[int] = None
    square_feet: Optional[int] = None
    year_built: Optional[int] = None
    transaction_date: Optional[date] = None
    source: Optional[str] = None  # Pinecone, CoStar, Manual
    is_selected: bool = Field(default=True)
    raw_data: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
