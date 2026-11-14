# tintmark-token trên Claude Chat (claude.ai, app điện thoại)

Chat không có hook, không có đồng hồ token, không tự mở chat mới, không nhắn được sang chat khác. Vì vậy mọi thứ dựa vào **dấu hiệu** và **tệp**.

## 1. Khi nào dừng chat để mở chat mới

Coi như đã tới ngưỡng "nhắc" khi có một trong các dấu hiệu:
- Khoảng 30–40 lượt hỏi đáp, hoặc 15–20 lượt nếu có tệp / ảnh / kết quả công cụ dài.
- Đã dán hoặc tải lên tài liệu dài (trên ~50 trang) và đã xử lý xong phần cần.
- Claude bắt đầu quên luật đã thống nhất, lặp lại câu hỏi, nhầm phiên bản.
- App báo cuộc trò chuyện dài / gần hết hạn mức.
- Đổi sang chủ đề khác.

Khi thấy dấu hiệu, Claude nói ở **câu đầu**: "Cuộc trò chuyện đã dài, nên bàn giao sang chat mới." rồi làm mục 2. Người dùng hỏi "còn bao nhiêu token" thì trả lời thật: không đo được chính xác trên Chat, chỉ ước theo dấu hiệu.

## 2. Bàn giao

Người dùng gõ "bàn giao" (hoặc Claude tự đề xuất): tạo tệp bàn giao 7 mục theo mẫu `ban-giao.md` (dạng tệp tải về hoặc artifact), dòng đầu là lệnh bàn giao. Người dùng mở chat mới **trong cùng Project**, đính tệp, gõ đúng lệnh bàn giao. Chat mới xác nhận 3 dòng rồi làm tiếp.

Tên chat mới: tên cũ + số (`dat-ten-phien.md`) — người dùng đổi tên trong app; Claude nhắc tên cần đặt.

Chat cũ: để nguyên, không hỏi tiếp trong đó. Cần chi tiết cũ thì dùng tìm kiếm trò chuyện.

## 3. Giữ chat gọn

- Tài liệu nền (bảng giá, hồ sơ công ty, quy tắc) đưa vào **Project** một lần, không dán lại mỗi chat.
- Hướng dẫn của Project ghi: model chuẩn, khuôn tên chat, vị trí tệp bàn giao.
- Một chat một việc. Hỏi nhanh ngoài lề → chat `Tạm`.
- Yêu cầu Claude trả kết quả dài ra tệp / artifact, trong chat chỉ tóm tắt.
- Tắt connector, tìm web, suy nghĩ mở rộng khi câu hỏi không cần.
- Sửa câu hỏi cũ (edit) thay vì hỏi nối thêm khi câu trả lời đi lệch — nhánh lệch không còn nằm trong ngữ cảnh.

## 4. Chọn model

Theo `chon-model.md` mục 4.

## 5. Điều phối chung Chat + Code

Một thư mục / Project giữ **sổ phiên** và các tệp bàn giao cho cả hai nơi. Phiên điều phối (ở đâu cũng được) soạn lời giao việc; việc cần sửa mã, chạy lệnh, lịch tự chạy → phiên Claude Code; việc tư vấn, viết, phân tích tài liệu → Chat. Kết quả từ Chat muốn vào dự án thì người dùng lưu tệp vào thư mục dự án; phiên Code đọc tệp đó, không ai chép lại bằng lời.
