"""
Loan Quote Model
"""

from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON


class LoanQuote(SQLModel, table=True):
    """Loan quote database model"""
    __tablename__ = "loan_quotes"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    deal_id: int = Field(index=True)
    
    # Lender Info
    lender_name: str
    lender_type: Optional[str] = None  # Agency, Bank, CMBS, Life Co, Debt Fund
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    
    # Loan Terms
    loan_amount: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    ltv: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    dscr: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)  # Debt Service Coverage Ratio
    
    # Rate
    rate_type: Optional[str] = None  # Fixed, Floating
    interest_rate: Optional[Decimal] = Field(default=None, max_digits=6, decimal_places=3)
    spread: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=3)  # Over index
    index: Optional[str] = None  # SOFR, Treasury, etc.
    rate_floor: Optional[Decimal] = Field(default=None, max_digits=6, decimal_places=3)
    rate_cap: Optional[Decimal] = Field(default=None, max_digits=6, decimal_places=3)
    
    # Term
    loan_term_years: Optional[int] = None
    amortization_years: Optional[int] = None
    io_period_months: Optional[int] = None  # Interest-only period
    
    # Prepayment
    prepayment_type: Optional[str] = None  # Yield Maintenance, Defeasance, Step-down
    prepayment_terms: Optional[str] = None
    lockout_months: Optional[int] = None
    
    # Fees
    origination_fee_pct: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=3)
    exit_fee_pct: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=3)
    
    # Dates
    quote_date: Optional[date] = None
    expiration_date: Optional[date] = None
    
    # Status
    status: str = Field(default="quoted")  # quoted, term_sheet, approved, selected, declined
    
    # Notes
    notes: Optional[str] = None
    terms_details: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
