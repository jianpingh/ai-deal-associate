"""
Asset Model
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Asset(SQLModel, table=True):
    """Real estate asset database model"""
    __tablename__ = "assets"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    deal_id: int = Field(index=True)
    name: str
    asset_type: str  # e.g., Multifamily, Retail, Office
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    valuation: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
