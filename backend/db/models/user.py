"""
User Model
"""

import uuid
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """User database model"""
    __tablename__ = "users"
    
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), 
        primary_key=True,
        description="UUID primary key"
    )
    email: str = Field(unique=True, index=True)
    name: str
    password_hash: Optional[str] = None  # For future auth
    role: str = Field(default="analyst")  # admin, manager, analyst
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
