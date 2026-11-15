# Nén tệp nhớ (CLAUDE.md, AGENTS.md, MEMORY.md, ghi chú nạp mỗi lượt)

Tệp nạp mỗi lượt là chi phí nền của MỌI lượt gọi ở MỌI phiên: ngắn đi 1k token là bớt 1k mỗi lượt.

## Cách làm (luôn bằng tay, có duyệt)

1. Đo trước: số ký tự / dòng từng tệp nạp mỗi lượt (`wc -c`).
2. Đề xuất từng chỉnh sửa dưới dạng diff; mỗi mục một lần người dùng đồng ý. Tệp luật là của người dùng: không tự ghi đè, không xoá nội dung nhớ khi chưa được đồng ý.
3. Sau mỗi sửa đo lại; không giảm thì hoàn tác.
4. **Không chạy script tự viết lại tệp bằng model** (bản gốc `caveman-compress` gửi toàn văn tệp ra nhà cung cấp model và ghi đè tệp gốc): trái luật "không gửi dữ liệu ra ngoài máy".

## Luật nén

- **Bỏ:** từ đệm (thật ra, về cơ bản, nói chung), lời lịch sự, rào đón ("có thể nên cân nhắc"), cụm thừa ("hãy đảm bảo" → "đảm bảo", "lý do là vì" → "vì"), "bạn nên", "hãy nhớ"; gộp gạch đầu dòng trùng ý; nhiều ví dụ cùng kiểu giữ một.
- **Giữ nguyên:** khối mã và mã trong backtick (chép chính xác, kể cả chú thích và khoảng trắng), URL, đường dẫn, lệnh, tên riêng, ngày, số bản, con số, biến môi trường, chữ phủ định.
- **Giữ cấu trúc:** mọi tiêu đề, cấp gạch đầu dòng, danh sách số, khung bảng, frontmatter.
- **Chỉ nén văn tự nhiên** (`.md`, `.txt`). Không đụng `.py .js .json .yaml .toml .env .sh .sql .html`. Tệp trộn văn và mã: chỉ nén phần văn; không chắc thì để nguyên.

Ví dụ: "Bạn nên luôn đảm bảo chạy bộ test trước khi đẩy lên nhánh chính, vì việc này giúp bắt lỗi sớm." → "Chạy test trước khi push lên main: bắt lỗi sớm."

## Rà sức khoẻ tệp nhớ

| Dấu hiệu | Xử lý |
|---|---|
| Cùng một luật nạp từ hai tệp mỗi lượt | Giữ bản ở tệp cụ thể nhất, bỏ bản kia |
| Chỉ mục trỏ tệp không còn; tệp không ai trỏ tới | Sửa hoặc bỏ dòng; tệp mồ côi thì cho xem vài dòng đầu rồi hỏi nối hay bỏ |
| Chỉ mục dài quá phần được nạp đầu phiên (mục cuối không bao giờ được đọc) | Cô đặc: mỗi mục một dòng, gộp mục cũ, đẩy chi tiết sang tệp con. Ưu tiên cô đặc hơn xoá |
| Đường dẫn / `@import` cũ | Hỏi sửa hay bỏ |
| Luật quan trọng bị chôn giữa tệp | Đề nghị đưa lên đầu, không viết lại câu chữ |
| Khối ngữ cảnh phải dán lại mỗi phiên | Chuyển ra tệp riêng, để lại con trỏ ngắn nói rõ cách gọi lại. Không bỏ ngữ cảnh mà không có đường gọi lại |
| Id phiên, số bản, trạng thái hay đổi ghi trong tệp luật | Chuyển sang sổ tra khi cần (`dieu-phoi.md` mục 1) |

Liên quan: `don-ngu-canh.md` mục 7 (cắt connector, skill thừa).
