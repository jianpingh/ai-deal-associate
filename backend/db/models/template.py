"""
Template Model
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON


class Template(SQLModel, table=True):
    """Template database model"""
    __tablename__ = "templates"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Basic info
    name: str
    description: Optional[str] = None
    type: str  # excel, pptx, assumptions, report
    
    # File location
    s3_path: str
    file_size: Optional[int] = None  # bytes
    
    # Applicability
    asset_type: Optional[str] = None  # Multifamily, Office, Retail, All
    deal_type: Optional[str] = None  # Acquisition, Disposition, All
    
    # Status
    is_default: bool = Field(default=False)
    is_active: bool = Field(default=True)
    version: str = Field(default="1.0")
    
    # Configuration
    config: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    # Example for Excel: {"input_sheet": "Inputs", "output_cells": {"irr": "B15"}}
    # Example for PPT: {"slides": ["Cover", "Summary", "Financials"]}
    
    # Ownership
    created_by: Optional[int] = None  # FK → users
    is_system: bool = Field(default=False)  # System-provided vs user-uploaded
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
