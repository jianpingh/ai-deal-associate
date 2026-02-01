"""
Scenario Model
"""

from typing import Optional
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON


class Scenario(SQLModel, table=True):
    """Scenario analysis database model"""
    __tablename__ = "scenarios"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    deal_id: int = Field(index=True)
    base_model_id: int = Field(index=True)  # FK → financial_models
    scenario_name: str
    scenario_type: str = Field(default="custom")  # upside, downside, stress, custom
    description: Optional[str] = None
    
    # Parameter changes from base case
    parameter_changes: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    # Example: {"exit_cap_rate": 5.5, "rent_growth_rate": 3.0}
    
    # Results
    irr: Optional[Decimal] = Field(default=None, max_digits=8, decimal_places=4)
    equity_multiple: Optional[Decimal] = Field(default=None, max_digits=6, decimal_places=2)
    npv: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    
    # IRR change from base
    irr_delta: Optional[Decimal] = Field(default=None, max_digits=8, decimal_places=4)
    
    # Full results
    results: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
