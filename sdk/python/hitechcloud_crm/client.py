"""Main client for the HiTechCloud CRM API."""

from typing import Optional

from .http_client import HTTPClient, PRODUCTION_URL, SANDBOX_URL
from .resources import (
    CrudResource,
    FilesResource,
    WebhooksResource,
    ImportsResource,
    ExportsResource,
    RESOURCE_PATHS,
)


class CRMClient:
    """HiTechCloud CRM client.

    Supply OAuth2 client credentials (recommended) or a pre-issued access token.

    Example::

        from hitechcloud_crm import CRMClient

        crm = CRMClient(
            client_id="YOUR_CLIENT_ID",
            client_secret="YOUR_CLIENT_SECRET",
            scope="contacts:read contacts:write",
        )
        customers = crm.contacts.list(lifecycle_stage="customer")
    """

    PRODUCTION_URL = PRODUCTION_URL
    SANDBOX_URL = SANDBOX_URL

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        scope: Optional[str] = None,
        token: Optional[str] = None,
        base_url: str = PRODUCTION_URL,
        sandbox: bool = False,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        if sandbox:
            base_url = SANDBOX_URL
        self._http = HTTPClient(
            client_id=client_id,
            client_secret=client_secret,
            scope=scope,
            token=token,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Standard CRUD resources
        self.contacts = CrudResource(self._http, "contacts")
        self.companies = CrudResource(self._http, "companies")
        self.deals = CrudResource(self._http, "deals")
        self.pipelines = CrudResource(self._http, "pipelines")
        self.stages = CrudResource(self._http, "stages")
        self.activities = CrudResource(self._http, "activities")
        self.tasks = CrudResource(self._http, "tasks")
        self.calls = CrudResource(self._http, "calls")
        self.emails = CrudResource(self._http, "emails")
        self.meetings = CrudResource(self._http, "meetings")
        self.notes = CrudResource(self._http, "notes")
        self.tags = CrudResource(self._http, "tags")
        self.segments = CrudResource(self._http, "segments")
        self.custom_fields = CrudResource(self._http, "custom-fields")
        self.lead_sources = CrudResource(self._http, "lead-sources")
        self.products = CrudResource(self._http, "products")
        self.quotes = CrudResource(self._http, "quotes")
        self.users = CrudResource(self._http, "users")
        self.teams = CrudResource(self._http, "teams")

        # Special resources
        self.files = FilesResource(self._http)
        self.webhooks = WebhooksResource(self._http)
        self.imports = ImportsResource(self._http)
        self.exports = ExportsResource(self._http)

    def fetch_token(self):
        """Force an OAuth2 token exchange and return the token data."""
        return self._http.fetch_token()

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "CRMClient":
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"CRMClient(base_url={self._http.base_url!r})"


# Keep a stable mapping available for introspection/testing.
__all_resources__ = list(RESOURCE_PATHS.keys()) + ["files", "webhooks", "imports", "exports"]
