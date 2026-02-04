"""
Tenant Model
"""

import uuid
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from sqlmodel import SQLModel, Field


class Tenant(SQLModel, table=True):
    """Tenant database model"""
    __tablename__ = "tenants"
    
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), 
        primary_key=True,
        description="UUID primary key"
    )
    deal_id: str = Field(index=True)  # FK → deals.id (UUID)
    asset_id: str = Field(index=True)  # FK → assets.id (UUID)
    name: str
    unit_number: Optional[str] = None
    lease_start: Optional[date] = None
    lease_end: Optional[date] = None
    current_rent: Optional[Decimal] = Field(default=None, max_digits=12, decimal_places=2)
    market_rent: Optional[Decimal] = Field(default=None, max_digits=12, decimal_places=2)
    area_sqft: Optional[Decimal] = Field(default=None, max_digits=12, decimal_places=2)
    rent_per_sqft: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    lease_type: Optional[str] = None  # NNN, Gross, Modified Gross
    status: str = Field(default="active")  # active, expired, pending
    created_at: datetime = Field(default_factory=datetime.utcnow)
