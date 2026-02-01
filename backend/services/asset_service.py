"""
Asset Service

Business logic layer for Asset operations.
"""

from typing import List, Optional
from sqlmodel import Session
from db.models import Asset
from repos import AssetRepository
from schemas import AssetCreate, AssetUpdate


class AssetService:
    """Service class for Asset business logic"""
    
    def __init__(self, session: Session):
        self.session = session
        self.repo = AssetRepository(session)
    
    def create_asset(self, data: AssetCreate) -> Asset:
        """Create a new asset"""
        asset = Asset(
            deal_id=data.deal_id,
            name=data.name,
            asset_type=data.asset_type,
            address=data.address,
            city=data.city,
            state=data.state,
            valuation=data.valuation,
        )
        return self.repo.create(asset)
    
    def get_asset(self, asset_id: int) -> Optional[Asset]:
        """Get an asset by ID"""
        return self.repo.get_by_id(asset_id)
    
    def get_assets(self, offset: int = 0, limit: int = 100) -> List[Asset]:
        """Get all assets with pagination"""
        return self.repo.get_all(offset=offset, limit=limit)
    
    def get_assets_by_deal(self, deal_id: int) -> List[Asset]:
        """Get all assets for a specific deal"""
        return self.repo.get_by_deal_id(deal_id)
    
    def get_assets_by_type(self, asset_type: str, offset: int = 0, limit: int = 100) -> List[Asset]:
        """Get assets filtered by type"""
        return self.repo.get_by_type(asset_type, offset=offset, limit=limit)
    
    def update_asset(self, asset_id: int, data: AssetUpdate) -> Optional[Asset]:
        """Update an asset"""
        asset = self.repo.get_byid(asset_id)
        if not asset:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        return self.repo.update(asset, update_data)
    
    def delete_asset(self, asset_id: int) -> bool:
        """Delete an asset"""
        asset = self.repo.get_by_id(asset_id)
        if not asset:
            return False
        return self.repo.delete(asset)
