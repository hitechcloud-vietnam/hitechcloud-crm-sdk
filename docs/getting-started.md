# Bắt đầu nhanh

Hướng dẫn cài đặt SDK, tạo client và thực hiện yêu cầu đầu tiên tới
**HiTechCloud CRM API**.

## 1. Lấy khoá ứng dụng

1. Đăng nhập `https://my.hitechcloud.vn`.
2. Vào **Cấu hình Công ty → API Access** và tạo một ứng dụng CRM mới.
3. Sao chép `client_id` và `client_secret`.
4. Lưu vào biến môi trường, ví dụ:

```bash
export CRM_CLIENT_ID="YOUR_CLIENT_ID"
export CRM_CLIENT_SECRET="YOUR_CLIENT_SECRET"
```

> Access Token cấp quyền truy cập dữ liệu khách hàng. Không nhúng token vào mã
> frontend và không commit lên kho mã nguồn công khai.

## 2. Cài đặt SDK

```bash
# Node.js / TypeScript
npm install @hitechcloud-vietnam/crm-sdk

# Python
pip install hitechcloud-crm

# PHP
composer require hitechcloud-vietnam/crm-sdk

# Go
go get github.com/hitechcloud-vietnam/hitechcloud-crm-sdk/go
```

```xml
<!-- Java (Maven) -->
<dependency>
  <groupId>vn.hitechcloud</groupId>
  <artifactId>crm-sdk</artifactId>
  <version>1.0.0</version>
</dependency>
```

## 3. Tạo client và gọi yêu cầu đầu tiên

SDK tự động đổi `client_id`/`client_secret` lấy access token, lưu cache và tự
làm mới khi hết hạn.

### Node.js / TypeScript

```typescript
import { CRMClient } from "@hitechcloud-vietnam/crm-sdk";

const crm = new CRMClient({
  clientId: process.env.CRM_CLIENT_ID!,
  clientSecret: process.env.CRM_CLIENT_SECRET!,
  scope: "contacts:read contacts:write",
});

const customers = await crm.contacts.list({ lifecycle_stage: "customer" });
console.log(customers.data);
```

### Python

```python
from hitechcloud_crm import CRMClient

crm = CRMClient(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    scope="contacts:read contacts:write",
)
print(crm.contacts.list(lifecycle_stage="customer")["data"])
```

### PHP

```php
use HiTechCloud\CRM\Client;

$crm = new Client([
    'client_id' => 'YOUR_CLIENT_ID',
    'client_secret' => 'YOUR_CLIENT_SECRET',
    'scope' => 'contacts:read contacts:write',
]);
print_r($crm->contacts()->list(['lifecycle_stage' => 'customer']));
```

### Go

```go
client, _ := crm.NewClient(
    crm.WithClientCredentials("YOUR_CLIENT_ID", "YOUR_CLIENT_SECRET", "contacts:read"),
)
res, _ := client.Contacts.List(map[string]string{"lifecycle_stage": "customer"})
fmt.Println(res["data"])
```

### Java

```java
CRMClient crm = new CRMClient("YOUR_CLIENT_ID", "YOUR_CLIENT_SECRET", "contacts:read");
System.out.println(crm.contacts().list(Map.of("lifecycle_stage", "customer")));
```

## 4. Tạo một liên hệ mới

```python
contact = crm.contacts.create(
    first_name="Nguyen",
    last_name="Van A",
    email="vana@example.com",
    phone="0901234567",
)
contact_id = contact["data"]["id"]  # vd: con_8f2a1c9d
```

## 5. Dùng môi trường Sandbox

Thử nghiệm an toàn với dữ liệu tách biệt bằng `sandbox`:

```python
crm = CRMClient(client_id="...", client_secret="...", sandbox=True)
```

Tiếp theo: xem [Xác thực](authentication.md) và [Tham chiếu API](api-reference.md).
