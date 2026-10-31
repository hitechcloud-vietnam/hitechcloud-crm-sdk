# Tài liệu HiTechCloud CRM SDK

Bộ SDK chính thức cho **HiTechCloud CRM API** — quản lý liên hệ, công ty, cơ hội
bán hàng, pipeline, hoạt động, báo giá và webhook thời gian thực từ ứng dụng của
bạn.

- Host: `https://crm-gateways.hitechcloud.vn`
- Tiền tố phiên bản: `/v1`
- Xác thực: OAuth2 `client_credentials` → Bearer token

## Mục lục

| Trang | Nội dung |
|-------|----------|
| [Bắt đầu nhanh](getting-started.md) | Cài đặt, tạo client và gọi yêu cầu đầu tiên |
| [Xác thực](authentication.md) | Luồng OAuth2, scope và quản lý token |
| [Tham chiếu API](api-reference.md) | Tài nguyên, endpoint và phương thức SDK |
| [Xử lý lỗi](error-handling.md) | Mã lỗi, ngoại lệ và cách xử lý |
| [Phân trang & Rate limit](rate-limiting.md) | Phân trang và giới hạn tần suất |

## Ngôn ngữ hỗ trợ

| Ngôn ngữ | Gói |
|----------|-----|
| Node.js / TypeScript | `@hitechcloud-vietnam/crm-sdk` (npm) |
| Python | `hitechcloud-crm` (PyPI) |
| PHP | `hitechcloud-vietnam/crm-sdk` (Composer) |
| Go | `github.com/hitechcloud-vietnam/hitechcloud-crm-sdk/go` |
| Java | `vn.hitechcloud:crm-sdk` (Maven) |

## Tài nguyên

Liên hệ, công ty, cơ hội, pipeline, giai đoạn, hoạt động, công việc, cuộc gọi,
email, cuộc hẹn, ghi chú, nhãn, phân khúc, trường tùy chỉnh, nguồn khách hàng,
sản phẩm, báo giá, tệp đính kèm, người dùng và nhóm — mỗi loại đều có đầy đủ
`list`, `get`, `create`, `update`, `delete`. Ngoài ra: thao tác hàng loạt
(contacts, deals), nhập/xuất CSV, tải tệp và đăng ký webhook.

## Môi trường

| Môi trường | Base URL |
|------------|----------|
| Production | `https://crm-gateways.hitechcloud.vn` |
| Sandbox | `https://crm-gateways-sandbox.hitechcloud.vn` |

Xem thêm `openapi.json` ở thư mục gốc để lấy đặc tả API ở định dạng máy đọc được.
