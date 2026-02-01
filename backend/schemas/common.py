"""
Common Schemas

Shared Pydantic models for common API responses.
"""

from typing import List, Any
from pydantic import BaseModel
from .base import Response


class MessageData(BaseModel):
    """Simple message data"""
    message: str


class HealthData(BaseModel):
    """Health check data"""
    status: str


class ValidationErrorItem(BaseModel):
    """Single validation error detail"""
    loc: List[Any]  # Location of the error (field path)
    msg: str        # Error message
    type: str       # Error type


# Concrete response types
class MessageResponse(Response[MessageData]):
    """Response with message data"""
    pass


class HealthResponse(Response[HealthData]):
    """Response with health check data"""
    pass


class ValidationErrorResponse(Response[List[ValidationErrorItem]]):
    """Response for validation errors (replaces FastAPI default 422)"""
    pass
