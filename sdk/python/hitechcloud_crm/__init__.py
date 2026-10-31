"""HiTechCloud CRM SDK for Python.

Official SDK for the HiTechCloud CRM API (https://developers.hitechcloud.vn).

Usage::

    from hitechcloud_crm import CRMClient

    crm = CRMClient(
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_CLIENT_SECRET",
        scope="contacts:read contacts:write",
    )
    contacts = crm.contacts.list(lifecycle_stage="customer")
"""

__version__ = "1.0.0"
__author__ = "HiTechCloud Vietnam"
__email__ = "support@hitechcloud.vn"

from .client import CRMClient
from .http_client import PRODUCTION_URL, SANDBOX_URL
from .webhooks import verify_signature, compute_signature
from .exceptions import (
    CRMError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ConflictError,
    ValidationError,
    RateLimitError,
    ServerError,
)

# Convenient alias
verify_webhook_signature = verify_signature

__all__ = [
    "CRMClient",
    "PRODUCTION_URL",
    "SANDBOX_URL",
    "verify_signature",
    "verify_webhook_signature",
    "compute_signature",
    "CRMError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ConflictError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
]
