# Changelog

All notable changes to the HiTechCloud CRM SDK are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-11-01

### Added
- Initial public release of the HiTechCloud CRM SDK in five languages:
  Node.js/TypeScript, Python, PHP, Go and Java.
- OAuth2 `client_credentials` token flow with automatic token caching and
  refresh in every client.
- Full CRUD coverage for 20 CRM resources: contacts, companies, deals,
  pipelines, stages, activities, tasks, calls, emails, meetings, notes, tags,
  segments, custom fields, lead sources, products, quotes, files, users and
  teams.
- Bulk operations for contacts and deals (`POST /v1/{resource}/bulk`).
- Asynchronous CSV import and export jobs.
- File upload (multipart) and download helpers.
- Webhook registration helpers and an `X-CRM-Signature` (HMAC-SHA256)
  verification helper in every language.
- Typed exception hierarchy mapped from HTTP status codes, including
  `RateLimitError` exposing `Retry-After`.
- Automatic retry with exponential backoff for `429` and `5xx` responses.
- `openapi.json` (OpenAPI 3.0.3) describing all endpoints.
- A Node.js Model Context Protocol (MCP) server exposing core CRM tools.
- Vietnamese documentation under `docs/`.

[1.0.0]: https://github.com/hitechcloud-vietnam/hitechcloud-crm-sdk/releases/tag/v1.0.0
