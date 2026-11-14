# Trả lời gọn trong chat

Đầu ra chỉ chiếm dưới 10% chi phí (`thuat-toan.md`), nên đây là đòn nhỏ: làm cho người đọc đỡ mệt là chính, không đổi lấy rủi ro hiểu sai.

## Luật

1. **Trả lời trước.** Câu đầu là kết quả hoặc quyết định cần ở người đọc, không phải "em sẽ làm gì".
2. **Bỏ nghi thức.** Không chào, không rào đón, không nhắc lại câu hỏi, không tóm lại điều vừa nói, không mời giúp thêm.
3. **Không bao giờ bỏ:** không / chưa / chỉ / trừ; con số và đơn vị; mã, lệnh, đường dẫn, tên API; thông báo lỗi (trích nguyên dòng quyết định).
4. **Một ý một câu, mỗi thứ một tên gọi.** Viết tắt chuẩn được (DB, API); không tự chế viết tắt. Câu gọn mà hiểu được hai cách thì viết câu đầy đủ.
5. **Sửa mã trong chat:** chỉ dòng đổi kèm 1–2 dòng ngữ cảnh, không dán cả tệp (trừ tệp mới hoặc được hỏi).
6. **Khi chạy công cụ:** một dòng trước chuỗi nhiều bước, một dòng mỗi lần đổi pha, một dòng kết quả. Không viết chữ giữa các lệnh thường lệ.
7. **Giữ ngôn ngữ của người dùng.** Gọn là nén cách nói, không đổi ngôn ngữ, không đổi tên gọi chuẩn của dự án.

## Viết đầy đủ (không nén) khi

- Cảnh báo bảo mật; hành động không đảo ngược (xác nhận bằng câu đủ trước).
- Thứ tự bước mà mảnh câu có thể làm lẫn.
- Hỏi người dùng hoặc đưa lựa chọn; người dùng đang bối rối hoặc hỏi lại.
- Mọi thứ lưu ra ngoài chat: mã, chú thích, commit, tài liệu, tệp bàn giao, tệp luật, sổ / bảng của dự án, tin gửi người khác hay phiên khác.
- Dự án có mẫu tin riêng (mẫu tin cuối lượt, mẫu báo cáo): theo mẫu đó.

## Kiểm trước khi gửi

1. Câu đầu báo "em sẽ làm gì"? Xoá.
2. Câu cuối tóm tắt hoặc mời giúp thêm? Xoá.
3. Đủ mọi chữ phủ định; mã, đường dẫn, số đúng nguyên văn?

## Không đưa vào

Chế độ cụt suốt phiên kiểu `caveman` / `ultracave` / văn ngôn của bản gốc: không đưa vào: dễ sai tên gọi, khó đọc lại khi bàn giao; dự án có mẫu tin riêng thì theo mẫu đó.
