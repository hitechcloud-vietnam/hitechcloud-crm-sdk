# Tham chiếu API

Mọi endpoint dùng tiền tố `/v1/` và header `Authorization: Bearer <token>`.
Phản hồi tuân theo khung JSON nhất quán: `status`, `data` và `meta` (phân trang
khi là danh sách).

## Khung phản hồi

```json
{
  "status": "success",
  "data": [],
  "meta": {
    "pagination": {
      "total": 100, "per_page": 20, "current_page": 1,
      "last_page": 5, "has_more": true
    }
  }
}
```

## Quy ước định danh

| Tài nguyên | Tiền tố ID | Ví dụ |
|------------|-----------|-------|
| Liên hệ | `con_` | `con_8f2a1c9d` |
| Công ty | `co_` | `co_4b7e2f10` |
| Cơ hội | `deal_` | `deal_a19c330e` |
| Pipeline / Giai đoạn | `pl_` / `stg_` | `pl_sales`, `stg_qualified` |
| Hoạt động | `act_` | `act_77de9012` |
| Ghi chú | `note_` | `note_15aa6b3c` |

## Tài nguyên CRUD

Mỗi tài nguyên dưới đây có 5 thao tác:

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `GET` | `/v1/{tài nguyên}` | Danh sách (phân trang + lọc) |
| `GET` | `/v1/{tài nguyên}/{id}` | Chi tiết theo ID |
| `POST` | `/v1/{tài nguyên}` | Tạo mới |
| `PATCH` | `/v1/{tài nguyên}/{id}` | Cập nhật một phần |
| `DELETE` | `/v1/{tài nguyên}/{id}` | Xoá |

Danh sách tài nguyên và accessor trong SDK:

| Tài nguyên | Path | Accessor (Node/Go/Java) | Accessor (Python/PHP) |
|------------|------|-------------------------|------------------------|
| Liên hệ | `contacts` | `contacts` | `contacts` |
| Công ty | `companies` | `companies` | `companies` |
| Cơ hội | `deals` | `deals` | `deals` |
| Pipeline | `pipelines` | `pipelines` | `pipelines` |
| Giai đoạn | `stages` | `stages` | `stages` |
| Hoạt động | `activities` | `activities` | `activities` |
| Công việc | `tasks` | `tasks` | `tasks` |
| Cuộc gọi | `calls` | `calls` | `calls` |
| Email | `emails` | `emails` | `emails` |
| Cuộc hẹn | `meetings` | `meetings` | `meetings` |
| Ghi chú | `notes` | `notes` | `notes` |
| Nhãn | `tags` | `tags` | `tags` |
| Phân khúc | `segments` | `segments` | `segments` |
| Trường tùy chỉnh | `custom-fields` | `customFields` | `custom_fields` / `customFields()` |
| Nguồn khách hàng | `lead-sources` | `leadSources` | `lead_sources` / `leadSources()` |
| Sản phẩm | `products` | `products` | `products` |
| Báo giá | `quotes` | `quotes` | `quotes` |
| Tệp đính kèm | `files` | `files` | `files` |
| Người dùng | `users` | `users` | `users` |
| Nhóm | `teams` | `teams` | `teams` |

### Ví dụ (các ngôn ngữ)

```python
crm.contacts.list(lifecycle_stage="customer", per_page=100)
crm.contacts.get("con_8f2a1c9d")
crm.contacts.create(first_name="Nguyen", email="vana@example.com")
crm.contacts.update("con_8f2a1c9d", lifecycle_stage="customer")
crm.contacts.delete("con_8f2a1c9d")
```

```typescript
await crm.deals.create({ title: "Goi Cloud Server", pipeline_id: "pl_sales", stage_id: "stg_qualified", amount: 24000000 });
await crm.deals.update("deal_a19c330e", { stage_id: "stg_won", status: "won" });
```

## Thao tác hàng loạt (Bulk)

Chỉ áp dụng cho `contacts` và `deals`. Tối đa 100 thao tác/lần, trả về
`207 Multi-Status` với kết quả từng phần.

| Method | Endpoint |
|--------|----------|
| `POST` | `/v1/contacts/bulk` |
| `POST` | `/v1/deals/bulk` |

```python
crm.contacts.bulk([
    {"op": "create", "data": {"first_name": "A", "email": "a@example.com"}},
    {"op": "update", "data": {"id": "con_8f2a1c9d", "lifecycle_stage": "customer"}},
    {"op": "delete", "data": {"id": "con_0011aabb"}},
])
```

## Tệp đính kèm (Files)

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `POST` | `/v1/files` | Tải lên (multipart), gắn vào contact/company/deal |
| `GET` | `/v1/files` | Danh sách tệp |
| `GET` | `/v1/files/{id}` | Chi tiết tệp |
| `GET` | `/v1/files/{id}/download` | Tải nội dung nhị phân |
| `DELETE` | `/v1/files/{id}` | Xoá tệp |

```python
crm.files.upload("hopdong.pdf", resource_type="deal", resource_id="deal_a19c330e")
url = crm.files.download_url("file_aa11bb22")
```

Dung lượng mỗi tệp tối đa 25MB.

## Nhập / Xuất dữ liệu (CSV, bất đồng bộ)

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `POST` | `/v1/imports` | Tạo tác vụ nhập từ CSV (multipart, `entity`) |
| `GET` | `/v1/imports/{id}` | Theo dõi tiến độ tác vụ nhập |
| `POST` | `/v1/exports` | Tạo tác vụ xuất (`entity`, `filter`) |
| `GET` | `/v1/exports/{id}` | Trạng thái và link tải (`download_url` hết hạn sau 2 giờ) |

```python
job = crm.imports.create("contacts.csv", entity="contact")
crm.imports.get(job["data"]["id"])

exp = crm.exports.create("contact", filter={"lifecycle_stage": "customer"})
crm.exports.get(exp["data"]["id"])
```

## Webhook

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `POST` | `/v1/webhooks` | Đăng ký endpoint (`url`, `events`, `secret`) |
| `GET` | `/v1/webhooks` | Danh sách webhook đã đăng ký |
| `DELETE` | `/v1/webhooks/{id}` | Xoá đăng ký |

Mỗi lần gửi, CRM đính kèm header `X-CRM-Signature` chứa HMAC-SHA256 của toàn bộ
body, ký bằng `secret`. Mọi SDK có hàm kiểm chứng chữ ký:

```python
from hitechcloud_crm import verify_webhook_signature
ok = verify_webhook_signature(raw_body, signature_header, "whsec_6b3c15aa")
```

### Danh sách sự kiện

| Nhóm | Sự kiện |
|------|---------|
| Contact | `contact.created`, `contact.updated`, `contact.deleted` |
| Company | `company.created`, `company.updated`, `company.deleted` |
| Deal | `deal.created`, `deal.stage_changed`, `deal.won`, `deal.lost`, `deal.deleted` |
| Activity | `activity.created`, `activity.completed` |
| Task | `task.created`, `task.completed` |
| Note | `note.created` |
| Quote | `quote.sent`, `quote.accepted`, `quote.rejected` |
| Import | `import.completed` |

Sự kiện gửi theo cơ chế **at-least-once** — khử trùng lặp theo `id` sự kiện
(`evt_...`). Hãy phản hồi `2xx` trong vòng 5 giây; nếu lỗi/chậm, hệ thống thử
gửi lại theo backoff tăng dần tối đa 24 giờ.

## Xác thực token

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `POST` | `/v1/oauth/token` | Đổi `client_credentials` lấy access token |

Xem đầy đủ ở `openapi.json` (OpenAPI 3.0.3).
