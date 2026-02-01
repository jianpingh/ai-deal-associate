"""
Deal Team Model
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON


class DealTeam(SQLModel, table=True):
    """Deal team member database model"""
    __tablename__ = "deal_team"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    deal_id: int = Field(index=True)
    user_id: int = Field(index=True)
    
    # Role in deal
    role: str = Field(default="analyst")  # lead, co-lead, analyst, reviewer, viewer
    
    # Permissions
    can_edit: bool = Field(default=True)
    can_approve: bool = Field(default=False)
    can_export: bool = Field(default=True)
    can_delete: bool = Field(default=False)
    permissions: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
    # Status
    is_active: bool = Field(default=True)
    
    added_at: datetime = Field(default_factory=datetime.utcnow)
    added_by: Optional[int] = None  # FK → users
