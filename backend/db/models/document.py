"""
Document Model
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Document(SQLModel, table=True):
    """Uploaded document database model"""
    __tablename__ = "documents"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    deal_id: int = Field(index=True)
    filename: str
    file_type: str  # pdf, xlsx, etc.
    s3_path: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
