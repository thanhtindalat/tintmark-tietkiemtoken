# Dọn ngữ cảnh và vòng lặp

Lệnh gọi: "dọn ngữ cảnh", "dọn phiên", "liệt kê vòng lặp". Dùng cho mọi dự án. Kết quả là **một bảng** rồi mới hành động.

## 1. Dọn ngữ cảnh của một phiên

1. Đo: số token hiện tại, nhóm chiếm nhiều nhất (tin nhắn / công cụ / connector / skill).
2. Ghi trạng thái ra tệp bàn giao trước (luôn làm trước khi dọn bất cứ gì).
3. ≥ 250k: đổi phiên theo `ban-giao.md`. Không nén tại chỗ.
4. < 250k nhưng đổi hẳn chủ đề: mở phiên mới cho chủ đề mới, phiên này giữ chủ đề cũ.
5. Thói quen giữ phiên gọn: lệnh in dài thì lọc / cắt đuôi (`| tail -40`, `grep`), đọc tệp theo đoạn, truy dữ liệu có lọc và giới hạn dòng, việc đọc rộng giao subagent.

## 2. Quét vòng lặp (mọi thứ tự chạy lại và tốn token)

Nguồn phải quét — có công cụ nào dùng công cụ đó, không có thì ghi "không quét được":

| Nguồn | Cách xem |
|---|---|
| Lịch tự chạy của app (scheduled tasks) | công cụ liệt kê lịch |
| Lịch chạy trên đám mây (routines) | công cụ / skill `schedule` |
| Cron trong phiên, `/loop`, hẹn giờ tự đánh thức | công cụ liệt kê cron của phiên |
| Tiến trình nền, theo dõi (monitor) của phiên | danh sách tác vụ nền |
| Lịch của hệ điều hành gọi `claude` | `crontab -l`, `launchctl list` (lọc bỏ `com.apple`) |
| Phiên bật điều khiển từ xa, phiên đang chạy không ai xem | danh sách phiên |

Bảng kết quả: tên · loại · tần suất · thuộc dự án nào · chủ (phiên / người) · lần chạy cuối · số phiên nó tạo ra mỗi tuần · đề xuất (giữ / tắt / giảm tần suất / hạ model) · lý do.

Xong thì chạy `cong_cu/vong_lap.py da-quet`.

## 3. Khi nào đề xuất tắt

| Dấu hiệu | Đề xuất |
|---|---|
| Dự án / phần việc đã tạm dừng hoặc kết thúc | Tắt |
| Đường dẫn, kho, công cụ mà lịch dùng không còn tồn tại | Tắt |
| 5 lần chạy gần nhất đều "không có việc mới" | Giảm tần suất hoặc tắt |
| Chạy dày hơn 1 lần / giờ | Giảm tần suất; cần lý do rõ mới giữ |
| Không rõ chủ, không ai đọc kết quả | Tắt |
| Trùng việc với lịch khác | Gộp, tắt cái thừa |
| Chạy model mạnh cho việc kiểm tra / chép dữ liệu | Giữ, hạ model |

## 4. Quy trình tắt có nhắc và có hạn (bắt buộc)

Không tắt im lặng, cũng không để treo vô hạn.

1. **Đề xuất.** Với mỗi vòng lặp nên tắt: nói rõ với người dùng (tên, tần suất, lý do, hệ quả khi tắt, cách bật lại) và ghi sổ:
   `python3 cong_cu/vong_lap.py de-xuat --id <id> --ten "<tên>" --loai lich --tan-suat "<…>" --ly-do "<…>" --du-an <gốc dự án> --han-gio 48`
2. **Nhắc.** Hook tự nhắc ở các phiên của dự án đó, tối đa 1 lần / 12 giờ, kèm hạn. Dự án có nơi duyệt tập trung thì ghi thêm vào đó.
3. **Người dùng đồng ý** → tạm dừng ngay, `vong_lap.py tra-loi --id <id> --tat` rồi `da-tat --id <id>`.
4. **Người dùng muốn giữ** → `tra-loi --id <id> --giu` (không hỏi lại trong 30 ngày).
5. **Quá hạn (mặc định 48 giờ) không trả lời** → hook báo `QUÁ HẠN`; phiên nhận được **tự tạm dừng**, chạy `da-tat --id <id> --tu-dong`, và báo người dùng một dòng: đã tự tắt gì, lúc nào, bật lại thế nào.
6. **Tự quét.** Sau 7 ngày kể từ lần quét cuối, hook gợi ý quét lại (mục 2). Vòng lặp mới xuất hiện cũng đi qua bước 1–5.

Luật an toàn:
- "Tắt" luôn là **tạm dừng**, không xoá định nghĩa lịch; bật lại được bằng một thao tác.
- Hạn tự tắt mặc định 48 giờ; vòng lặp ảnh hưởng người ngoài (gửi tin cho khách, phát hành, thanh toán) thì hạn 7 ngày và phải nêu rõ hệ quả.
- Cron / hẹn giờ do chính phiên này tạo cho việc đã xong: tắt luôn, chỉ báo.
- Không tắt tiến trình không thuộc Claude (máy chủ, dịch vụ hệ thống) theo quy trình này.

## 5. Lịch tự chạy còn giữ thì phải

- Chạy model nhỏ; lời nhắc của lịch ngắn, tự đủ.
- Bước đầu tiên là kiểm "có việc mới không" bằng lệnh rẻ; không có thì thoát ngay.
- Phiên do lịch tạo đặt tên `Lịch - <Dự án> - <Việc>` và tự lưu trữ khi xong.
- Có chủ (phiên hoặc người) ghi trong tệp bàn giao mục 6.

## 6. Dọn phiên của cả dự án

Bảng phiên: tên · token · hoạt động cuối · trạng thái · đề xuất.
- Phiên `Tạm`, `Lịch` đã xong; phiên tạm dừng; phiên đã có kế nhiệm → lưu trữ.
- Phiên > 300k còn dùng → đổi phiên khi có việc kế tiếp (không đánh thức chỉ để bàn giao, trừ khi chưa có tệp bàn giao).
- Tên sai quy tắc → `dat-ten-phien.md` mục 6.
- Sắp xếp, đổi tên phiên máy đặt, lưu trữ phiên đã xong: làm luôn rồi báo. Xoá hẳn: hỏi.

## 7. Cắt chi phí nền

- Connector: liệt kê connector của phiên; cái nào không phục vụ loại việc của phiên thì đề xuất tắt. **Không tự tắt connector người dùng đã nói giữ**; ghi danh sách "không được tắt" vào tệp luật của dự án.
- Skill: skill trùng nhau (cùng nội dung ở hai nơi cài) → đề xuất gỡ một bản; mô tả skill quá dài → rút gọn mô tả.
- Tệp luật nạp mỗi lượt (CLAUDE.md, bộ nhớ): giữ ngắn, chi tiết đẩy sang tệp tham chiếu đọc khi cần; không rút tới mức mất chữ phủ định, con số.
