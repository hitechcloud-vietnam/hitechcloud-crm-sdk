# HiTechCloud CRM SDK for Python

Official Python SDK for the [HiTechCloud CRM API](https://developers.hitechcloud.vn).

## Install

```bash
pip install hitechcloud-crm
```

## Authentication

The client uses the OAuth2 `client_credentials` flow and manages the access
token for you (fetch, cache and refresh):

```python
from hitechcloud_crm import CRMClient

crm = CRMClient(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    scope="contacts:read contacts:write deals:read deals:write",
)
```

You may also pass a pre-issued `token=...`, or `sandbox=True` to target the
sandbox environment.

## Usage

```python
# List with filters + pagination
customers = crm.contacts.list(lifecycle_stage="customer", per_page=100)

# Create / get / update / delete
c = crm.contacts.create(first_name="Nguyen", email="vana@example.com")
cid = c["data"]["id"]
crm.contacts.update(cid, lifecycle_stage="customer")
crm.contacts.get(cid)
crm.contacts.delete(cid)

# Deals
crm.deals.create(title="Goi Cloud Server", pipeline_id="pl_sales",
                 stage_id="stg_qualified", amount=24000000)

# Bulk (contacts, deals only)
crm.contacts.bulk([
    {"op": "create", "data": {"first_name": "A", "email": "a@example.com"}},
    {"op": "delete", "data": {"id": "con_0011aabb"}},
])

# Files
crm.files.upload("hopdong.pdf", resource_type="deal", resource_id="deal_a19c330e")

# Import / export
job = crm.imports.create("contacts.csv", entity="contact")
crm.exports.create("contact", filter={"lifecycle_stage": "customer"})

# Webhooks
crm.webhooks.register("https://your-app.vn/hooks/crm",
                      events=["contact.created", "deal.won"],
                      secret="whsec_6b3c15aa")
```

## Verifying webhooks

```python
from hitechcloud_crm import verify_webhook_signature

def handle(request):
    raw = request.get_data()  # exact raw bytes
    sig = request.headers.get("X-CRM-Signature", "")
    if not verify_webhook_signature(raw, sig, "whsec_6b3c15aa"):
        return "", 400
    ...
```

## Error handling

```python
from hitechcloud_crm import NotFoundError, RateLimitError, ValidationError

try:
    crm.contacts.get("con_missing")
except NotFoundError:
    ...
except RateLimitError as e:
    print("retry after", e.retry_after)
except ValidationError as e:
    print(e.code, e.errors)
```

## License

MIT
