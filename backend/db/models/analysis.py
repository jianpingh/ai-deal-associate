"""
Analysis Model
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Analysis(SQLModel, table=True):
    """Analysis result database model"""
    __tablename__ = "analyses"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    deal_id: int = Field(index=True)
    analysis_type: str = Field(default="general")  # financial, legal, market
    content: str = Field()  # JSON or text content
    created_at: datetime = Field(default_factory=datetime.utcnow)
