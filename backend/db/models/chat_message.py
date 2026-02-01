"""
Chat Message Model
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON


class ChatMessage(SQLModel, table=True):
    """Chat message database model"""
    __tablename__ = "chat_messages"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    thread_id: int = Field(index=True)  # FK → chat_threads
    
    # Message info
    role: str  # user, assistant, system, tool
    content: str
    
    # For assistant messages with function calls
    name: Optional[str] = None  # Tool/function name
    tool_call_id: Optional[str] = None
    
    # Message type
    message_type: str = Field(default="text")  # text, tool_call, tool_result, error
    
    # Extra data (renamed from metadata - reserved word)
    extra_data: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    # Example: {"tokens": 150, "model": "gpt-4o", "latency_ms": 1200}
    
    # For tool calls
    tool_calls: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    # Example: [{"id": "call_xxx", "function": {"name": "search_comps", "arguments": "{...}"}}]
    
    # Attachments
    attachments: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    # Example: [{"type": "file", "filename": "rent_roll.pdf", "s3_path": "..."}]
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
