"""
Custom exceptions and error handlers
"""
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic_core import ValidationError
import logging

logger = logging.getLogger(__name__)


class ALIAException(Exception):
    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ValidationException(ALIAException):
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class NotFoundException(ALIAException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, "NOT_FOUND")


class UnauthorizedException(ALIAException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, "UNAUTHORIZED")


class ForbiddenException(ALIAException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, "FORBIDDEN")


class RateLimitException(ALIAException):
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, "RATE_LIMIT_EXCEEDED")


async def alia_exception_handler(request: Request, exc: ALIAException):
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": None
            }
        }
    )


async def http_exception_handler(request: Request, exc: Exception):
    # Handle different types of exceptions
    if isinstance(exc, StarletteHTTPException):
        error_codes = {
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            422: "VALIDATION_ERROR",
            429: "RATE_LIMIT_EXCEEDED",
            500: "INTERNAL_ERROR"
        }
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": error_codes.get(exc.status_code, "UNKNOWN_ERROR"),
                    "message": exc.detail,
                    "details": None
                }
            }
        )
    elif isinstance(exc, ValidationError):
        # Handle Pydantic validation errors
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Data validation failed",
                    "details": exc.errors()
                }
            }
        )
    else:
        # Handle other exceptions
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An internal error occurred",
                    "details": None
                }
            }
        )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request data",
                "details": exc.errors()
            }
        }
    )