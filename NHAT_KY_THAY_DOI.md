# Nhật ký thay đổi — tintmark-tietkiemtoken

## 0.7.1 — 15/11/2026
- Dữ liệu mẫu trong test_cau_noi trung tính (bộ quét công khai); không đổi hành vi.

## 0.7.0 — 15/11/2026
- Module cau_noi: phê duyệt bằng giọng nói qua thư mục Google Drive đồng bộ (scripts/cau_noi.py tao / ban-sao / canh / chua-doc / da-doc; tài khoản Drive đặt trong cau_hinh.json, không đoán), hook đầu lượt báo kết quả phê duyệt chưa đọc (tối đa 1 lần / 6 giờ mỗi tệp). Luật bàn giao: mỗi dự án một sổ hỏi đáp, ghi sổ trước khi trả lời, phiên kế nhiệm đọc sổ trước (ban-giao.md mục 2b, lệnh bàn giao mẫu). Kế nhiệm 250k/300k: lượt người dùng gõ mở thẳng user_asked (kể cả việc theo luật thường trực), lượt tự động nhờ phiên điều phối mở hộ thay vì để thẻ chờ bấm, list_sessions chống mở trùng; dieu-phoi.md mục mở hộ. Skill: phe-duyet-giong-noi.md, claude-chat.md mục 6. Test 91.

## 0.6.0 — 15/11/2026
- Luật đổi phiên: (1) module ban_giao — hook PostToolUse báo [tintmark-tietkiemtoken] BÀN GIAO DÀI khi ghi ban_giao_phien/*.md (Write/Edit/Bash) quá ban_giao_chu (mặc định 1.500 chữ, 0 = tắt), không chặn; (2) ở 300k lời nhắc đổi thành 'lưu trữ phiên TRƯỚC ĐÓ nếu có, GIỮ phiên này' (trước: lưu trữ phiên này, trái luật 2 phiên mới nhất); (3) phiên kế nhiệm detach_session "self" trước mọi bước lưu trữ (lệnh bàn giao mẫu, lời nhắc hook, SKILL.md). Test 80.

## 0.5.2 — 15/11/2026
- Khung 0.2.1: miễn dòng bản quyền cho mã bên thứ ba khai trong khung.json ma_ben_thu_ba kèm NOTICE ở thư mục cha (cho gói khác dùng khung); plugin này không có mã bên thứ ba, hành vi không đổi.

## 0.5.1 — 15/11/2026
- Bỏ tên người trong ghi chú mã (bộ quét công khai chặn); không đổi hành vi.

## 0.5.0 — 15/11/2026
- GĐ4 hội viên: thuật toán Ed25519 Python thuần (RFC 8032, chọn 15/11) trong hoi_vien.py, khoá công khai trong hoi_vien.json; cơ chế vẫn TẮT (bat:false, chưa thu phí A198), fail-open, kiểm cục bộ. Khung 0.2.0: cong_cu/cap_khoa.py (tạo khoá, ký; không đi theo plugin). Gồm sửa 0.4.1. Test 75.

## 0.4.1 — 15/11/2026
- Hook nén bỏ qua output ≥ 30.000 ký tự (Claude Code tự cất output gốc, bản nén không tới model; thống kê không còn tính ảo); thêm cap_nhat.py thu-khoi [thư mục] để kiểm hook bản cài bằng dữ liệu tạm thay cho gọi tay (gọi tay đã ghi 2 dòng giả vào sổ thống kê thật); khung 0.1.1; test 72.

## 0.4.0 — 15/11/2026
- Dùng khung plugin bản quyền 0.1.0: bật/tắt module (module.py: nen, tu_sua, nguong, vong_lap, tu_cap_nhat), cơ chế hội viên mặc định tắt (hoi_vien.py, kiểm cục bộ, fail-open), cập nhật cài bằng bản sao thật thay liên kết, thử khói đọc khung.json; README tóm tắt tiếng Anh khớp LICENSE.

## 0.3.10 — 15/11/2026
- Bản quyền: LICENSE độc quyền (được xem, cài dùng cá nhân; cấm sao chép / phân phối lại / bán khi chưa có văn bản), NOTICE, dòng bản quyền đầu mọi tệp mã, chân SKILL.md / README, 'by Tintmark' ở thong_ke.py và do_token.py, plugin.json license SEE LICENSE IN LICENSE; test kiểm.

## 0.3.9 — 15/11/2026
- Mô tả SKILL.md rút còn 292 ký tự / 351 byte (trước ~1.000 ký tự / ~1.240 byte, vượt giới hạn 1.024 của claude.ai); test giới hạn 320 ký tự và 1.024 byte.

## 0.3.8 — 15/11/2026
- Theo bản đổi tên: ban-giao.md mục Phiên con: list_sessions không cho thấy cha – con; dò get_session tìm parentSessionId (cả cháu), detach_session phiên còn dùng, lỡ kéo theo thì unarchive_session. Thêm test.

## 0.3.7 — 15/11/2026
- cap_nhat.py thử khói tìm hook ngưỡng theo mẫu skills/*/cong_cu/nguong_token.py (bản cũ 0.3.5 kiểm đường skill cũ nên tự quay lui khi lên 0.3.6).

## 0.3.6 — 15/11/2026
- Đổi tên thống nhất: plugin, skill, thư mục, thẻ hook -> tintmark-tietkiemtoken; vẫn đọc dữ liệu tên cũ (plugin-tintmark-tietkiem, plugin-nen-token, ~/.claude/tintmark-token, .claude/tintmark-token.json); doi_ten.py có --tu/--sang/--skill-tu/--skill-sang.

## 0.3.5 — 15/11/2026
- cap-nhat.md: kênh từ xa chính thức là marketplace GitHub (cài / cập nhật bằng claude plugin marketplace)

## 0.3.4 — 15/11/2026
- Mỗi chuỗi phiên (tên cũ + số, dòng Chuỗi phiên, các lần chạy của một lịch) chỉ hiện 2 phiên mới nhất, còn lại archive_session ngay; ghi chú detach_session phiên con còn dùng trước khi lưu trữ cha, gọi lại khi hook thêm trường session, phiên đang chạy / đang mở để lần sau

## 0.3.3 — 15/11/2026
- Đổi phiên: phiên kế nhiệm bắt buộc gọi archive_session lưu trữ mọi phiên cũ trong Chuỗi phiên (kể cả phiên ngay trước) và ghi id mới vào sổ phiên

## 0.3.2 — 15/11/2026
- Luật gọn (15/11): tệp bàn giao dưới ~1.500 chữ chỉ trỏ đường dẫn; lời giao kế nhiệm = lệnh bàn giao + việc mới nguyên văn; dò tìm / đọc nhiều tệp giao subagent; gom lệnh, truy bảng lọc + giới hạn dòng; mục xin duyệt một dòng; không đánh thức phiên nghỉ quá 1 giờ (luật vàng 3); phiên Yêu cầu / Báo cáo / Điều phối chạy Sonnet / Haiku; rút gọn lời nhắc hook

## 0.3.1 — 15/11/2026
- Lưu trữ phiên cũ: mẫu lệnh bàn giao có bước lưu trữ theo dòng Chuỗi phiên; hook NHẮC đòi id thật và báo id phiên hiện tại; lời giao phiên kế nhiệm có bước lưu trữ; ban-giao.md ghi thứ tự từ cũ nhất (kéo theo phiên con), gọi lại khi lỗi hook ở auto mode, cách báo khi công cụ từ chối; cai_dat.py trang-thai báo bản Claude Code ghi nhận và cảnh báo lệch; test mới

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
