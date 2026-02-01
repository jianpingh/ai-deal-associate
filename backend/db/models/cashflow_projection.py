"""
Cashflow Projection Model
"""

from typing import Optional
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field


class CashflowProjection(SQLModel, table=True):
    """Annual cashflow projection database model"""
    __tablename__ = "cashflow_projections"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    model_id: int = Field(index=True)  # FK → financial_models
    
    # Period
    year: int  # 0 = acquisition, 1-N = operating years
    is_exit_year: bool = Field(default=False)
    
    # Revenue
    gross_potential_rent: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    vacancy_loss: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    other_income: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    effective_gross_income: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    
    # Expenses
    operating_expenses: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    
    # NOI
    noi: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    
    # Capital
    capex: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    capex_reserve: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    
    # Debt Service
    interest_payment: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    principal_payment: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    total_debt_service: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    
    # Cash Flow
    cash_flow_before_debt: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    cash_flow_after_debt: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    
    # Exit (for exit year only)
    exit_price: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    selling_costs: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    loan_payoff: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    net_sale_proceeds: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    
    # Total Cash Flow (including exit)
    total_cash_flow: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    cumulative_cash_flow: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    
    # Metrics
    cash_on_cash: Optional[Decimal] = Field(default=None, max_digits=8, decimal_places=4)
    dscr: Optional[Decimal] = Field(default=None, max_digits=6, decimal_places=2)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
