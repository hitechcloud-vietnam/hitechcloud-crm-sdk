# HiTechCloud CRM SDK for Java

Official Java SDK for the [HiTechCloud CRM API](https://developers.hitechcloud.vn).
Java 11+, Gson for JSON, the built-in `java.net.http` client for transport.

## Install

```xml
<dependency>
  <groupId>vn.hitechcloud</groupId>
  <artifactId>crm-sdk</artifactId>
  <version>1.0.0</version>
</dependency>
```

## Authentication

The client performs the OAuth2 `client_credentials` flow and manages the token:

```java
import vn.hitechcloud.crm.CRMClient;

CRMClient crm = new CRMClient("YOUR_CLIENT_ID", "YOUR_CLIENT_SECRET",
        "contacts:read contacts:write deals:read deals:write");

// Sandbox / pre-issued token:
CRMClient sandbox = new CRMClient(null, null, null, "crm_at_...",
        CRMClient.SANDBOX_URL, 30, 3);
```

## Usage

```java
Map<String, Object> customers = crm.contacts().list(Map.of("lifecycle_stage", "customer"));

Map<String, Object> created = crm.contacts().create(Map.of(
        "first_name", "Nguyen", "email", "vana@example.com"));

crm.deals().create(Map.of(
        "title", "Goi Cloud Server", "pipeline_id", "pl_sales",
        "stage_id", "stg_qualified", "amount", 24000000));

// Bulk (contacts, deals)
crm.contacts().bulk(List.of(
        Map.of("op", "create", "data", Map.of("first_name", "A", "email", "a@example.com")),
        Map.of("op", "delete", "data", Map.of("id", "con_0011aabb"))));

// Files, import/export
crm.files().upload(Path.of("hopdong.pdf"), "deal", "deal_a19c330e");
crm.imports().create(Path.of("contacts.csv"), "contact");
crm.exports().create("contact", Map.of("lifecycle_stage", "customer"));

// Webhooks
crm.webhooks().register("https://your-app.vn/hooks/crm",
        List.of("contact.created", "deal.won"), "whsec_6b3c15aa");
```

## Verifying webhooks

```java
import vn.hitechcloud.crm.Webhook;

boolean ok = Webhook.verifySignature(rawBodyBytes, signatureHeader, "whsec_6b3c15aa");
if (!ok) { /* reject */ }
```

## Error handling

```java
try {
    crm.contacts().get("con_missing");
} catch (NotFoundException e) {
    // ...
} catch (RateLimitException e) {
    System.out.println("retry after " + e.getRetryAfter());
} catch (CRMException e) {
    System.out.println(e.getCode() + ": " + e.getMessage());
}
```

## License

MIT
