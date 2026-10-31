"""Webhook signature verification for HiTechCloud CRM.

The CRM signs every webhook body with HMAC-SHA256 using the ``secret`` supplied
at registration time, and sends the hex digest in the ``X-CRM-Signature``
header. Always verify the signature before trusting a payload.
"""

import hashlib
import hmac
from typing import Union


def compute_signature(raw_body: Union[str, bytes], secret: str) -> str:
    """Return the expected hex HMAC-SHA256 signature for ``raw_body``."""
    if isinstance(raw_body, str):
        raw_body = raw_body.encode("utf-8")
    return hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()


def verify_signature(
    raw_body: Union[str, bytes], signature: str, secret: str
) -> bool:
    """Constant-time comparison of a received ``X-CRM-Signature`` header.

    Args:
        raw_body: the exact raw request body bytes/string received.
        signature: the value of the ``X-CRM-Signature`` header.
        secret: the webhook secret you registered.

    Returns:
        ``True`` if the signature is valid, ``False`` otherwise.
    """
    if not signature:
        return False
    expected = compute_signature(raw_body, secret)
    return hmac.compare_digest(expected, signature.strip())
