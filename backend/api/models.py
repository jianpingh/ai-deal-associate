from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class Deal(SQLModel, table=True):
    __tablename__ = "deals"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    client_name: Optional[str] = None
    status: str = Field(default="New")  # New, Analysis, Closed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Asset(SQLModel, table=True):
    __tablename__ = "assets"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    # No Foreign Key constraint as requested
    deal_id: int = Field(index=True) 
    name: str
    asset_type: str  # e.g., Multifamily, Retail
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    valuation: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Document(SQLModel, table=True):
    __tablename__ = "documents"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    # No Foreign Key constraint as requested
    deal_id: int = Field(index=True)
    filename: str
    file_type: str  # pdf, xlsxA
    s3_path: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

class Analysis(SQLModel, table=True):
    __tablename__ = "analyses"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    # No Foreign Key constraint as requested
    deal_id: int = Field(index=True)
    analysis_type: str = Field(default="general") # financial, legal, market
    content: str = Field() # Maps to VARCHAR/TEXT in Postgres
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ChatHistory(SQLModel, table=True):
    __tablename__ = "chat_history"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    # No Foreign Key constraint as requested
    deal_id: Optional[int] = Field(default=None, index=True) 
    session_id: str = Field(index=True)
    sender: str  # user, ai
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
