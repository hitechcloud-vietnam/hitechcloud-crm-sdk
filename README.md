# HiTechCloud CRM SDK

> Official multi-language SDK for the **HiTechCloud CRM API** — manage contacts,
> companies, deals, pipelines, activities, quotes and real-time webhooks from
> your own applications.

Host: `https://crm-gateways.hitechcloud.vn` · Base path: `/v1` ·
Auth: OAuth2 `client_credentials` → Bearer token ·
Docs: [developers.hitechcloud.vn](https://developers.hitechcloud.vn)

## Supported languages

| Language | Package | Manifest |
|----------|---------|----------|
| Node.js / TypeScript | `@hitechcloud-vietnam/crm-sdk` (npm) | `sdk/nodejs/package.json` |
| Python | `hitechcloud-crm` (PyPI) | `sdk/python/pyproject.toml` |
| PHP | `hitechcloud-vietnam/crm-sdk` (Composer) | `sdk/php/composer.json` |
| Go | `github.com/hitechcloud-vietnam/hitechcloud-crm-sdk/go` | `sdk/go/go.mod` |
| Java | `vn.hitechcloud:crm-sdk` (Maven) | `sdk/java/pom.xml` |

## Resources covered

Contacts, companies, deals, pipelines, stages, activities, tasks, calls,
emails, meetings, notes, tags, segments, custom fields, lead sources, products,
quotes, files, users and teams — each with `list`, `get`, `create`, `update`
and `delete`. Plus: bulk operations (contacts, deals), CSV import/export,
file upload/download, and webhook registration + `X-CRM-Signature` verification.

## Environments

| Environment | Base URL |
|-------------|----------|
| Production | `https://crm-gateways.hitechcloud.vn` |
| Sandbox | `https://crm-gateways-sandbox.hitechcloud.vn` |

## Authentication

Every request uses an OAuth2 `client_credentials` access token. The SDKs fetch,
cache and refresh the token automatically — you only supply `client_id`,
`client_secret` and the scopes you need.

```bash
curl -X POST "https://crm-gateways.hitechcloud.vn/v1/oauth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "grant_type": "client_credentials",
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "scope": "contacts:read contacts:write deals:read deals:write"
  }'
```

Available scopes: `contacts:read`, `contacts:write`, `deals:read`,
`deals:write`, `activities:write`, `webhooks:manage`.

## Quick start

### Node.js / TypeScript

```bash
npm install @hitechcloud-vietnam/crm-sdk
```

```typescript
import { CRMClient } from "@hitechcloud-vietnam/crm-sdk";

const crm = new CRMClient({
  clientId: process.env.CRM_CLIENT_ID!,
  clientSecret: process.env.CRM_CLIENT_SECRET!,
  scope: "contacts:read contacts:write deals:read deals:write",
});

const contacts = await crm.contacts.list({ lifecycle_stage: "customer" });
const deal = await crm.deals.create({
  title: "Goi Cloud Server",
  pipeline_id: "pl_sales",
  stage_id: "stg_qualified",
  amount: 24000000,
});
```

### Python

```bash
pip install hitechcloud-crm
```

```python
from hitechcloud_crm import CRMClient

crm = CRMClient(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    scope="contacts:read contacts:write",
)

contacts = crm.contacts.list(lifecycle_stage="customer")
contact = crm.contacts.create(first_name="Nguyen", email="vana@example.com")
```

### PHP

```bash
composer require hitechcloud-vietnam/crm-sdk
```

```php
use HiTechCloud\CRM\Client;

$crm = new Client([
    'client_id' => 'YOUR_CLIENT_ID',
    'client_secret' => 'YOUR_CLIENT_SECRET',
    'scope' => 'contacts:read contacts:write',
]);

$contacts = $crm->contacts()->list(['lifecycle_stage' => 'customer']);
```

### Go

```bash
go get github.com/hitechcloud-vietnam/hitechcloud-crm-sdk/go
```

```go
import crm "github.com/hitechcloud-vietnam/hitechcloud-crm-sdk/go"

client, _ := crm.NewClient(
    crm.WithClientCredentials("YOUR_CLIENT_ID", "YOUR_CLIENT_SECRET", "contacts:read contacts:write"),
)
contacts, _ := client.Contacts.List(map[string]string{"lifecycle_stage": "customer"})
```

### Java

```xml
<dependency>
  <groupId>vn.hitechcloud</groupId>
  <artifactId>crm-sdk</artifactId>
  <version>1.0.0</version>
</dependency>
```

```java
import vn.hitechcloud.crm.CRMClient;

CRMClient crm = new CRMClient("YOUR_CLIENT_ID", "YOUR_CLIENT_SECRET",
        "contacts:read contacts:write");
Map<String, Object> contacts = crm.contacts().list(Map.of("lifecycle_stage", "customer"));
```

## Webhooks

The CRM signs every webhook body with HMAC-SHA256 and sends it in the
`X-CRM-Signature` header. Each SDK ships a verification helper:

```typescript
import { verifyWebhookSignature } from "@hitechcloud-vietnam/crm-sdk";

if (!verifyWebhookSignature(rawBody, req.headers["x-crm-signature"], secret)) {
  return res.status(400).end();
}
```

See [`docs/`](docs/README.md) for the full Vietnamese documentation, and
[`openapi.json`](openapi.json) for the machine-readable API specification.

## Rate limits

`120 req/min` (standard), `600 req/min` (enterprise), `240 req/min` (sandbox).
On `429` the API returns a `Retry-After` header; the SDKs retry automatically.

## License

MIT — see [LICENSE](LICENSE).

## Support

- Email: support@hitechcloud.vn
- Docs: https://developers.hitechcloud.vn
- Issues: https://github.com/hitechcloud-vietnam/hitechcloud-crm-sdk/issues
