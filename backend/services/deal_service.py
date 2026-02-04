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
            user_id=data.user_id,  # UUID string directly
            deal_type=data.deal_type,
            asset_type=data.asset_type,
            status=data.status,
            stage=data.stage,
            target_price=data.target_price,
            target_irr=data.target_irr,
            target_close_date=data.target_close_date,
            market=data.market,
            description=data.description,
        )
        return self.repo.create(deal)
    
    def get_deal(self, deal_id: str) -> Optional[Deal]:
        """Get a deal by UUID"""
        return self.repo.get_by_id(deal_id)
    
    def get_deals(self, offset: int = 0, limit: int = 100) -> List[Deal]:
        """Get all deals with pagination"""
        return self.repo.get_all(offset=offset, limit=limit)
    
    def get_deals_by_status(self, status: str, offset: int = 0, limit: int = 100) -> List[Deal]:
        """Get deals filtered by status"""
        return self.repo.get_by_status(status, offset=offset, limit=limit)
    
    def get_deals_by_user(self, user_id: str, offset: int = 0, limit: int = 100) -> List[Deal]:
        """Get deals for a specific user by UUID"""
        return self.repo.get_by_user(user_id, offset=offset, limit=limit)
    
    def update_deal(self, deal_id: str, data: DealUpdate) -> Optional[Deal]:
        """Update a deal by UUID"""
        deal = self.repo.get_by_id(deal_id)
        if not deal:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        return self.repo.update(deal, update_data)
    
    def delete_deal(self, deal_id: str) -> bool:
        """Delete a deal by UUID"""
        deal = self.repo.get_by_id(deal_id)
        if not deal:
            return False
        return self.repo.delete(deal)
    
    def count_deals(self) -> int:
        """Get total count of deals"""
        return self.repo.count()
