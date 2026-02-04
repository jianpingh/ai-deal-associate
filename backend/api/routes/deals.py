"""
Deals API Routes

RESTful endpoints for Deal management.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, Path
from sqlmodel import Session

from api.deps import get_db
from services import DealService
from schemas import (
    Response, ErrorCode,
    DealCreate, DealUpdate, DealData,
    DealResponse, DealListResponse
)


router = APIRouter(prefix="/deals", tags=["Deals"])


def _deal_to_data(deal) -> DealData:
    """Convert Deal model to DealData schema"""
    return DealData(
        id=deal.id,  # UUID primary key
        name=deal.name,
        client_name=deal.client_name,
        user_id=deal.user_id,  # UUID foreign key
        deal_type=deal.deal_type,
        asset_type=deal.asset_type,
        status=deal.status,
        stage=deal.stage,
        target_price=deal.target_price,
        target_irr=deal.target_irr,
        target_close_date=deal.target_close_date,
        actual_close_date=deal.actual_close_date,
        market=deal.market,
        description=deal.description,
        created_at=deal.created_at,
        updated_at=deal.updated_at
    )


@router.get("", response_model=DealListResponse, summary="Get all deals")
def list_deals(
    status: Optional[str] = Query(None, description="Filter by status (New, Active, On Hold, Closed, Cancelled)"),
    user_id: Optional[str] = Query(None, description="Filter by owner user UUID"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Max items to return"),
    db: Session = Depends(get_db)
):
    """
    Get all deals with optional filtering and pagination.
    
    - **status**: Filter deals by status (New, Active, On Hold, Closed, Cancelled)
    - **user_id**: Filter deals by owner user UUID
    - **offset**: Skip N items for pagination
    - **limit**: Maximum number of items to return
    """
    service = DealService(db)
    
    if user_id:
        deals = service.get_deals_by_user(user_id, offset=offset, limit=limit)
    elif status:
        deals = service.get_deals_by_status(status, offset=offset, limit=limit)
    else:
        deals = service.get_deals(offset=offset, limit=limit)
    
    deal_data_list = [_deal_to_data(deal) for deal in deals]
    
    return Response[list[DealData]](
        code=ErrorCode.SUCCESS,
        msg="Deals retrieved successfully",
        data=deal_data_list
    )


@router.get("/{deal_id}", response_model=DealResponse, summary="Get a deal by ID")
def get_deal(
    deal_id: str = Path(..., description="Deal UUID"),
    db: Session = Depends(get_db)
):
    """
    Get a specific deal by its UUID.
    
    - **deal_id**: The UUID of the deal to retrieve
    """
    service = DealService(db)
    deal = service.get_deal(deal_id)
    
    if not deal:
        return Response[None](
            code=ErrorCode.NOT_FOUND,
            msg=f"Deal with id {deal_id} not found",
            data=None
        )
    
    return Response[DealData](
        code=ErrorCode.SUCCESS,
        msg="Deal retrieved successfully",
        data=_deal_to_data(deal)
    )


@router.post("", response_model=DealResponse, summary="Create a new deal")
def create_deal(
    data: DealCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new deal.
    
    - **name**: Name of the deal (required, 1-200 characters)
    - **deal_type**: Type of deal - Acquisition, Disposition, Refinance (default: Acquisition)
    - **asset_type**: Type of asset - Multifamily, Office, Retail, Industrial, Logistics, Mixed-Use, Other
    - **client_name**: Name of the client (optional, max 200 characters)
    - **user_id**: Owner user UUID (optional)
    - **status**: Deal status - New, Active, On Hold, Closed, Cancelled (default: New)
    - **stage**: Deal stage - Sourcing, Due Diligence, LOI, Under Contract, Closing
    - **target_price**: Target acquisition/sale price (>=0)
    - **target_irr**: Target IRR percentage (0-100)
    - **target_close_date**: Expected closing date
    - **market**: Market/location (e.g., "Dallas-Fort Worth", max 100 characters)
    - **description**: Deal notes/description (max 2000 characters)
    """
    service = DealService(db)
    deal = service.create_deal(data)
    
    return Response[DealData](
        code=ErrorCode.SUCCESS,
        msg="Deal created successfully",
        data=_deal_to_data(deal)
    )


@router.put("/{deal_id}", response_model=DealResponse, summary="Update a deal")
def update_deal(
    deal_id: str = Path(..., description="Deal UUID"),
    data: DealUpdate = None,
    db: Session = Depends(get_db)
):
    """
    Update an existing deal.
    
    - **deal_id**: The UUID of the deal to update
    - Only provided fields will be updated
    - All fields have the same validation as create
    """
    service = DealService(db)
    deal = service.update_deal(deal_id, data)
    
    if not deal:
        return Response[None](
            code=ErrorCode.NOT_FOUND,
            msg=f"Deal with id {deal_id} not found",
            data=None
        )
    
    return Response[DealData](
        code=ErrorCode.SUCCESS,
        msg="Deal updated successfully",
        data=_deal_to_data(deal)
    )


@router.delete("/{deal_id}", response_model=Response, summary="Delete a deal")
def delete_deal(
    deal_id: str = Path(..., description="Deal UUID"),
    db: Session = Depends(get_db)
):
    """
    Delete a deal by its UUID.
    
    - **deal_id**: The UUID of the deal to delete
    
    Note: This will also cascade delete related assets, documents, etc.
    """
    service = DealService(db)
    success = service.delete_deal(deal_id)
    
    if not success:
        return Response[None](
            code=ErrorCode.NOT_FOUND,
            msg=f"Deal with id {deal_id} not found",
            data=None
        )
    
    return Response[None](
        code=ErrorCode.SUCCESS,
        msg="Deal deleted successfully",
        data=None
    )
