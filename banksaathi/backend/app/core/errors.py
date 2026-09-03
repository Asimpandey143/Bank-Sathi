"""
Structured error handling for BankSathi.

All API errors use a consistent JSON format:
  {"code": "ERROR_CODE", "message": "Human-readable message"}

Never expose internal stack traces in responses.
"""
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


class BankSathiError(Exception):
    """Base application error."""

    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(BankSathiError):
    def __init__(self, resource: str) -> None:
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class UnauthorizedError(BankSathiError):
    def __init__(self, message: str = "Authentication required.") -> None:
        super().__init__(
            code="UNAUTHORIZED",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenError(BankSathiError):
    def __init__(self, message: str = "You do not have permission to perform this action.") -> None:
        super().__init__(
            code="FORBIDDEN",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class InvalidStateTransitionError(BankSathiError):
    def __init__(self, from_state: str, to_state: str) -> None:
        super().__init__(
            code="INVALID_STATE_TRANSITION",
            message=f"Cannot transition transaction from {from_state} to {to_state}.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class TransactionNotConfirmableError(BankSathiError):
    def __init__(self) -> None:
        super().__init__(
            code="TRANSACTION_NOT_CONFIRMABLE",
            message="Additional verification is required.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class HelperPermissionError(BankSathiError):
    def __init__(self) -> None:
        super().__init__(
            code="HELPER_PERMISSION_DENIED",
            message="Helpers cannot approve, execute, or modify transactions.",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class IntentParseError(BankSathiError):
    def __init__(self, message: str = "Could not understand your request. Please try again.") -> None:
        super().__init__(
            code="INTENT_PARSE_ERROR",
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class ConflictError(BankSathiError):
    def __init__(self, message: str) -> None:
        super().__init__(
            code="CONFLICT",
            message=message,
            status_code=status.HTTP_409_CONFLICT,
        )


class ValidationError(BankSathiError):
    def __init__(self, message: str) -> None:
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


async def banksathi_error_handler(request: Request, exc: BankSathiError) -> JSONResponse:
    """Convert BankSathiError to consistent JSON response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message},
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Convert FastAPI HTTPException to consistent JSON response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": "HTTP_ERROR", "message": exc.detail},
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all — never expose internal details."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred. Please try again.",
        },
    )
