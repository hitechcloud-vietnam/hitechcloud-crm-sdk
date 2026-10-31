"""HiTechCloud CRM SDK exceptions."""

from typing import Any, Dict, List, Optional


class CRMError(Exception):
    """Base exception for the HiTechCloud CRM SDK."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        code: Optional[str] = None,
        errors: Optional[Dict[str, List[str]]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.code = code
        self.errors = errors or {}
        super().__init__(self.message)


class AuthenticationError(CRMError):
    """Raised when the access token is missing or invalid (401)."""


class AuthorizationError(CRMError):
    """Raised when the token lacks the required scope (403)."""


class NotFoundError(CRMError):
    """Raised when a resource is not found (404)."""


class ConflictError(CRMError):
    """Raised on a duplicate resource conflict (409)."""


class ValidationError(CRMError):
    """Raised when request validation fails (400/422)."""


class RateLimitError(CRMError):
    """Raised when the rate limit is exceeded (429)."""

    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs: Any):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class ServerError(CRMError):
    """Raised when the server returns a 5xx error."""


ERROR_MAP = {
    400: ValidationError,
    401: AuthenticationError,
    403: AuthorizationError,
    404: NotFoundError,
    409: ConflictError,
    422: ValidationError,
    429: RateLimitError,
    500: ServerError,
    502: ServerError,
    503: ServerError,
}
