"""
Schemas Module

Pydantic models for API request/response validation.
"""

from .base import Response, ErrorCode, PagedData
from .deal import (
    DealCreate, DealUpdate, DealData,
    DealResponse, DealListResponse
)
from .asset import (
    AssetCreate, AssetUpdate, AssetData,
    AssetResponse, AssetListResponse
)
from .common import (
    MessageData, MessageResponse,
    HealthData, HealthResponse,
    ValidationErrorItem, ValidationErrorResponse
)

__all__ = [
    # Base
    "Response", "ErrorCode", "PagedData",
    # Deal
    "DealCreate", "DealUpdate", "DealData",
    "DealResponse", "DealListResponse",
    # Asset
    "AssetCreate", "AssetUpdate", "AssetData",
    "AssetResponse", "AssetListResponse",
    # Common
    "MessageData", "MessageResponse",
    "HealthData", "HealthResponse",
    "ValidationErrorItem", "ValidationErrorResponse",
]
