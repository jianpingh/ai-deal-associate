"""
Assumption Model
"""

from typing import Optional
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON


class Assumption(SQLModel, table=True):
    """Financial assumptions database model"""
    __tablename__ = "assumptions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    deal_id: int = Field(index=True)
    assumption_set_name: str = Field(default="Base Case")
    is_active: bool = Field(default=True)
    
    # Acquisition
    acquisition_price: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    closing_costs_pct: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    
    # Financing
    loan_amount: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    ltv: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)  # Loan-to-Value %
    interest_rate: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=3)
    loan_term_years: Optional[int] = None
    amortization_years: Optional[int] = None
    io_period_years: Optional[int] = None  # Interest-only period
    
    # Exit
    exit_cap_rate: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    hold_period_years: int = Field(default=5)
    selling_costs_pct: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    
    # Growth Rates
    rent_growth_rate: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    expense_growth_rate: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    vacancy_rate: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    
    # CapEx
    capex_reserve_per_unit: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    capex_reserve_per_sf: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    
    # Custom fields
    custom_assumptions: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
