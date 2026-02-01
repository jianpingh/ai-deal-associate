"""
Deals API Routes

RESTful endpoints for Deal management.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from api.deps import get_db
from services import DealService
from schemas import (
    Response, ErrorCode,
    DealCreate, DealUpdate, DealData,
    DealResponse, DealListResponse
)


router = APIRouter(prefix="/deals", tags=["deals"])


@router.get("", response_model=DealListResponse, summary="Get all deals")
def list_deals(
    status: Optional[str] = Query(None, description="Filter by status"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Max items to return"),
    db: Session = Depends(get_db)
):
    """
    Get all deals with optional filtering and pagination.
    
    - **status**: Filter deals by status (draft, active, closed)
    - **offset**: Skip N items for pagination
    - **limit**: Maximum number of items to return
    """
    service = DealService(db)
    
    if status:
        deals = service.get_deals_by_status(status, offset=offset, limit=limit)
    else:
        deals = service.get_deals(offset=offset, limit=limit)
    
    deal_data_list = [
        DealData(
            id=deal.id,
            name=deal.name,
            client_name=deal.client_name,
            status=deal.status,
            created_at=deal.created_at,
            updated_at=deal.updated_at
        )
        for deal in deals
    ]
    
    return Response[list[DealData]](
        code=ErrorCode.SUCCESS,
        msg="Deals retrieved successfully",
        data=deal_data_list
    )


@router.get("/{deal_id}", response_model=DealResponse, summary="Get a deal by ID")
def get_deal(
    deal_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific deal by its ID.
    
    - **deal_id**: The ID of the deal to retrieve
    """
    service = DealService(db)
    deal = service.get_deal(deal_id)
    
    if not deal:
        return Response[None](
            code=ErrorCode.NOT_FOUND,
            msg=f"Deal with id {deal_id} not found",
            data=None
        )
    
    deal_data = DealData(
        id=deal.id,
        name=deal.name,
        client_name=deal.client_name,
        status=deal.status,
        created_at=deal.created_at,
        updated_at=deal.updated_at
    )
    
    return Response[DealData](
        code=ErrorCode.SUCCESS,
        msg="Deal retrieved successfully",
        data=deal_data
    )


@router.post("", response_model=DealResponse, summary="Create a new deal")
def create_deal(
    data: DealCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new deal.
    
    - **name**: Name of the deal (required)
    - **client_name**: Name of the client (optional)
    - **status**: Deal status (default: draft)
    """
    service = DealService(db)
    deal = service.create_deal(data)
    
    deal_data = DealData(
        id=deal.id,
        name=deal.name,
        client_name=deal.client_name,
        status=deal.status,
        created_at=deal.created_at,
        updated_at=deal.updated_at
    )
    
    return Response[DealData](
        code=ErrorCode.SUCCESS,
        msg="Deal created successfully",
        data=deal_data
    )


@router.put("/{deal_id}", response_model=DealResponse, summary="Update a deal")
def update_deal(
    deal_id: int,
    data: DealUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing deal.
    
    - **deal_id**: The ID of the deal to update
    - Only provided fields will be updated
    """
    service = DealService(db)
    deal = service.update_deal(deal_id, data)
    
    if not deal:
        return Response[None](
            code=ErrorCode.NOT_FOUND,
            msg=f"Deal with id {deal_id} not found",
            data=None
        )
    
    deal_data = DealData(
        id=deal.id,
        name=deal.name,
        client_name=deal.client_name,
        status=deal.status,
        created_at=deal.created_at,
        updated_at=deal.updated_at
    )
    
    return Response[DealData](
        code=ErrorCode.SUCCESS,
        msg="Deal updated successfully",
        data=deal_data
    )


@router.delete("/{deal_id}", response_model=Response, summary="Delete a deal")
def delete_deal(
    deal_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a deal by its ID.
    
    - **deal_id**: The ID of the deal to delete
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
