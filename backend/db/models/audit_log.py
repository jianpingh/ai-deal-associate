"""
Audit Log Model
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON


class AuditLog(SQLModel, table=True):
    """Audit log database model"""
    __tablename__ = "audit_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Who
    user_id: Optional[int] = Field(default=None, index=True)
    user_email: Optional[str] = None  # Denormalized for convenience
    
    # What
    action: str  # create, update, delete, export, view, login, logout
    entity_type: str  # deal, model, deck, document, assumption, etc.
    entity_id: Optional[int] = None
    entity_name: Optional[str] = None  # Denormalized for readability
    
    # Context
    deal_id: Optional[int] = Field(default=None, index=True)
    
    # Changes (for update actions)
    old_value: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    new_value: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    changes_summary: Optional[str] = None  # Human-readable summary
    
    # Request info
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
