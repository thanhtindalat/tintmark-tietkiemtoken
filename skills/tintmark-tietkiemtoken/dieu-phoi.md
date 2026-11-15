# Luật cho phiên điều phối (Claude Code và Claude Chat)

Phiên điều phối sắp xếp các phiên làm việc của một hoặc nhiều dự án. Nó dễ trở thành phiên tốn nhất vì sống lâu và nhắn nhiều.

## 1. Điều phối bằng tệp, không bằng hỏi đáp

- Nguồn sự thật là **sổ phiên** của dự án (một tệp, ví dụ `tham_chieu/phien.md` hoặc `ban_giao_phien/SO_PHIEN.md`): tên, id, phạm vi, model, tệp bàn giao, trạng thái (đang làm / rảnh / tạm dừng / đã lưu trữ), số token lần đo cuối.
- Muốn biết phiên X đang ở đâu: đọc tệp bàn giao của X. Không nhắn hỏi.
- Giao việc: một tin ngắn, đủ ngữ cảnh (mục tiêu, tệp, tiêu chí xong, nơi ghi kết quả); trỏ đường dẫn thay vì chép nội dung. Không nhắn rồi nhắn bổ sung.
- Mục xin người dùng duyệt: đủ ý trong một dòng — cần gì, vì sao, hệ quả (mỗi phương án).
- Nhận kết quả: phiên con ghi ra tệp, nhắn một dòng trỏ tệp.
- Không gửi thông báo chung cho mọi phiên. Luật chung ghi vào tệp luật của dự án; phiên tự đọc khi có việc.
- Không ghi cứng id phiên trong tệp luật (CLAUDE.md). Tệp luật chỉ nói "tra sổ phiên"; nếu không, mỗi lần đổi phiên phải sửa luật.

## 2. Trước khi nhắn một phiên

| Phiên nhận | Làm gì |
|---|---|
| < 300k, vừa hoạt động | Nhắn bình thường |
| Đã nghỉ quá 1 giờ, không có việc thật | Không nhắn (bộ đệm hết hạn, nạp lại cả ngữ cảnh giá gấp đôi). Có việc thật mà phiên nhỏ thì gom mọi ý vào một tin |
| > 350k hoặc đã nghỉ lâu mà phiên to | Không nhắn. Mở phiên kế nhiệm từ tệp bàn giao của nó rồi giao việc cho phiên mới |
| Không có tệp bàn giao, > 350k | Nhắn **một** tin duy nhất: "viết bàn giao theo tintmark-tietkiemtoken rồi dừng"; sau đó mở phiên kế nhiệm |
| Việc nhỏ, độc lập | Không dùng phiên dài hạn; mở phiên `Tạm` model nhỏ hoặc subagent |

## 3. Khi phiên làm việc đầy

Phiên đó tự làm theo `ban-giao.md` (hook nhắc nó). Điều phối chỉ: nhận dòng báo "cũ → mới", sửa sổ phiên, từ đó chỉ nhắn phiên mới. Phiên con không tự làm được (treo, hết hạn mức): điều phối mở phiên kế nhiệm bằng **lệnh bàn giao** ở dòng đầu tệp bàn giao của nó.

**Mở hộ phiên kế nhiệm** (phiên con nhắn "nhờ mở hộ"): ghi lại yêu cầu; ở **lượt người dùng gõ kế tiếp** tại phiên điều phối, `list_sessions` tìm tên mới — chưa có thì `start_session` "user_asked", "fresh", tên mới, lời giao = lệnh bàn giao ở dòng đầu tệp bàn giao; đã có thì thôi. Không tạo thẻ chờ bấm. Ghi id mới vào sổ phiên. Hai nơi cùng mở (điều phối và người dùng bấm thẻ cũ) thì giữ phiên đã nhận việc, phiên kia dừng và lưu trữ.

## 4. Khi chính phiên điều phối đầy

Như `ban-giao.md`, thêm:
1. Tệp bàn giao của điều phối kèm đường dẫn sổ phiên và danh sách việc đã giao chưa có kết quả.
2. Sửa dòng "Điều phối" trong sổ phiên sang id mới. Không báo từng phiên con — chúng đọc sổ khi cần liên hệ.
3. Lịch tự chạy đang báo về phiên điều phối cũ: chuyển sang phiên mới.
4. Phiên điều phối nên đặt ngưỡng thấp (150k / 200k) và chạy Sonnet / Haiku vì việc của nó là đọc tệp và chuyển tin; đọc rộng thì giao subagent.

## 5. Khi dự án càng ngày càng tốn

Chạy `cong_cu/do_token.py 7`, rồi xử theo thứ tự:
1. Phiên có đỉnh ngữ cảnh > 350k: đổi phiên, bắt đầu từ các phiên chiếm nhiều chi phí nhất.
2. Phiên sổ sách đang chạy model mạnh: hạ model (`chon-model.md`).
3. Số lần ghi lại cache nguội cao: đang nhắn qua lại nhiều → áp mục 1 và 2 ở trên.
4. Phiên tạm dừng, phiên `Tạm` / `Lịch` cũ: lưu trữ, tắt điều khiển từ xa.
5. Vòng lặp: rà theo `don-ngu-canh.md`.
6. Chi phí nền > 50k: cắt connector / skill thừa.
7. Thói quen "một phiên cho một phòng ban, sống vô hạn" → chuyển sang "một việc lớn = một phiên có đầu có cuối"; phiên dài hạn chỉ giữ cho vai trò thật sự liên tục (điều phối, phát hành).

## 6. Mở phiên mới cho một việc

Trước khi mở: (a) đã có phiên cùng `<Dự án> - <Phạm vi> - <Việc>` chưa — có thì dùng nó hoặc kế nhiệm của nó; (b) chọn model theo việc; (c) tên theo `dat-ten-phien.md`; (d) lời giao việc tự đủ, không "như đã bàn"; (e) ghi vào sổ phiên.

## 7. Điều phối trên Claude Chat

Chat không nhắn được sang phiên khác và không mở phiên hộ. Phiên điều phối trên Chat chỉ: giữ sổ phiên (tệp trong Project), soạn lời giao việc để người dùng dán vào chat / phiên Code tương ứng, đọc tệp bàn giao người dùng tải lên. Xem `claude-chat.md`.
