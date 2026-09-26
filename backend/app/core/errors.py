"""Custom Exceptions & Centralized Error Handlers

Ensures uniform, security-safe error envelopes across all endpoints.
"""

from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.logging import logger


class AppBaseException(Exception):
    """Base class for all application-specific exceptions."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class ParsingError(AppBaseException):
    """Raised when an email payload cannot be parsed."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="EMAIL_PARSING_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            details=details,
        )


class AnalysisError(AppBaseException):
    """Raised when an analytical engine fails during triage."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="ANALYSIS_PROCESSING_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class ModelNotLoadedError(AppBaseException):
    """Raised when an ML classifier artifact cannot be located."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="MODEL_ARTIFACT_NOT_FOUND",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details,
        )


class ReportGenerationError(AppBaseException):
    """Raised when PDF report generation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="REPORT_GENERATION_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


def register_error_handlers(app: FastAPI) -> None:
    """Registers standardized error handlers with the FastAPI application."""

    @app.exception_handler(AppBaseException)
    async def app_base_exception_handler(_: Request, exc: AppBaseException) -> JSONResponse:
        logger.error("Application error: %s [%s] - %s", exc.code, exc.status_code, exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning("Request validation failed: %s", exc.errors())
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid request payload format",
                    "details": exc.errors(),
                }
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled internal exception: %s", str(exc))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "UNHANDLED_EXCEPTION",
                    "message": "An unexpected internal error occurred during execution.",
                    "details": {"error_type": type(exc).__name__},
                }
            },
        )
