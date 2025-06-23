from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from enum import Enum
from typing import Any, Dict, Optional
import traceback
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorCode(str, Enum):
    """Standardized error codes for the application."""
    # Authentication & Authorization
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    
    # Validation Errors
    INVALID_INPUT = "INVALID_INPUT"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    MALFORMED_REQUEST = "MALFORMED_REQUEST"
    
    # Business Logic Errors
    CONVERSATION_NOT_FOUND = "CONVERSATION_NOT_FOUND"
    MESSAGE_TOO_LONG = "MESSAGE_TOO_LONG"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    
    # Database Errors
    DATABASE_ERROR = "DATABASE_ERROR"
    RECORD_NOT_FOUND = "RECORD_NOT_FOUND"
    DUPLICATE_RECORD = "DUPLICATE_RECORD"
    
    # External Service Errors
    OPENAI_API_ERROR = "OPENAI_API_ERROR"
    KNOWLEDGE_BASE_ERROR = "KNOWLEDGE_BASE_ERROR"
    INTENT_SERVICE_ERROR = "INTENT_SERVICE_ERROR"
    
    # System Errors
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    DEPENDENCY_ERROR = "DEPENDENCY_ERROR"

class BaseAPIException(Exception):
    """Base exception class for API errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.timestamp = time.time()
        super().__init__(self.message)

class ValidationException(BaseAPIException):
    """Exception for input validation errors."""
    
    def __init__(
        self,
        message: str = "Invalid input provided",
        field_errors: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=422,
            details={"field_errors": field_errors or {}}
        )

class AuthenticationException(BaseAPIException):
    """Exception for authentication errors."""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            error_code=ErrorCode.UNAUTHORIZED,
            status_code=401
        )

class AuthorizationException(BaseAPIException):
    """Exception for authorization errors."""
    
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(
            message=message,
            error_code=ErrorCode.FORBIDDEN,
            status_code=403
        )

class RateLimitException(BaseAPIException):
    """Exception for rate limiting."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None
    ):
        details = {}
        if retry_after:
            details["retry_after"] = retry_after
        
        super().__init__(
            message=message,
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            status_code=429,
            details=details
        )

class DatabaseException(BaseAPIException):
    """Exception for database errors."""
    
    def __init__(
        self,
        message: str = "Database operation failed",
        operation: Optional[str] = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.DATABASE_ERROR,
            status_code=500,
            details={"operation": operation} if operation else {}
        )

class ConversationNotFoundException(BaseAPIException):
    """Exception for conversation not found."""
    
    def __init__(self, conversation_id: str):
        super().__init__(
            message=f"Conversation {conversation_id} not found",
            error_code=ErrorCode.CONVERSATION_NOT_FOUND,
            status_code=404,
            details={"conversation_id": conversation_id}
        )

class ExternalServiceException(BaseAPIException):
    """Exception for external service errors."""
    
    def __init__(
        self,
        service_name: str,
        message: str = "External service error",
        service_error_code: Optional[str] = None
    ):
        super().__init__(
            message=f"{service_name}: {message}",
            error_code=ErrorCode.SERVICE_UNAVAILABLE,
            status_code=503,
            details={
                "service_name": service_name,
                "service_error_code": service_error_code
            }
        )

class OpenAIException(ExternalServiceException):
    """Exception for OpenAI API errors."""
    
    def __init__(
        self,
        message: str = "OpenAI API error",
        api_error_code: Optional[str] = None
    ):
        super().__init__(
            service_name="OpenAI",
            message=message,
            service_error_code=api_error_code
        )
        self.error_code = ErrorCode.OPENAI_API_ERROR

# Error response formatting
class ErrorResponse:
    """Standardized error response format."""
    
    @staticmethod
    def format_error(
        error_code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        timestamp: Optional[float] = None
    ) -> Dict[str, Any]:
        """Format error response in consistent structure."""
        return {
            "error": {
                "code": error_code.value,
                "message": message,
                "details": details or {},
                "timestamp": timestamp or time.time()
            },
            "success": False
        }

# Global exception handlers
async def api_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """Handle custom API exceptions."""
    # Log the exception
    logger.error(
        f"API Exception: {exc.error_code.value} - {exc.message}",
        extra={
            "error_code": exc.error_code.value,
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse.format_error(
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
            timestamp=exc.timestamp
        )
    )

async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle Pydantic validation exceptions."""
    logger.warning(f"Validation error: {str(exc)}", extra={"path": request.url.path})
    
    return JSONResponse(
        status_code=422,
        content=ErrorResponse.format_error(
            error_code=ErrorCode.VALIDATION_ERROR,
            message="Validation failed",
            details={"validation_errors": str(exc)}
        )
    )

async def http_exception_handler_custom(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions with consistent format."""
    logger.warning(
        f"HTTP Exception: {exc.status_code} - {exc.detail}",
        extra={"path": request.url.path, "method": request.method}
    )
    
    # Map HTTP status codes to error codes
    error_code_mapping = {
        400: ErrorCode.MALFORMED_REQUEST,
        401: ErrorCode.UNAUTHORIZED,
        403: ErrorCode.FORBIDDEN,
        404: ErrorCode.RECORD_NOT_FOUND,
        429: ErrorCode.RATE_LIMIT_EXCEEDED,
        500: ErrorCode.INTERNAL_SERVER_ERROR,
        503: ErrorCode.SERVICE_UNAVAILABLE
    }
    
    error_code = error_code_mapping.get(exc.status_code, ErrorCode.INTERNAL_SERVER_ERROR)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse.format_error(
            error_code=error_code,
            message=exc.detail if hasattr(exc, 'detail') else "An error occurred"
        )
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    # Log the full traceback for debugging
    logger.error(
        f"Unexpected error: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc()
        }
    )
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse.format_error(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred"
        )
    )

# Exception raising utilities
class ExceptionRaiser:
    """Utility class for raising common exceptions."""
    
    @staticmethod
    def require_auth(condition: bool, message: str = "Authentication required"):
        """Raise authentication exception if condition is False."""
        if not condition:
            raise AuthenticationException(message)
    
    @staticmethod
    def require_permission(condition: bool, message: str = "Access forbidden"):
        """Raise authorization exception if condition is False."""
        if not condition:
            raise AuthorizationException(message)
    
    @staticmethod
    def validate_input(condition: bool, message: str, field_errors: Optional[Dict[str, str]] = None):
        """Raise validation exception if condition is False."""
        if not condition:
            raise ValidationException(message, field_errors)
    
    @staticmethod
    def check_not_found(obj: Any, identifier: str, resource_type: str = "Resource"):
        """Raise not found exception if object is None."""
        if obj is None:
            raise BaseAPIException(
                message=f"{resource_type} {identifier} not found",
                error_code=ErrorCode.RECORD_NOT_FOUND,
                status_code=404,
                details={"identifier": identifier, "resource_type": resource_type}
            )
    
    @staticmethod
    def check_rate_limit(condition: bool, retry_after: Optional[int] = None):
        """Raise rate limit exception if condition is False."""
        if not condition:
            raise RateLimitException(retry_after=retry_after) 