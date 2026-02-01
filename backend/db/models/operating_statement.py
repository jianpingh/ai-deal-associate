"""
Operating Statement Model (T12)
"""

from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON


class OperatingStatement(SQLModel, table=True):
    """Operating statement (T12) database model"""
    __tablename__ = "operating_statements"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    asset_id: int = Field(index=True)
    
    # Period
    period_type: str = Field(default="T12")  # T12, T6, T3, Annual, Monthly
    period_start: date
    period_end: date
    
    # Revenue
    gross_potential_rent: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    loss_to_lease: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    vacancy_loss: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    concessions: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    bad_debt: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    net_rental_income: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    
    # Other Income
    utility_reimbursement: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    parking_income: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    laundry_income: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    pet_fees: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    other_income: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    total_other_income: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    
    effective_gross_income: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    
    # Operating Expenses
    payroll: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    repairs_maintenance: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    utilities: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    insurance: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    real_estate_taxes: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    management_fee: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    marketing: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    admin_general: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    contract_services: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    other_expenses: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    total_operating_expenses: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    
    # NOI
    noi: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    
    # Below the line
    capex: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    debt_service: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    cash_flow: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    
    # Per unit / Per SF metrics
    noi_per_unit: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    noi_per_sf: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    expense_ratio: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    
    # Detailed line items (flexible)
    line_items: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
    # Source
    source_doc_id: Optional[int] = None  # FK → documents
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
