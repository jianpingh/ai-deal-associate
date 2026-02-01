"""
Deal Service

Business logic layer for Deal operations.
"""

from typing import List, Optional
from datetime import datetime
from sqlmodel import Session
from db.models import Deal
from repos import DealRepository
from schemas import DealCreate, DealUpdate, DealData


class DealService:
    """Service class for Deal business logic"""
    
    def __init__(self, session: Session):
        self.session = session
        self.repo = DealRepository(session)
    
    def create_deal(self, data: DealCreate) -> Deal:
        """Create a new deal"""
        deal = Deal(
            name=data.name,
            client_name=data.client_name,
            status=data.status,
        )
        return self.repo.create(deal)
    
    def get_deal(self, deal_id: int) -> Optional[Deal]:
        """Get a deal by ID"""
        return self.repo.get_by_id(deal_id)
    
    def get_deals(self, offset: int = 0, limit: int = 100) -> List[Deal]:
        """Get all deals with pagination"""
        return self.repo.get_all(offset=offset, limit=limit)
    
    def get_deals_by_status(self, status: str, offset: int = 0, limit: int = 100) -> List[Deal]:
        """Get deals filtered by status"""
        return self.repo.get_by_status(status, offset=offset, limit=limit)
    
    def update_deal(self, deal_id: int, data: DealUpdate) -> Optional[Deal]:
        """Update a deal"""
        deal = self.repo.get_by_id(deal_id)
        if not deal:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        return self.repo.update(deal, update_data)
    
    def delete_deal(self, deal_id: int) -> bool:
        """Delete a deal"""
        deal = self.repo.get_by_id(deal_id)
        if not deal:
            return False
        return self.repo.delete(deal)
    
    def count_deals(self) -> int:
        """Get total count of deals"""
        return self.repo.count()
