# Examples

Runnable examples for each language SDK. All target the **sandbox** environment
and read credentials from `CRM_CLIENT_ID` / `CRM_CLIENT_SECRET`.

| Language | File | Run |
|----------|------|-----|
| Python | [`python/basic_usage.py`](python/basic_usage.py) | `python basic_usage.py` |
| Node.js | [`nodejs/basic_usage.mjs`](nodejs/basic_usage.mjs) | `node basic_usage.mjs` |
| PHP | [`php/basic_usage.php`](php/basic_usage.php) | `php basic_usage.php` |
| Go | [`go/basic_usage.go`](go/basic_usage.go) | `go run basic_usage.go` |
| Java | [`java/BasicUsage.java`](java/BasicUsage.java) | `java BasicUsage.java` |

```bash
export CRM_CLIENT_ID="YOUR_CLIENT_ID"
export CRM_CLIENT_SECRET="YOUR_CLIENT_SECRET"
```

Each example: creates a contact, updates and fetches it, lists customers,
creates a deal, registers a webhook, and demonstrates error handling.
