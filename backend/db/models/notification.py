"""
Notification Model
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON


class Notification(SQLModel, table=True):
    """Notification database model"""
    __tablename__ = "notifications"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    deal_id: Optional[int] = Field(default=None, index=True)
    
    # Notification type
    type: str  # model_complete, review_needed, deck_ready, comment, mention, export_ready
    priority: str = Field(default="normal")  # low, normal, high, urgent
    
    # Content
    title: str
    message: str
    
    # Action link
    action_url: Optional[str] = None  # Deep link to relevant page
    action_label: Optional[str] = None  # "View Model", "Review Deck"
    
    # Extra data (renamed from 'metadata' - reserved word in SQLModel)
    extra_data: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    # Example: {"model_id": 123, "irr": 15.5}
    
    # Status
    is_read: bool = Field(default=False)
    read_at: Optional[datetime] = None
    is_dismissed: bool = Field(default=False)
    
    # Source
    triggered_by: Optional[int] = None  # FK → users (who triggered this notification)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
