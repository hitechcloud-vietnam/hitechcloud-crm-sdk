# @hitechcloud-vietnam/crm-sdk

Official Node.js / TypeScript SDK for the
[HiTechCloud CRM API](https://developers.hitechcloud.vn). Zero runtime
dependencies — uses the built-in `fetch` and `crypto` (Node 18+).

## Install

```bash
npm install @hitechcloud-vietnam/crm-sdk
```

## Authentication

The client performs the OAuth2 `client_credentials` flow and caches/refreshes
the token automatically:

```typescript
import { CRMClient } from "@hitechcloud-vietnam/crm-sdk";

const crm = new CRMClient({
  clientId: process.env.CRM_CLIENT_ID!,
  clientSecret: process.env.CRM_CLIENT_SECRET!,
  scope: "contacts:read contacts:write deals:read deals:write",
  // sandbox: true,
});
```

You can also pass `{ token: "crm_at_..." }` to use a pre-issued token.

## Usage

```typescript
const customers = await crm.contacts.list({ lifecycle_stage: "customer", per_page: 100 });

const created = await crm.contacts.create({ first_name: "Nguyen", email: "vana@example.com" });
const id = created.data.id;
await crm.contacts.update(id, { lifecycle_stage: "customer" });
await crm.contacts.get(id);
await crm.contacts.delete(id);

await crm.deals.create({ title: "Goi Cloud Server", pipeline_id: "pl_sales", stage_id: "stg_qualified", amount: 24000000 });

// Bulk (contacts, deals)
await crm.contacts.bulk([
  { op: "create", data: { first_name: "A", email: "a@example.com" } },
  { op: "delete", data: { id: "con_0011aabb" } },
]);

// Files, import/export
await crm.files.upload("hopdong.pdf", "deal", "deal_a19c330e");
await crm.imports.create("contacts.csv", "contact");
await crm.exports.create("contact", { lifecycle_stage: "customer" });

// Webhooks
await crm.webhooks.register("https://your-app.vn/hooks/crm", ["contact.created", "deal.won"], "whsec_6b3c15aa");
```

## Verifying webhooks

```typescript
import { verifyWebhookSignature } from "@hitechcloud-vietnam/crm-sdk";

app.post("/hooks/crm", express.raw({ type: "*/*" }), (req, res) => {
  const ok = verifyWebhookSignature(req.body, req.header("X-CRM-Signature"), process.env.CRM_WEBHOOK_SECRET!);
  if (!ok) return res.status(400).end();
  // req.body is the exact raw Buffer
  res.status(200).end();
});
```

## Error handling

```typescript
import { NotFoundError, RateLimitError } from "@hitechcloud-vietnam/crm-sdk";

try {
  await crm.contacts.get("con_missing");
} catch (e) {
  if (e instanceof NotFoundError) { /* ... */ }
  if (e instanceof RateLimitError) console.log("retry after", e.retryAfter);
}
```

## Build

```bash
npm install && npm run build
```

## License

MIT
