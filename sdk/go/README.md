# HiTechCloud CRM SDK for Go

Official Go SDK for the [HiTechCloud CRM API](https://developers.hitechcloud.vn).
Standard library only — no third-party dependencies.

## Install

```bash
go get github.com/hitechcloud-vietnam/hitechcloud-crm-sdk/go
```

```go
import crm "github.com/hitechcloud-vietnam/hitechcloud-crm-sdk/go"
```

## Authentication

The client uses the OAuth2 `client_credentials` flow and manages the token for
you:

```go
client, err := crm.NewClient(
    crm.WithClientCredentials("YOUR_CLIENT_ID", "YOUR_CLIENT_SECRET",
        "contacts:read contacts:write deals:read deals:write"),
    // crm.WithSandbox(),
)
if err != nil {
    log.Fatal(err)
}
```

You can also use `crm.WithToken("crm_at_...")`.

## Usage

```go
customers, err := client.Contacts.List(map[string]string{"lifecycle_stage": "customer"})

created, _ := client.Contacts.Create(map[string]interface{}{
    "first_name": "Nguyen", "email": "vana@example.com",
})

client.Deals.Create(map[string]interface{}{
    "title": "Goi Cloud Server", "pipeline_id": "pl_sales",
    "stage_id": "stg_qualified", "amount": 24000000,
})

// Bulk (contacts, deals)
client.Contacts.Bulk([]crm.BulkOperation{
    {Op: "create", Data: map[string]interface{}{"first_name": "A", "email": "a@example.com"}},
    {Op: "delete", Data: map[string]interface{}{"id": "con_0011aabb"}},
})

// Files, import/export
client.Files.Upload("hopdong.pdf", "deal", "deal_a19c330e")
client.Imports.Create("contacts.csv", "contact")
client.Exports.Create("contact", map[string]interface{}{"lifecycle_stage": "customer"})

// Webhooks
client.Webhooks.Register("https://your-app.vn/hooks/crm",
    []string{"contact.created", "deal.won"}, "whsec_6b3c15aa")
```

## Verifying webhooks

```go
func handler(w http.ResponseWriter, r *http.Request) {
    body, _ := io.ReadAll(r.Body)
    sig := r.Header.Get("X-CRM-Signature")
    if !crm.VerifyWebhookSignature(body, sig, "whsec_6b3c15aa") {
        w.WriteHeader(http.StatusBadRequest)
        return
    }
    // ...
}
```

## Error handling

```go
_, err := client.Contacts.Get("con_missing")
var nf *crm.NotFoundError
var rl *crm.RateLimitError
switch {
case errors.As(err, &nf):
    // not found
case errors.As(err, &rl):
    fmt.Println("retry after", rl.RetryAfter)
}
```

## License

MIT
