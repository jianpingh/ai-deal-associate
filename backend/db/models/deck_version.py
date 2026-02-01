"""
Deck Version Model
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON


class DeckVersion(SQLModel, table=True):
    """Presentation deck version database model"""
    __tablename__ = "deck_versions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    deal_id: int = Field(index=True)
    model_id: Optional[int] = Field(default=None, index=True)  # FK → financial_models
    version_name: str = Field(default="V1")
    version_number: int = Field(default=1)
    
    # Output file
    pptx_s3_path: Optional[str] = None
    pdf_s3_path: Optional[str] = None  # PDF export
    
    status: str = Field(default="draft")  # draft, review, final
    
    # Slide content summary
    slide_count: Optional[int] = None
    slide_contents: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    # Example: {"slides": [{"title": "Executive Summary", "type": "summary"}, ...]}
    
    # Metadata
    created_by: Optional[int] = None  # FK → users
    notes: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
