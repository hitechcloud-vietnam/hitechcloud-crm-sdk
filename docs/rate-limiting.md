# Phân trang & Rate limit

## Phân trang

Mọi endpoint danh sách hỗ trợ phân trang bằng `page` và `per_page`, kèm khối
`meta.pagination`.

| Tham số | Kiểu | Mặc định | Mô tả |
|---------|------|----------|-------|
| `page` | integer | 1 | Số thứ tự trang cần lấy |
| `per_page` | integer | 20 | Số bản ghi mỗi trang, tối đa 100 |

Khối `meta.pagination`:

| Trường | Mô tả |
|--------|-------|
| `total` | Tổng số bản ghi khớp bộ lọc |
| `per_page` | Số bản ghi mỗi trang đang áp dụng |
| `current_page` | Trang hiện tại |
| `last_page` | Trang cuối cùng |
| `has_more` | `true` nếu còn trang sau |

### Lặp qua tất cả trang

```python
page, all_contacts = 1, []
while True:
    res = crm.contacts.list(page=page, per_page=100)
    all_contacts.extend(res["data"])
    if not res["meta"]["pagination"]["has_more"]:
        break
    page += 1
print(f"Da lay {len(all_contacts)} lien he")
```

```typescript
let page = 1;
const all: any[] = [];
for (;;) {
  const res = await crm.contacts.list({ page, per_page: 100 });
  all.push(...res.data);
  if (!res.meta?.pagination?.has_more) break;
  page++;
}
```

## Giới hạn tần suất (Rate Limits)

| Loại tài khoản | Giới hạn | Header trả về |
|----------------|----------|---------------|
| Tiêu chuẩn | 120 requests / phút | `X-RateLimit-Limit: 120` |
| Doanh nghiệp | 600 requests / phút | `X-RateLimit-Limit: 600` |
| Sandbox | 240 requests / phút | `X-RateLimit-Limit: 240` |

Khi vượt hạn mức, API trả `429 Too Many Requests` kèm header `Retry-After`
(số giây nên chờ).

### SDK tự xử lý

Các SDK **tự động chờ `Retry-After` và thử lại** (tối đa `max_retries` lần, mặc
định 3). Nếu vẫn vượt hạn mức sau khi hết lượt thử, SDK ném `RateLimitError`
(hoặc `RateLimitException`) với thuộc tính `retry_after`.

### Mẹo giảm số lần gọi

- Dùng `per_page=100` kết hợp bộ lọc khi đồng bộ dữ liệu lớn.
- Dùng endpoint **bulk** cho `contacts`/`deals` thay vì gọi lẻ từng bản ghi.
- Dùng **webhook** thay vì polling để nhận thay đổi thời gian thực.
- Cache access token (SDK đã làm sẵn) thay vì gọi `/v1/oauth/token` mỗi lần.
