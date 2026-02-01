"""
Deal Repository

Data access layer for Deal operations.
"""

from typing import List, Optional
from sqlmodel import Session, select
from db.models import Deal
from .base import BaseRepository


class DealRepository(BaseRepository[Deal]):
    """Repository for Deal model operations"""
    
    def __init__(self, session: Session):
        super().__init__(Deal, session)
    
    def get_by_name(self, name: str) -> Optional[Deal]:
        """Find deal by name"""
        statement = select(Deal).where(Deal.name == name)
        return self.session.exec(statement).first()
    
    def get_by_status(self, status: str, offset: int = 0, limit: int = 100) -> List[Deal]:
        """Get deals filtered by status"""
        statement = select(Deal).where(Deal.status == status).offset(offset).limit(limit)
        return list(self.session.exec(statement).all())
    
    def get_by_client(self, client_name: str) -> List[Deal]:
        """Get deals for a specific client"""
        statement = select(Deal).where(Deal.client_name == client_name)
        return list(self.session.exec(statement).all())
