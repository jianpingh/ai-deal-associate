"""
Chat History Model
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class ChatHistory(SQLModel, table=True):
    """Chat history database model"""
    __tablename__ = "chat_history"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    deal_id: Optional[int] = Field(default=None, index=True)
    session_id: str = Field(index=True)
    sender: str  # user, assistant
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
