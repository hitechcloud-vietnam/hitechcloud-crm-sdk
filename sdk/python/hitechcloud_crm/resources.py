"""Resource classes for the HiTechCloud CRM API.

Every CRM resource follows the same REST CRUD shape under ``/v1/{path}``, so a
single :class:`CrudResource` implements the common verbs and each concrete
resource simply binds its path. Resources with extra behaviour (files, bulk,
import/export, webhooks) add dedicated methods.
"""

from typing import Any, Dict, List, Optional


class CrudResource:
    """Generic CRUD resource bound to a collection path (e.g. ``contacts``)."""

    #: Resources that support the bulk endpoint.
    _BULK = {"contacts", "deals"}

    def __init__(self, http, path: str):
        self._http = http
        self._path = path

    def list(self, **params: Any) -> Dict[str, Any]:
        """``GET /v1/{path}`` — list records with pagination and filters."""
        clean = {k: v for k, v in params.items() if v is not None}
        return self._http.get(f"/v1/{self._path}", params=clean)

    def get(self, resource_id: str) -> Dict[str, Any]:
        """``GET /v1/{path}/{id}`` — fetch a single record."""
        return self._http.get(f"/v1/{self._path}/{resource_id}")

    def create(self, data: Optional[Dict[str, Any]] = None, **fields: Any) -> Dict[str, Any]:
        """``POST /v1/{path}`` — create a record."""
        body = dict(data or {})
        body.update(fields)
        return self._http.post(f"/v1/{self._path}", json_data=body)

    def update(self, resource_id: str, data: Optional[Dict[str, Any]] = None, **fields: Any) -> Dict[str, Any]:
        """``PATCH /v1/{path}/{id}`` — partially update a record."""
        body = dict(data or {})
        body.update(fields)
        return self._http.patch(f"/v1/{self._path}/{resource_id}", json_data=body)

    def delete(self, resource_id: str) -> Dict[str, Any]:
        """``DELETE /v1/{path}/{id}`` — delete a record."""
        return self._http.delete(f"/v1/{self._path}/{resource_id}")

    def bulk(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """``POST /v1/{path}/bulk`` — up to 100 create/update/delete operations."""
        if self._path not in self._BULK:
            raise ValueError(f"Bulk operations are not supported for {self._path}")
        return self._http.post(f"/v1/{self._path}/bulk", json_data={"operations": operations})


class FilesResource(CrudResource):
    """Files: multipart upload, metadata and binary download."""

    def __init__(self, http):
        super().__init__(http, "files")

    def upload(self, file_path: str, resource_type: str, resource_id: str) -> Dict[str, Any]:
        """``POST /v1/files`` — upload a file and attach it to a resource."""
        with open(file_path, "rb") as fh:
            return self._http.post(
                "/v1/files",
                files={"file": fh},
                data={"resource_type": resource_type, "resource_id": resource_id},
            )

    def download_url(self, file_id: str) -> str:
        """Return the binary download URL for a file."""
        return f"{self._http.base_url}/v1/files/{file_id}/download"

    def create(self, *args: Any, **kwargs: Any):  # pragma: no cover - guard
        raise NotImplementedError("Use FilesResource.upload() to create files")


class WebhooksResource:
    """Register, list and remove webhook endpoints."""

    def __init__(self, http):
        self._http = http

    def list(self) -> Dict[str, Any]:
        return self._http.get("/v1/webhooks")

    def register(self, url: str, events: List[str], secret: Optional[str] = None) -> Dict[str, Any]:
        body: Dict[str, Any] = {"url": url, "events": events}
        if secret:
            body["secret"] = secret
        return self._http.post("/v1/webhooks", json_data=body)

    def delete(self, webhook_id: str) -> Dict[str, Any]:
        return self._http.delete(f"/v1/webhooks/{webhook_id}")


class ImportsResource:
    """Asynchronous CSV import jobs."""

    def __init__(self, http):
        self._http = http

    def create(self, file_path: str, entity: str) -> Dict[str, Any]:
        """``POST /v1/imports`` — start a CSV import job (``contact``/``company``)."""
        with open(file_path, "rb") as fh:
            return self._http.post("/v1/imports", files={"file": fh}, data={"entity": entity})

    def get(self, import_id: str) -> Dict[str, Any]:
        return self._http.get(f"/v1/imports/{import_id}")


class ExportsResource:
    """Asynchronous CSV export jobs."""

    def __init__(self, http):
        self._http = http

    def create(self, entity: str, filter: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """``POST /v1/exports`` — start a CSV export job (``contact``/``deal``/``activity``)."""
        body: Dict[str, Any] = {"entity": entity}
        if filter:
            body["filter"] = filter
        return self._http.post("/v1/exports", json_data=body)

    def get(self, export_id: str) -> Dict[str, Any]:
        return self._http.get(f"/v1/exports/{export_id}")


#: Accessor name -> collection path for every standard CRUD resource.
RESOURCE_PATHS = {
    "contacts": "contacts",
    "companies": "companies",
    "deals": "deals",
    "pipelines": "pipelines",
    "stages": "stages",
    "activities": "activities",
    "tasks": "tasks",
    "calls": "calls",
    "emails": "emails",
    "meetings": "meetings",
    "notes": "notes",
    "tags": "tags",
    "segments": "segments",
    "custom_fields": "custom-fields",
    "lead_sources": "lead-sources",
    "products": "products",
    "quotes": "quotes",
    "users": "users",
    "teams": "teams",
}
