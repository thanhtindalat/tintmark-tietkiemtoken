# Phê duyệt bằng giọng nói (Claude Code ↔ Claude Chat qua Google Drive)

Người dùng duyệt / ra chỉ đạo bằng giọng trên app Claude điện thoại thay vì gõ trong phiên Code. Cầu nối là **một thư mục Google Drive đồng bộ trên máy**: phiên Code ghi tệp vào đó (0 token), Chat đọc / ghi qua connector Google Drive. Dùng cho mọi dự án. Chỉ có ở plugin (Claude Code); phía Chat làm theo `claude-chat.md` mục 6.

## 1. Điều kiện (một lần)

- App Google Drive máy tính đăng nhập **đúng tài khoản của connector Google Drive trong Claude** (thư mục `~/Library/CloudStorage/GoogleDrive-<tài khoản>/My Drive`). Khác tài khoản thì Chat không thấy tệp.
- Ghi tài khoản đó vào `cau_hinh.json` của plugin (thư mục dữ liệu plugin): `{"cau_noi": {"tai_khoan": "<email connector Drive>"}}`, hoặc chỉ thẳng thư mục `{"cau_noi": {"drive": "<thư mục>"}}`. Không đặt thì lệnh báo lỗi, không đoán (tránh ghi nhầm vào Drive mà Chat không thấy).
- Kiểm: `python3 $P/scripts/cau_noi.py thu-muc` (`P` = thư mục plugin, như `SKILL.md` mục Công cụ). Lỗi thì in cách sửa.

## 2. Phiên Code làm

1. Viết câu hỏi ra tệp tạm: mỗi câu một dòng đánh số `1.` (hoặc `Câu 1:`), câu ngắn, kèm lựa chọn `A: … B: …` và đề xuất. Đủ ý để quyết tại chỗ (cần gì, vì sao, hệ quả).
2. `python3 $P/scripts/cau_noi.py tao --du-an "<dự án>" --ten "<tên ngắn>" --tu <tệp câu hỏi>` → tạo `<Drive>/dieu_phoi/<du_an>/<ten>.md`, đầu tệp có giao thức cho Chat.
3. Canh nền (0 token khi chờ): Bash `run_in_background` chạy `python3 $P/scripts/cau_noi.py canh --ten <ten>` (mặc định chờ 24 giờ, kiểm mỗi 30 giây). Có tệp kết quả thì lệnh thoát → phiên tự thức.
4. Báo người dùng một dòng: "Mở Claude trên điện thoại, nói: đọc tệp phê duyệt `<ten>`."
5. Kết quả về (lệnh canh thoát, hoặc hook đầu lượt báo `CÓ KẾT QUẢ PHÊ DUYỆT`): đọc tệp `ket_qua_<ten>_<giờ>.md` → **ghi sổ hỏi đáp dự án trước** (`ban-giao.md` mục 2b) → làm việc được duyệt; chỉ đạo mới ghi sổ yêu cầu của dự án → `cau_noi.py da-doc <tệp>`.

Tệp điều phối: `cau_noi.py ban-sao --du-an "<dự án>" --tu <tệp điều phối>` chép **bản sao chỉ đọc** (ghi đè bản sao cũ mỗi lần chép) kèm giao thức nhận chỉ đạo; chỉ đạo về lại thành tệp `ket_qua_…` như trên.

Phiên đã tắt khi tệp về: hook `UserPromptSubmit` báo ở lượt kế tiếp của bất kỳ phiên nào trong cùng thư mục dự án (mỗi tệp tối đa 1 lần / 6 giờ, mục chờ quá 14 ngày thì thôi). Tắt: module `cau_noi`.

## 3. Giới hạn đã biết

- Connector Drive **không ghi đè** nội dung tệp có sẵn → Chat luôn tạo tệp mới `ket_qua_…`; phiên Code không chờ tệp gốc đổi.
- Chat tạo nhầm Google Docs (`.gdoc`) thay vì `.md`: hook vẫn báo, nhưng phải đọc bằng connector Drive.
- **Chưa kiểm:** chế độ giọng nói (voice mode) của app Claude có gọi connector / skill không. Dự phòng: chat thường, bấm nút micro để đọc chính tả câu trả lời và nút "đọc to" để nghe câu hỏi; giao thức nằm ngay đầu tệp nên Chat không cần skill vẫn làm đúng.
- Drive đồng bộ có độ trễ (vài giây tới vài phút); lệnh canh kiểm mỗi 30 giây.
- Chi phí: phía Code gần 0 (chỉ đọc kết quả); phía Chat tính theo gói Claude của người dùng.
