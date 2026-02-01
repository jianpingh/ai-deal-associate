"""
Base Response Schemas

Unified API response format and error codes.
"""

from typing import TypeVar, Generic, Optional, List
from pydantic import BaseModel

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
