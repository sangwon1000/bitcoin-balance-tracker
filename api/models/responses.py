"""
Standardized response models for the API
"""

from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime


def get_current_timestamp() -> str:
    """Get current timestamp as ISO format string"""
    return datetime.utcnow().isoformat()


class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = Field(True, description="Request success status")
    message: str = Field(..., description="Human-readable message")
    data: Any = Field(..., description="Response data")
    timestamp: str = Field(default_factory=get_current_timestamp, description="Response timestamp")


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = Field(False, description="Request success status")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Any] = Field(None, description="Additional error details")
    timestamp: str = Field(default_factory=get_current_timestamp, description="Response timestamp")


class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    success: bool = Field(False, description="Request success status")
    error: str = Field("validation_error", description="Error type")
    message: str = Field(..., description="Human-readable error message")
    validation_errors: list = Field(..., description="Detailed validation errors")
    timestamp: str = Field(default_factory=get_current_timestamp, description="Response timestamp") 