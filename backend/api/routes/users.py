"""
Users API Routes

RESTful endpoints for User management.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from api.deps import get_db
from services.user_service import UserService
from schemas.base import Response, ErrorCode
from schemas.user import (
    UserCreate, UserUpdate, UserData,
    UserResponse, UserListResponse
)


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=UserListResponse, summary="Get all users")
def list_users(
    role: Optional[str] = Query(None, description="Filter by role (admin/manager/analyst)"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Max items to return"),
    db: Session = Depends(get_db)
):
    """
    Get all users with optional filtering and pagination.
    
    - **role**: Filter users by role
    - **offset**: Skip N items for pagination
    - **limit**: Maximum number of items to return
    """
    service = UserService(db)
    
    if role:
        users = service.get_users_by_role(role, offset=offset, limit=limit)
    else:
        users = service.get_users(offset=offset, limit=limit)
    
    user_data_list = [
        UserData(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        for user in users
    ]
    
    return Response[list[UserData]](
        code=ErrorCode.SUCCESS,
        msg="Users retrieved successfully",
        data=user_data_list
    )


@router.get("/{user_id}", response_model=UserResponse, summary="Get a user by ID")
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific user by their ID.
    
    - **user_id**: The ID of the user to retrieve
    """
    service = UserService(db)
    user = service.get_user(user_id)
    
    if not user:
        return Response[None](
            code=ErrorCode.NOT_FOUND,
            msg=f"User with id {user_id} not found",
            data=None
        )
    
    user_data = UserData(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )
    
    return Response[UserData](
        code=ErrorCode.SUCCESS,
        msg="User retrieved successfully",
        data=user_data
    )


@router.post("", response_model=UserResponse, summary="Create a new user")
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new user.
    
    - **email**: User's email address (required, must be unique)
    - **name**: User's full name (required)
    - **password**: User's password (optional)
    - **role**: User's role - admin, manager, or analyst (default: analyst)
    """
    service = UserService(db)
    user, error = service.create_user(data)
    
    if error:
        return Response[None](
            code=ErrorCode.CONFLICT,
            msg=error,
            data=None
        )
    
    user_data = UserData(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )
    
    return Response[UserData](
        code=ErrorCode.SUCCESS,
        msg="User created successfully",
        data=user_data
    )


@router.put("/{user_id}", response_model=UserResponse, summary="Update a user")
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing user.
    
    - **user_id**: The ID of the user to update
    - Only provided fields will be updated
    """
    service = UserService(db)
    user, error = service.update_user(user_id, data)
    
    if error:
        code = ErrorCode.NOT_FOUND if "not found" in error.lower() else ErrorCode.CONFLICT
        return Response[None](
            code=code,
            msg=error,
            data=None
        )
    
    user_data = UserData(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )
    
    return Response[UserData](
        code=ErrorCode.SUCCESS,
        msg="User updated successfully",
        data=user_data
    )


@router.delete("/{user_id}", response_model=Response, summary="Delete a user")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a user by their ID.
    
    - **user_id**: The ID of the user to delete
    """
    service = UserService(db)
    success = service.delete_user(user_id)
    
    if not success:
        return Response[None](
            code=ErrorCode.NOT_FOUND,
            msg=f"User with id {user_id} not found",
            data=None
        )
    
    return Response[None](
        code=ErrorCode.SUCCESS,
        msg="User deleted successfully",
        data=None
    )


@router.post("/{user_id}/deactivate", response_model=UserResponse, summary="Deactivate a user")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Soft delete - deactivate a user instead of deleting.
    
    - **user_id**: The ID of the user to deactivate
    """
    service = UserService(db)
    user = service.deactivate_user(user_id)
    
    if not user:
        return Response[None](
            code=ErrorCode.NOT_FOUND,
            msg=f"User with id {user_id} not found",
            data=None
        )
    
    user_data = UserData(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )
    
    return Response[UserData](
        code=ErrorCode.SUCCESS,
        msg="User deactivated successfully",
        data=user_data
    )
