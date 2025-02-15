from typing import Any, Dict, Optional
from fastapi import status

class ErrorCode:
    """Error codes enum-like class."""
    UNAUTHORIZED = "UNAUTHORIZED"
    NOT_FOUND = "NOT_FOUND"
    INTEGRATION_ERROR = "INTEGRATION_ERROR"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"

class AppError(Exception):
    """Base error class that wraps exceptions with additional context."""
    def __init__(
            self,
            message: str,
            code: str,
            status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
            cause: Optional[Exception] = None,
            context: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.cause = cause
        self.context = context or {}
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API response."""
        return {
            "code": self.code,
            "message": self.message,
            "context": self.context,
            "cause": str(self.cause) if self.cause else None
        }

class NotFoundError(AppError):
    """Resource not found error."""
    def __init__(
            self,
            message: str,
            cause: Optional[Exception] = None,
            context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
            cause=cause,
            context=context
        )

class IntegrationError(AppError):
    """Third-party integration error."""
    def __init__(
            self,
            message: str,
            cause: Optional[Exception] = None,
            context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.INTEGRATION_ERROR,
            status_code=status.HTTP_502_BAD_GATEWAY,
            cause=cause,
            context=context
        )