# Nhật ký thay đổi — tintmark-tietkiem

## 0.3.0 — 15/11/2026
- Đổi tên plugin nen-token -> tintmark-tietkiem (dữ liệu ~/.claude/plugin-tintmark-tietkiem, đọc tiếp thư mục cũ; scripts/doi_ten.py chuyển máy + quay lui); luật git-ghi (push/pull/commit/branch…); nén lệnh dạng cd X && <lệnh đơn>; hook báo phản hồi mở quá 3 ngày; lệnh /tintmark-tietkiem:phan-hoi; luật phat-hanh chuyển sang luật riêng máy; mẫu mau/ thay bằng kho mẫu tổng hợp; tài liệu trung tính, README có tóm tắt tiếng Anh và ghi chưa cấp phép

## 0.2.7 — 15/11/2026
- sap-xep-phien.md sửa theo lượt chạy thử thật (697 phiên): liệt kê một lần rồi xử lý bằng script, chuẩn hoá thư mục, nhóm phẳng, thẻ cụm tự sinh, giới hạn công cụ tìm, tên công cụ thật

## 0.2.6 — 15/11/2026
- Gộp phần hay từ một skill token cũ vào skill: tra-loi-gon.md, nen-tep-nho.md, subagent-nen.md, do-trung-thuc.md; thêm test kiểm mô tả SKILL.md ≤ 1024 ký tự và tệp được nhắc phải có

## 0.2.5 — 15/11/2026
- SKILL.md: thêm dòng và từ gọi cho phiên Sắp xếp - tìm kiếm (0.2.4 phát thiếu phần này), mô tả rút còn dưới 1024 ký tự

## 0.2.4 — 15/11/2026
- Skill: thêm sap-xep-phien.md (phiên Sắp xếp - tìm kiếm: xếp phiên theo dự án, thẻ đề xuất đổi tên / lưu trữ / xoá, tìm phiên theo từ khoá)

## 0.2.3 — 15/11/2026
- Đổi phiên: từ ngưỡng đổi, hook nhắc ở mọi lượt người dùng và bảo mở phiên kế nhiệm kèm nguyên văn tin vừa gửi; lượt do phiên khác gửi thì tạo thẻ đề xuất; mức nhắc bảo tạo một thẻ đề xuất mỗi phiên; giữ tin vài giây khi quá ngưỡng (cho_giay, mặc định 8, không chặn); câu báo mới; ban-giao.md thêm Chuỗi phiên và quy tắc chỉ giữ 1 phiên trước

## 0.2.2 — 15/11/2026
- Tài liệu: viết lại nen-token.md (bỏ rtk), thêm phan-hoi.md, tu-sua.md, cap-nhat.md, sửa SKILL.md, viết lại README (cài, đo, phản hồi, cập nhật, gỡ)

## 0.2.1 — 15/11/2026
- docker-list: không cắt cột NAMES ở cuối dòng (max_line_len 180→400); hook trước: auto mode không đổi lệnh nào (phản hồi PH-261115-015523-ac85, PH-261115-015523-c9fb)

## 0.2.0 — 15/11/2026
- Nén ở PostToolUse (updatedToolOutput) thay cho đổi lệnh: hết xung đột auto mode, lệnh lỗi không bao giờ bị nén. Gộp skill tintmark-token + hook ngưỡng vào plugin. Sổ phản hồi, tự ghi dấu nghi hỏng, tự tắt bộ lọc, tự sửa, phát bản, cập nhật có kiểm băm / test / thử khói, quay lui. Luật git nhận git -C. Sửa sổ vòng lặp bị bỏ rơi sau khi đổi tên skill.
