# Xác thực & Access Token

Mọi endpoint của **HiTechCloud CRM API** yêu cầu xác thực bằng Access Token dạng
Bearer. Token được cấp theo luồng **OAuth2 Client Credentials**.

## Luồng cấp token

```
client_id + client_secret + scope
        │
        ▼
POST /v1/oauth/token  (grant_type=client_credentials)
        │
        ▼
access_token (Bearer, hết hạn sau expires_in giây)
        │
        ▼
Authorization: Bearer <access_token>  ← mọi request /v1/*
```

## Đổi lấy token

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

Phản hồi:

```json
{
  "status": "success",
  "data": {
    "access_token": "crm_at_9f8e7d6c5b4a3210",
    "token_type": "Bearer",
    "expires_in": 3600,
    "scope": "contacts:read contacts:write deals:read deals:write"
  }
}
```

## Gửi token trong header

```http
Authorization: Bearer crm_at_9f8e7d6c5b4a3210
Content-Type: application/json
Accept: application/json
```

## Scope quyền truy cập

| Scope | Quyền |
|-------|-------|
| `contacts:read` | Đọc liên hệ và công ty |
| `contacts:write` | Tạo/sửa/xoá liên hệ và công ty |
| `deals:read` | Đọc cơ hội, pipeline và giai đoạn |
| `deals:write` | Tạo/sửa/xoá cơ hội và di chuyển giai đoạn |
| `activities:write` | Ghi nhận hoạt động và ghi chú |
| `webhooks:manage` | Đăng ký và quản lý webhook |

## SDK tự quản lý token

Tất cả SDK trong kho này đều **tự đổi khoá lấy token, cache và làm mới** trước
khi hết hạn (sớm 60 giây), đồng thời tự thử lại một lần nếu máy chủ trả `401`.
Bạn chỉ cần cung cấp `client_id`, `client_secret` và `scope`.

```python
from hitechcloud_crm import CRMClient

crm = CRMClient(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    scope="contacts:read contacts:write",
)
# Không cần tự gọi /v1/oauth/token; muốn lấy thủ công:
token_data = crm.fetch_token()
```

Nếu đã có sẵn token (vd từ hệ thống khác), truyền trực tiếp:

```python
crm = CRMClient(token="crm_at_9f8e7d6c5b4a3210")
```

## Lưu ý bảo mật

- Access Token hết hạn sau `expires_in` giây (mặc định 3600). Hãy cache token,
  đừng gọi `/v1/oauth/token` ở mỗi request.
- Không log hoặc lộ `client_secret`, `access_token` hay `secret` webhook.
- Dùng Sandbox (`crm-gateways-sandbox.hitechcloud.vn`) khi phát triển.
