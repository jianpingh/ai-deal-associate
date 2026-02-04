"""
Document Model
"""

import uuid
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON


class Document(SQLModel, table=True):
    """Uploaded document database model"""
    __tablename__ = "documents"
    
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), 
        primary_key=True,
        description="UUID primary key"
    )
    deal_id: str = Field(index=True)  # FK → deals.id (UUID)
    asset_id: Optional[str] = Field(default=None, index=True)  # FK → assets.id (UUID)
    
    # File info
    filename: str
    original_filename: Optional[str] = None
    file_type: str  # pdf, xlsx, docx, csv, jpg, png
    file_size: Optional[int] = None  # bytes
    
    # Storage
    s3_path: str
    s3_bucket: Optional[str] = None
    
    # Classification
    doc_category: Optional[str] = None  # OM, Rent Roll, T12, Financials, Photos, Legal, Other
    doc_subcategory: Optional[str] = None
    
    # Processing
    processing_status: str = Field(default="pending")  # pending, processing, completed, failed
    processing_error: Optional[str] = None
    
    # Extracted data
    extracted_data: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    extracted_text: Optional[str] = None  # OCR/parsed text
    page_count: Optional[int] = None
    
    # Metadata
    description: Optional[str] = None
    tags: Optional[dict] = Field(default=None, sa_column=Column(JSON))  # ["rent_roll", "2024"]
    
    # Audit
    uploaded_by: Optional[int] = None  # FK → users
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
