"""
Asset Repository

Data access layer for Asset operations.
"""

from typing import List
from sqlmodel import Session, select
from db.models import Asset
from .base import BaseRepository


class AssetRepository(BaseRepository[Asset]):
    """Repository for Asset model operations"""
    
    def __init__(self, session: Session):
        super().__init__(Asset, session)
    
    def get_by_deal_id(self, deal_id: int) -> List[Asset]:
        """Get all assets for a specific deal"""
        statement = select(Asset).where(Asset.deal_id == deal_id)
        return list(self.session.exec(statement).all())
    
    def get_by_type(self, asset_type: str, offset: int = 0, limit: int = 100) -> List[Asset]:
        """Get assets filtered by type"""
        statement = select(Asset).where(Asset.asset_type == asset_type).offset(offset).limit(limit)
        return list(self.session.exec(statement).all())
    
    def get_by_city(self, city: str) -> List[Asset]:
        """Get assets in a specific city"""
        statement = select(Asset).where(Asset.city == city)
        return list(self.session.exec(statement).all())
