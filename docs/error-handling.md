# Mã lỗi & Xử lý lỗi

Khi request không thành công, API trả mã HTTP phù hợp cùng **envelope lỗi** có
`status: "error"`, `code` và `message`. Hãy dựa vào `code` (ổn định) thay vì
`message` để xử lý logic.

## Envelope lỗi

```json
{
  "status": "error",
  "code": "VALIDATION_ERROR",
  "message": "Truong email khong dung dinh dang.",
  "errors": {
    "email": ["Dinh dang email khong hop le"]
  }
}
```

## Mã trạng thái HTTP

| HTTP | Ý nghĩa |
|------|---------|
| `200 OK` | Thành công |
| `201 Created` | Tạo mới thành công |
| `207 Multi-Status` | Kết quả từng phần (bulk) |
| `400 Bad Request` | Tham số không hợp lệ |
| `401 Unauthorized` | Thiếu hoặc sai Access Token |
| `403 Forbidden` | Token thiếu scope cho thao tác này |
| `404 Not Found` | Không tìm thấy tài nguyên |
| `409 Conflict` | Xung đột (vd trùng email) |
| `422 Unprocessable Entity` | Dữ liệu không qua kiểm tra nghiệp vụ |
| `429 Too Many Requests` | Vượt giới hạn tần suất |
| `500 Internal Server Error` | Lỗi phía máy chủ |

## Mã lỗi chuỗi (code)

| code | HTTP | Mô tả |
|------|------|-------|
| `UNAUTHORIZED` | 401 | Token không hợp lệ hoặc đã hết hạn |
| `FORBIDDEN` | 403 | Token thiếu scope cần thiết |
| `NOT_FOUND` | 404 | ID tài nguyên không tồn tại |
| `VALIDATION_ERROR` | 400/422 | Tham số hoặc payload sai định dạng |
| `DUPLICATE_RESOURCE` | 409 | Tài nguyên đã tồn tại |
| `TOO_MANY_REQUESTS` | 429 | Vượt giới hạn tần suất, xem `Retry-After` |
| `INTERNAL_ERROR` | 500 | Lỗi không mong muốn phía hệ thống |

## Ngoại lệ trong SDK

Mỗi SDK ánh xạ mã HTTP sang một lớp ngoại lệ:

| HTTP | Python / Node / Go / Java |
|------|---------------------------|
| 401 | `AuthenticationError` / `AuthenticationException` |
| 403 | `AuthorizationError` / `AuthorizationException` |
| 404 | `NotFoundError` / `NotFoundException` |
| 409 | `ConflictError` / `ConflictException` |
| 400, 422 | `ValidationError` / `ValidationException` |
| 429 | `RateLimitError` / `RateLimitException` (có `retry_after`) |
| 5xx | `ServerError` / `ServerException` |
| khác | `CRMError` / `CRMException` |

### Python

```python
from hitechcloud_crm import NotFoundError, RateLimitError, ValidationError

try:
    crm.contacts.get("con_missing")
except NotFoundError:
    ...
except RateLimitError as e:
    print("thu lai sau", e.retry_after, "giay")
except ValidationError as e:
    print(e.code, e.errors)
```

### Node.js / TypeScript

```typescript
import { NotFoundError, RateLimitError } from "@hitechcloud-vietnam/crm-sdk";

try {
  await crm.contacts.get("con_missing");
} catch (e) {
  if (e instanceof NotFoundError) { /* ... */ }
  else if (e instanceof RateLimitError) console.log("retry after", e.retryAfter);
}
```

### Go

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

### Java

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

## Thử lại (retry)

Các SDK **tự động thử lại** với độ trễ tăng dần (exponential backoff) cho lỗi
`429` (tôn trọng `Retry-After`) và `5xx`. Với `400/401/403/404`, thử lại thường
vô ích — cần sửa request. SDK cũng tự làm mới token và thử lại một lần khi gặp
`401` do token hết hạn.
