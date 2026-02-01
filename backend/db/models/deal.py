"""
Deal Model
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Deal(SQLModel, table=True):
    """Deal/Project database model"""
    __tablename__ = "deals"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    client_name: Optional[str] = None
    status: str = Field(default="New")  # New, Analysis, Closed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
