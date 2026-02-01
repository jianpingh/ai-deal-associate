"""
Chat Thread Model
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON


class ChatThread(SQLModel, table=True):
    """Chat thread database model"""
    __tablename__ = "chat_threads"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    deal_id: Optional[int] = Field(default=None, index=True)
    user_id: Optional[int] = Field(default=None, index=True)
    
    # LangGraph integration
    langgraph_thread_id: str = Field(index=True)  # UUID from LangGraph
    
    # Thread info
    title: Optional[str] = None  # Auto-generated or user-provided
    
    # Status
    status: str = Field(default="active")  # active, archived, deleted
    
    # State snapshot (for quick access without calling LangGraph)
    current_step: Optional[str] = None  # Current workflow step
    state_snapshot: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    
    # Statistics
    message_count: int = Field(default=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_message_at: Optional[datetime] = None
