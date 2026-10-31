"""Low-level HTTP client for the HiTechCloud CRM API.

Handles the OAuth2 ``client_credentials`` token flow (fetch, cache and refresh),
retries on ``429``/``5xx`` and maps error envelopes to typed exceptions.
"""

import time
from typing import Any, Dict, Optional

import requests

from .exceptions import CRMError, RateLimitError, ERROR_MAP

__version__ = "1.0.0"

PRODUCTION_URL = "https://crm-gateways.hitechcloud.vn"
SANDBOX_URL = "https://crm-gateways-sandbox.hitechcloud.vn"
TOKEN_PATH = "/v1/oauth/token"


class HTTPClient:
    """HTTP transport with built-in OAuth2 token management."""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        scope: Optional[str] = None,
        token: Optional[str] = None,
        base_url: str = PRODUCTION_URL,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._client_id = client_id
        self._client_secret = client_secret
        self._scope = scope
        self._token: Optional[str] = token
        self._token_expiry: float = float("inf") if token else 0.0
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": f"hitechcloud-crm-python/{__version__}",
            }
        )

    # -- token management -------------------------------------------------
    def _ensure_token(self) -> None:
        if self._token and time.time() < self._token_expiry:
            return
        if not (self._client_id and self._client_secret):
            if self._token:
                return
            raise CRMError("No access token and no client credentials configured")
        self.fetch_token()

    def fetch_token(self) -> Dict[str, Any]:
        """Exchange client credentials for a fresh access token."""
        payload = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }
        if self._scope:
            payload["scope"] = self._scope
        resp = self.session.post(
            self.base_url + TOKEN_PATH, json=payload, timeout=self.timeout
        )
        if resp.status_code >= 400:
            self._raise_error(resp)
        data = resp.json().get("data", {})
        self._token = data.get("access_token")
        expires_in = int(data.get("expires_in", 3600))
        # refresh 60s early to avoid edge-of-expiry failures
        self._token_expiry = time.time() + max(expires_in - 60, 30)
        return data

    def set_token(self, token: str) -> None:
        self._token = token
        self._token_expiry = float("inf")

    # -- requests ---------------------------------------------------------
    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        data: Optional[Dict] = None,
        _retry_auth: bool = True,
    ) -> Any:
        self._ensure_token()
        url = self.base_url + "/" + path.lstrip("/")
        headers = {"Authorization": f"Bearer {self._token}"}
        if json_data is not None:
            headers["Content-Type"] = "application/json"

        last_error: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                resp = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    data=data,
                    files=files,
                    headers=headers,
                    timeout=self.timeout,
                )
            except (requests.ConnectionError, requests.Timeout) as exc:
                last_error = exc
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
                    continue
                raise CRMError(f"Request failed: {exc}")

            if resp.status_code == 401 and _retry_auth and self._client_id:
                # token likely expired server-side: refresh once and retry
                self.fetch_token()
                headers["Authorization"] = f"Bearer {self._token}"
                _retry_auth = False
                continue

            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", 60))
                if attempt < self.max_retries:
                    time.sleep(retry_after)
                    continue
                raise RateLimitError(
                    "Rate limit exceeded", retry_after=retry_after, status_code=429,
                    code="TOO_MANY_REQUESTS",
                )

            if resp.status_code >= 500 and attempt < self.max_retries:
                time.sleep(2 ** attempt)
                continue

            if resp.status_code >= 400:
                self._raise_error(resp)

            if resp.status_code == 204 or not resp.content:
                return None
            return resp.json()

        if last_error:
            raise CRMError(f"Request failed after retries: {last_error}")
        raise CRMError("Request failed")

    def _raise_error(self, resp: requests.Response) -> None:
        code = None
        errors: Dict[str, Any] = {}
        try:
            body = resp.json()
            message = body.get("message") or f"HTTP {resp.status_code}"
            code = body.get("code")
            errors = body.get("errors", {}) or {}
        except ValueError:
            message = f"HTTP {resp.status_code}: {resp.text[:200]}"

        error_class = ERROR_MAP.get(resp.status_code, CRMError)
        kwargs: Dict[str, Any] = {
            "status_code": resp.status_code,
            "code": code,
            "errors": errors,
        }
        if error_class is RateLimitError:
            kwargs["retry_after"] = int(resp.headers.get("Retry-After", 60))
        raise error_class(message, **kwargs)

    # -- verbs ------------------------------------------------------------
    def get(self, path: str, params: Optional[Dict] = None) -> Any:
        return self.request("GET", path, params=params)

    def post(self, path: str, json_data: Optional[Dict] = None, **kw: Any) -> Any:
        return self.request("POST", path, json_data=json_data, **kw)

    def patch(self, path: str, json_data: Optional[Dict] = None) -> Any:
        return self.request("PATCH", path, json_data=json_data)

    def delete(self, path: str) -> Any:
        return self.request("DELETE", path)

    def close(self) -> None:
        self.session.close()
