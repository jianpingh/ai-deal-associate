"""
Assets API Routes

RESTful endpoints for Asset management.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from api.deps import get_db
from services import AssetService
from schemas import (
    Response, ErrorCode,
    AssetCreate, AssetUpdate, AssetData,
    AssetResponse, AssetListResponse
)


router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=AssetListResponse, summary="Get all assets")
def list_assets(
    deal_id: Optional[int] = Query(None, description="Filter by deal ID"),
    asset_type: Optional[str] = Query(None, description="Filter by asset type"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Max items to return"),
    db: Session = Depends(get_db)
):
    """
    Get all assets with optional filtering and pagination.
    
    - **deal_id**: Filter assets by deal ID
    - **asset_type**: Filter by asset type (office, retail, industrial, multifamily)
    - **offset**: Skip N items for pagination
    - **limit**: Maximum number of items to return
    """
    service = AssetService(db)
    
    if deal_id:
        assets = service.get_assets_by_deal(deal_id)
    elif asset_type:
        assets = service.get_assets_by_type(asset_type, offset=offset, limit=limit)
    else:
        assets = service.get_assets(offset=offset, limit=limit)
    
    asset_data_list = [
        AssetData(
            id=asset.id,
            deal_id=asset.deal_id,
            name=asset.name,
            asset_type=asset.asset_type,
            address=asset.address,
            city=asset.city,
            state=asset.state,
            valuation=asset.valuation,
            created_at=asset.created_at
        )
        for asset in assets
    ]
    
    return Response[list[AssetData]](
        code=ErrorCode.SUCCESS,
        msg="Assets retrieved successfully",
        data=asset_data_list
    )


@router.get("/{asset_id}", response_model=AssetResponse, summary="Get an asset by ID")
def get_asset(
    asset_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific asset by its ID.
    
    - **asset_id**: The ID of the asset to retrieve
    """
    service = AssetService(db)
    asset = service.get_asset(asset_id)
    
    if not asset:
        return Response[None](
            code=ErrorCode.NOT_FOUND,
            msg=f"Asset with id {asset_id} not found",
            data=None
        )
    
    asset_data = AssetData(
        id=asset.id,
        deal_id=asset.deal_id,
        name=asset.name,
        asset_type=asset.asset_type,
        address=asset.address,
        city=asset.city,
        state=asset.state,
        valuation=asset.valuation,
        created_at=asset.created_at
    )
    
    return Response[AssetData](
        code=ErrorCode.SUCCESS,
        msg="Asset retrieved successfully",
        data=asset_data
    )


@router.post("", response_model=AssetResponse, summary="Create a new asset")
def create_asset(
    data: AssetCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new asset.
    
    - **deal_id**: ID of the associated deal (required)
    - **name**: Name of the asset (required)
    - **asset_type**: Type of asset (optional)
    - **address, city, state**: Location info (optional)
    - **valuation**: Asset valuation (optional)
    """
    service = AssetService(db)
    asset = service.create_asset(data)
    
    asset_data = AssetData(
        id=asset.id,
        deal_id=asset.deal_id,
        name=asset.name,
        asset_type=asset.asset_type,
        address=asset.address,
        city=asset.city,
        state=asset.state,
        valuation=asset.valuation,
        created_at=asset.created_at
    )
    
    return Response[AssetData](
        code=ErrorCode.SUCCESS,
        msg="Asset created successfully",
        data=asset_data
    )


@router.put("/{asset_id}", response_model=AssetResponse, summary="Update an asset")
def update_asset(
    asset_id: int,
    data: AssetUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing asset.
    
    - **asset_id**: The ID of the asset to update
    - Only provided fields will be updated
    """
    service = AssetService(db)
    asset = service.update_asset(asset_id, data)
    
    if not asset:
        return Response[None](
            code=ErrorCode.NOT_FOUND,
            msg=f"Asset with id {asset_id} not found",
            data=None
        )
    
    asset_data = AssetData(
        id=asset.id,
        deal_id=asset.deal_id,
        name=asset.name,
        asset_type=asset.asset_type,
        address=asset.address,
        city=asset.city,
        state=asset.state,
        valuation=asset.valuation,
        created_at=asset.created_at
    )
    
    return Response[AssetData](
        code=ErrorCode.SUCCESS,
        msg="Asset updated successfully",
        data=asset_data
    )


@router.delete("/{asset_id}", response_model=Response, summary="Delete an asset")
def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an asset by its ID.
    
    - **asset_id**: The ID of the asset to delete
    """
    service = AssetService(db)
    success = service.delete_asset(asset_id)
    
    if not success:
        return Response[None](
            code=ErrorCode.NOT_FOUND,
            msg=f"Asset with id {asset_id} not found",
            data=None
        )
    
    return Response[None](
        code=ErrorCode.SUCCESS,
        msg="Asset deleted successfully",
        data=None
    )
