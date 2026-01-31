"""
Unified API Response Schemas

Provides standardized response format for business APIs.
LangGraph proxy endpoints should NOT use these wrappers.
"""

from typing import TypeVar, Generic, Optional, Any, List
from pydantic import BaseModel
from datetime import datetime

T = TypeVar('T')


class Response(BaseModel, Generic[T]):
    """
    Unified API response format.
    
    Example:
        {
            "code": 0,
            "msg": "success",
            "data": {...}
        }
    """
    code: int = 0
    msg: str = "success"
    data: Optional[T] = None

    @classmethod
    def success(cls, data: T = None, msg: str = "success") -> "Response[T]":
        """Create a success response"""
        return cls(code=0, msg=msg, data=data)
    
    @classmethod
    def error(cls, code: int = -1, msg: str = "error", data: T = None) -> "Response[T]":
        """Create an error response"""
        return cls(code=code, msg=msg, data=data)


class PagedData(BaseModel, Generic[T]):
    """Paged data wrapper for list responses"""
    items: List[T]
    total: int
    offset: int = 0
    limit: int = 100


class ErrorCode:
    """Standard error codes"""
    SUCCESS = 0
    PARAM_ERROR = 400        # Invalid parameters
    UNAUTHORIZED = 401       # Authentication required
    FORBIDDEN = 403          # Access denied
    NOT_FOUND = 404          # Resource not found
    CONFLICT = 409           # Resource conflict
    SERVER_ERROR = 500       # Internal server error
    DB_ERROR = 501           # Database error
    EXTERNAL_API_ERROR = 502 # External API error
    SERVICE_UNAVAILABLE = 503 # Service unavailable


# ============================================================
# Specific Response Data Models for Swagger Documentation
# ============================================================

class MessageData(BaseModel):
    """Simple message data"""
    message: str


class HealthData(BaseModel):
    """Health check data"""
    status: str


class DealData(BaseModel):
    """Deal data model"""
    id: Optional[int] = None
    name: str
    client_name: Optional[str] = None
    status: str = "New"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AssetData(BaseModel):
    """Asset data model"""
    id: Optional[int] = None
    deal_id: int
    name: str
    asset_type: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    valuation: Optional[float] = None
    created_at: Optional[datetime] = None


# Concrete response types for Swagger documentation
class MessageResponse(Response[MessageData]):
    """Response with message data"""
    pass


class HealthResponse(Response[HealthData]):
    """Response with health check data"""
    pass


class DealResponse(Response[DealData]):
    """Response with single deal"""
    pass


class DealListResponse(Response[List[DealData]]):
    """Response with list of deals"""
    pass


class AssetResponse(Response[AssetData]):
    """Response with single asset"""
    pass


class AssetListResponse(Response[List[AssetData]]):
    """Response with list of assets"""
    pass


# Validation error detail item
class ValidationErrorItem(BaseModel):
    """Single validation error detail"""
    loc: List[Any]  # Location of the error (field path)
    msg: str        # Error message
    type: str       # Error type


class ValidationErrorResponse(Response[List[ValidationErrorItem]]):
    """Response for validation errors (replaces FastAPI default 422)"""
    pass
