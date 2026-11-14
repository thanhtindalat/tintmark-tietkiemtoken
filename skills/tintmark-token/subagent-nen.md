# Giao subagent trả kết quả nén

Kết quả subagent được chèn nguyên văn vào ngữ cảnh chính và bị đọc lại ở mọi lượt sau: 2k token văn xuôi tốn 2k mỗi lượt; cùng phát hiện trả dạng `đường_dẫn:dòng` còn khoảng một phần ba (ước tính của bản gốc, chưa đo trên máy này).

Khi nào giao và chọn model nào: `chon-model.md` mục 5 (mỗi subagent tốn 20–30k khởi động; không giao việc vài lệnh).

## Giao gì

| Việc | Dùng |
|---|---|
| "X định nghĩa ở đâu / ai gọi Y / liệt kê chỗ dùng Z" | Subagent dò tìm model nhỏ, chỉ đọc, trả `đường_dẫn:dòng` |
| Như trên nhưng cần nhận xét kiến trúc | Subagent thường, yêu cầu kết luận ngắn |
| Review diff tìm lỗi | Subagent review, một dòng mỗi phát hiện |
| Sửa nhỏ ≤ 2 tệp, đã biết tệp, phạm vi rõ | Subagent sửa, hoặc làm luôn ở luồng chính nếu chỉ vài lệnh |
| Tính năng mới, ≥ 3 tệp, refactor cắt ngang | Luồng chính |
| Câu trả lời một dòng đã biết | Luồng chính |

## Hợp đồng đầu ra (ghi thẳng vào lời giao)

- **Dò tìm:** mỗi dòng `đường_dẫn:dòng — ký hiệu — ghi chú ngắn`, cuối có `tổng: …`; không thấy thì đúng một dòng `không thấy`. Chỉ trích dòng đã đọc thật.
- **Sửa:** `đường_dẫn:dòng-dòng — đổi gì (≤ 10 từ)` và `đã kiểm: đọc lại khớp | lệch ở đường_dẫn:dòng`; hoặc một trong `quá lớn` / `cần xác nhận` / `mơ hồ` / `làm hỏng` rồi dừng.
- **Review:** `đường_dẫn:dòng: mức: vấn đề. Cách sửa.` với mức `lỗi` (hỏng hành vi), `rủi ro` (chạy nhưng mong manh), `vặt`, `hỏi`; không có thì `không có lỗi`.
- **Mọi loại:** không chép lại nội dung tệp, không kể lại quá trình; kết quả dài thì ghi ra tệp và trả đường dẫn (luật vàng 4).

## Không nên

- Tin ngay câu "không thấy / không có lỗi" của subagent: kiểm một lần đúng tệp, đúng phạm vi; kiểm số dòng trích có trong tệp.
- Giao sửa khi chưa biết tệp (truyền ngữ cảnh tốn hơn tự làm).
- Nhờ subagent "góp ý chung".
- Đưa đầu ra cụt của subagent thẳng cho người đọc: diễn giải lại bằng câu đầy đủ (`tra-loi-gon.md`).
- Giao tràn lan để "giữ ngữ cảnh": dò rộng tối đa 2–3 subagent song song, và chỉ khi dữ liệu phải đọc lớn hơn hẳn kết quả trả về.
