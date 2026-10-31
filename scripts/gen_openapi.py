#!/usr/bin/env python3
"""Generate openapi.json for the HiTechCloud CRM API.

Source of truth: portal-tools/src/lib/docs/crm.ts
Host: https://crm-gateways.hitechcloud.vn, base path /v1
Auth: OAuth2 client_credentials -> Bearer
This script writes ../openapi.json relative to this file.
"""
import json
import os

HOST = "https://crm-gateways.hitechcloud.vn"
SANDBOX = "https://crm-gateways-sandbox.hitechcloud.vn"

# (accessor, path, vi_name, id_sample, tag)
RESOURCES = [
    ("contacts", "contacts", "Contacts", "con_8f2a1c9d", True),
    ("companies", "companies", "Companies", "co_4b7e2f10", False),
    ("deals", "deals", "Deals", "deal_a19c330e", True),
    ("pipelines", "pipelines", "Pipelines", "pl_sales", False),
    ("stages", "stages", "Stages", "stg_qualified", False),
    ("activities", "activities", "Activities", "act_77de9012", False),
    ("tasks", "tasks", "Tasks", "task_5c1d2e3f", False),
    ("calls", "calls", "Calls", "call_9a8b7c6d", False),
    ("emails", "emails", "Emails", "email_1f2e3d4c", False),
    ("meetings", "meetings", "Meetings", "mtg_7788aabb", False),
    ("notes", "notes", "Notes", "note_15aa6b3c", False),
    ("tags", "tags", "Tags", "tag_vip", False),
    ("segments", "segments", "Segments", "seg_vip_hcm", False),
    ("custom-fields", "custom-fields", "Custom Fields", "cf_hang_khach", False),
    ("lead-sources", "lead-sources", "Lead Sources", "ls_website", False),
    ("products", "products", "Products", "prod_cloud8", False),
    ("quotes", "quotes", "Quotes", "quote_2026001", False),
    ("users", "users", "Users", "usr_12", False),
    ("teams", "teams", "Teams", "team_sales", False),
]

BULK_RESOURCES = {"contacts", "deals"}


def envelope_ref():
    return {"$ref": "#/components/schemas/Envelope"}


def list_envelope_ref():
    return {"$ref": "#/components/schemas/ListEnvelope"}


def error_responses():
    codes = {
        "400": "VALIDATION_ERROR",
        "401": "UNAUTHORIZED",
        "403": "FORBIDDEN",
        "404": "NOT_FOUND",
        "409": "DUPLICATE_RESOURCE",
        "422": "VALIDATION_ERROR",
        "429": "TOO_MANY_REQUESTS",
        "500": "INTERNAL_ERROR",
    }
    out = {}
    for code, _ in codes.items():
        out[code] = {
            "description": "Error",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorEnvelope"}
                }
            },
        }
    return out


def build():
    paths = {}

    # OAuth token endpoint
    paths["/v1/oauth/token"] = {
        "post": {
            "tags": ["Authentication"],
            "summary": "Exchange client credentials for an access token",
            "operationId": "createToken",
            "security": [],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/TokenRequest"}
                    }
                },
            },
            "responses": {
                "200": {
                    "description": "Access token issued",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/TokenEnvelope"}
                        }
                    },
                },
                **error_responses(),
            },
        }
    }

    for accessor, path, name, id_sample, has_bulk in RESOURCES:
        is_files = path == "files"
        # Collection path
        collection = {
            "get": {
                "tags": [name],
                "summary": f"List {name.lower()}",
                "operationId": f"list_{accessor.replace('-', '_')}",
                "parameters": [
                    {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
                    {"name": "per_page", "in": "query", "schema": {"type": "integer", "default": 20, "maximum": 100}},
                    {"name": "q", "in": "query", "schema": {"type": "string"}},
                ],
                "responses": {
                    "200": {
                        "description": "A paginated list",
                        "content": {"application/json": {"schema": list_envelope_ref()}},
                    },
                    **error_responses(),
                },
            }
        }
        if is_files:
            collection["post"] = {
                "tags": [name],
                "summary": "Upload a file and attach it to a resource",
                "operationId": "upload_file",
                "requestBody": {
                    "required": True,
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "file": {"type": "string", "format": "binary"},
                                    "resource_type": {"type": "string", "enum": ["contact", "company", "deal"]},
                                    "resource_id": {"type": "string"},
                                },
                                "required": ["file", "resource_type", "resource_id"],
                            }
                        }
                    },
                },
                "responses": {
                    "201": {"description": "File uploaded", "content": {"application/json": {"schema": envelope_ref()}}},
                    **error_responses(),
                },
            }
        else:
            collection["post"] = {
                "tags": [name],
                "summary": f"Create a new {name.lower()[:-1] if name.endswith('s') else name.lower()}",
                "operationId": f"create_{accessor.replace('-', '_')}",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"type": "object"}}},
                },
                "responses": {
                    "201": {"description": "Created", "content": {"application/json": {"schema": envelope_ref()}}},
                    **error_responses(),
                },
            }
        paths[f"/v1/{path}"] = collection

        # Item path
        item = {
            "get": {
                "tags": [name],
                "summary": f"Get a {name.lower()} record by ID",
                "operationId": f"get_{accessor.replace('-', '_')}",
                "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}, "example": id_sample}],
                "responses": {
                    "200": {"description": "Found", "content": {"application/json": {"schema": envelope_ref()}}},
                    **error_responses(),
                },
            },
            "delete": {
                "tags": [name],
                "summary": f"Delete a {name.lower()} record",
                "operationId": f"delete_{accessor.replace('-', '_')}",
                "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}, "example": id_sample}],
                "responses": {
                    "200": {"description": "Deleted", "content": {"application/json": {"schema": envelope_ref()}}},
                    **error_responses(),
                },
            },
        }
        if not is_files:
            item["patch"] = {
                "tags": [name],
                "summary": f"Partially update a {name.lower()} record",
                "operationId": f"update_{accessor.replace('-', '_')}",
                "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}, "example": id_sample}],
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object"}}}},
                "responses": {
                    "200": {"description": "Updated", "content": {"application/json": {"schema": envelope_ref()}}},
                    **error_responses(),
                },
            }
        paths[f"/v1/{path}/{{id}}"] = item

        if has_bulk:
            paths[f"/v1/{path}/bulk"] = {
                "post": {
                    "tags": [name],
                    "summary": f"Bulk create/update/delete {name.lower()}",
                    "operationId": f"bulk_{accessor.replace('-', '_')}",
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BulkRequest"}}},
                    },
                    "responses": {
                        "207": {"description": "Multi-Status partial result", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BulkEnvelope"}}}},
                        **error_responses(),
                    },
                }
            }

    # File download
    paths["/v1/files/{id}/download"] = {
        "get": {
            "tags": ["Files"],
            "summary": "Download a file's binary content",
            "operationId": "download_file",
            "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}],
            "responses": {
                "200": {"description": "Binary content", "content": {"application/octet-stream": {"schema": {"type": "string", "format": "binary"}}}},
                **error_responses(),
            },
        }
    }

    # Imports
    paths["/v1/imports"] = {
        "post": {
            "tags": ["Import/Export"],
            "summary": "Create an asynchronous CSV import job",
            "operationId": "create_import",
            "requestBody": {
                "required": True,
                "content": {
                    "multipart/form-data": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "file": {"type": "string", "format": "binary"},
                                "entity": {"type": "string", "enum": ["contact", "company"]},
                            },
                            "required": ["file", "entity"],
                        }
                    }
                },
            },
            "responses": {
                "202": {"description": "Import job accepted", "content": {"application/json": {"schema": envelope_ref()}}},
                **error_responses(),
            },
        }
    }
    paths["/v1/imports/{id}"] = {
        "get": {
            "tags": ["Import/Export"],
            "summary": "Get the status of an import job",
            "operationId": "get_import",
            "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}],
            "responses": {
                "200": {"description": "Import job status", "content": {"application/json": {"schema": envelope_ref()}}},
                **error_responses(),
            },
        }
    }
    # Exports
    paths["/v1/exports"] = {
        "post": {
            "tags": ["Import/Export"],
            "summary": "Create an asynchronous CSV export job",
            "operationId": "create_export",
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ExportRequest"}}},
            },
            "responses": {
                "202": {"description": "Export job accepted", "content": {"application/json": {"schema": envelope_ref()}}},
                **error_responses(),
            },
        }
    }
    paths["/v1/exports/{id}"] = {
        "get": {
            "tags": ["Import/Export"],
            "summary": "Get the status and download link of an export job",
            "operationId": "get_export",
            "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}],
            "responses": {
                "200": {"description": "Export job status", "content": {"application/json": {"schema": envelope_ref()}}},
                **error_responses(),
            },
        }
    }
    # Webhooks
    paths["/v1/webhooks"] = {
        "get": {
            "tags": ["Webhooks"],
            "summary": "List registered webhook endpoints",
            "operationId": "list_webhooks",
            "responses": {
                "200": {"description": "A list of webhooks", "content": {"application/json": {"schema": list_envelope_ref()}}},
                **error_responses(),
            },
        },
        "post": {
            "tags": ["Webhooks"],
            "summary": "Register a webhook endpoint",
            "operationId": "create_webhook",
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/WebhookRequest"}}},
            },
            "responses": {
                "201": {"description": "Webhook registered", "content": {"application/json": {"schema": envelope_ref()}}},
                **error_responses(),
            },
        },
    }
    paths["/v1/webhooks/{id}"] = {
        "delete": {
            "tags": ["Webhooks"],
            "summary": "Delete a webhook registration",
            "operationId": "delete_webhook",
            "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}],
            "responses": {
                "200": {"description": "Deleted", "content": {"application/json": {"schema": envelope_ref()}}},
                **error_responses(),
            },
        }
    }

    schemas = {
        "Envelope": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "example": "success"},
                "data": {"type": "object"},
            },
            "required": ["status", "data"],
        },
        "ListEnvelope": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "example": "success"},
                "data": {"type": "array", "items": {"type": "object"}},
                "meta": {"$ref": "#/components/schemas/Meta"},
            },
            "required": ["status", "data"],
        },
        "Meta": {
            "type": "object",
            "properties": {
                "pagination": {
                    "type": "object",
                    "properties": {
                        "total": {"type": "integer"},
                        "per_page": {"type": "integer"},
                        "current_page": {"type": "integer"},
                        "last_page": {"type": "integer"},
                        "has_more": {"type": "boolean"},
                    },
                }
            },
        },
        "ErrorEnvelope": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "example": "error"},
                "code": {"type": "string", "example": "VALIDATION_ERROR"},
                "message": {"type": "string"},
                "errors": {"type": "object", "additionalProperties": {"type": "array", "items": {"type": "string"}}},
            },
            "required": ["status", "code", "message"],
        },
        "TokenRequest": {
            "type": "object",
            "properties": {
                "grant_type": {"type": "string", "enum": ["client_credentials"]},
                "client_id": {"type": "string"},
                "client_secret": {"type": "string"},
                "scope": {"type": "string", "example": "contacts:read contacts:write deals:read deals:write"},
            },
            "required": ["grant_type", "client_id", "client_secret"],
        },
        "TokenEnvelope": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "example": "success"},
                "data": {
                    "type": "object",
                    "properties": {
                        "access_token": {"type": "string", "example": "crm_at_9f8e7d6c5b4a3210"},
                        "token_type": {"type": "string", "example": "Bearer"},
                        "expires_in": {"type": "integer", "example": 3600},
                        "scope": {"type": "string"},
                    },
                },
            },
        },
        "BulkRequest": {
            "type": "object",
            "properties": {
                "operations": {
                    "type": "array",
                    "maxItems": 100,
                    "items": {
                        "type": "object",
                        "properties": {
                            "op": {"type": "string", "enum": ["create", "update", "delete"]},
                            "data": {"type": "object"},
                        },
                        "required": ["op", "data"],
                    },
                }
            },
            "required": ["operations"],
        },
        "BulkEnvelope": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "example": "success"},
                "data": {
                    "type": "object",
                    "properties": {
                        "results": {"type": "array", "items": {"type": "object"}},
                        "succeeded": {"type": "integer"},
                        "failed": {"type": "integer"},
                    },
                },
            },
        },
        "ExportRequest": {
            "type": "object",
            "properties": {
                "entity": {"type": "string", "enum": ["contact", "deal", "activity"]},
                "filter": {"type": "object"},
            },
            "required": ["entity"],
        },
        "WebhookRequest": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "format": "uri"},
                "events": {"type": "array", "items": {"type": "string"}},
                "secret": {"type": "string", "example": "whsec_6b3c15aa"},
            },
            "required": ["url", "events"],
        },
    }

    doc = {
        "openapi": "3.0.3",
        "info": {
            "title": "HiTechCloud CRM API",
            "description": (
                "Official REST API for HiTechCloud CRM: contacts, companies, deals, "
                "pipelines, stages, activities, tasks, calls, emails, meetings, notes, "
                "tags, segments, custom fields, lead sources, products, quotes, files, "
                "users and teams, plus bulk operations, CSV import/export and real-time "
                "webhooks signed with X-CRM-Signature (HMAC-SHA256)."
            ),
            "version": "1.0.0",
            "contact": {
                "name": "HiTechCloud Support",
                "email": "support@hitechcloud.vn",
                "url": "https://developers.hitechcloud.vn",
            },
            "license": {"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
        },
        "servers": [
            {"url": HOST, "description": "Production"},
            {"url": SANDBOX, "description": "Sandbox"},
        ],
        "security": [{"BearerAuth": []}],
        "tags": [{"name": n} for _, _, n, _, _ in RESOURCES]
        + [
            {"name": "Authentication"},
            {"name": "Import/Export"},
            {"name": "Webhooks"},
        ],
        "paths": paths,
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "description": "OAuth2 client_credentials access token in the Authorization header.",
                },
                "OAuth2": {
                    "type": "oauth2",
                    "flows": {
                        "clientCredentials": {
                            "tokenUrl": f"{HOST}/v1/oauth/token",
                            "scopes": {
                                "contacts:read": "Read contacts and companies",
                                "contacts:write": "Create/update/delete contacts and companies",
                                "deals:read": "Read deals, pipelines and stages",
                                "deals:write": "Create/update/delete deals and move stages",
                                "activities:write": "Log activities and notes",
                                "webhooks:manage": "Register and manage webhooks",
                            },
                        }
                    },
                },
            },
            "schemas": schemas,
        },
    }
    return doc


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "..", "openapi.json")
    doc = build()
    with open(out, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Wrote {os.path.normpath(out)} with {len(doc['paths'])} paths")


if __name__ == "__main__":
    main()
