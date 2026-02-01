"""
Financial Model
"""

from typing import Optional
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON


class FinancialModel(SQLModel, table=True):
    """Financial model results database model"""
    __tablename__ = "financial_models"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    deal_id: int = Field(index=True)
    assumption_id: Optional[int] = Field(default=None, index=True)
    model_name: str = Field(default="Base Case Model")
    status: str = Field(default="draft")  # draft, final, archived
    
    # Output file
    excel_s3_path: Optional[str] = None
    
    # Key Metrics
    irr: Optional[Decimal] = Field(default=None, max_digits=8, decimal_places=4)  # Internal Rate of Return
    equity_multiple: Optional[Decimal] = Field(default=None, max_digits=6, decimal_places=2)
    npv: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)  # Net Present Value
    cash_on_cash_y1: Optional[Decimal] = Field(default=None, max_digits=8, decimal_places=4)  # Year 1 CoC
    avg_cash_on_cash: Optional[Decimal] = Field(default=None, max_digits=8, decimal_places=4)
    
    # Investment Summary
    total_equity: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    total_debt: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    total_investment: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    
    # Exit Summary
    exit_price: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    profit: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    
    # Detailed data
    annual_cashflows: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    sensitivity_matrix: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
