"""
Asset Model
"""

import uuid
from typing import Optional
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON


class Asset(SQLModel, table=True):
    """Real estate asset database model"""
    __tablename__ = "assets"
    
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), 
        primary_key=True,
        description="UUID primary key"
    )
    deal_id: str = Field(index=True)  # FK → deals.id (UUID)
    
    # Basic info
    name: str
    asset_type: str  # Multifamily, Retail, Office, Industrial, Mixed-Use
    property_class: Optional[str] = None  # A, B, C
    
    # Location
    address: Optional[str] = None
    city: Optional[str] = Field(default=None, index=True)
    state: Optional[str] = Field(default=None, index=True)
    zip_code: Optional[str] = None
    county: Optional[str] = None
    submarket: Optional[str] = None
    
    # Physical characteristics
    year_built: Optional[int] = None
    year_renovated: Optional[int] = None
    num_units: Optional[int] = None
    num_buildings: Optional[int] = None
    num_floors: Optional[int] = None
    square_feet: Optional[Decimal] = Field(default=None, max_digits=12, decimal_places=2)
    land_area_acres: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    parking_spaces: Optional[int] = None
    
    # Unit mix (for Multifamily)
    unit_mix: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    # Example: {"Studio": 10, "1BR": 50, "2BR": 30, "3BR": 10}
    
    # Financial metrics
    current_noi: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    proforma_noi: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    occupancy_rate: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    avg_rent_per_unit: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    avg_rent_per_sf: Optional[Decimal] = Field(default=None, max_digits=8, decimal_places=2)
    
    # Valuation
    valuation: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    price_per_unit: Optional[Decimal] = Field(default=None, max_digits=12, decimal_places=2)
    price_per_sf: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    cap_rate: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    
    # Amenities & features
    amenities: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    # Example: ["Pool", "Gym", "Clubhouse", "Dog Park"]
    
    # Additional details
    property_details: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
