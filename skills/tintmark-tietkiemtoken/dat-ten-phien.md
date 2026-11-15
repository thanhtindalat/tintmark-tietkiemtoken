# Quy tắc đặt tên phiên

Tên phiên là thứ duy nhất người dùng và phiên điều phối nhìn thấy khi chọn phiên. Tên sai dẫn tới nhắn nhầm phiên, mở trùng phiên, giữ phiên rác.

## 1. Khuôn tên

```
<Dự án> - <Phạm vi> - <Việc>[ (trạng thái)][ <số>]
```

| Phần | Quy tắc | Ví dụ |
|---|---|---|
| Dự án | Mã ngắn 2–8 ký tự, cố định cho cả dự án. Dự án có nhiều nhóm sản phẩm thì dùng mã nhóm | `TI`, `Admin`, `Web`, `Shop` |
| Phạm vi | Phòng ban / khối / phần hệ thống. Phiên dùng chung cả dự án ghi `Khung` hoặc `Chung` | `Kinh doanh`, `Máy chủ`, `Khung` |
| Việc | Danh từ ngắn, tối đa 5 từ, không ngày tháng, không mã yêu cầu | `Săn khách FB`, `Phát hành` |
| Trạng thái | Chỉ dùng `(tạm dừng)`; hết tạm dừng thì bỏ | `(tạm dừng)` |
| Số | Số kế nhiệm, xem mục 3 | `2`, `3` |

Dự án đã có khuôn riêng (ví dụ `<Khối> - <Giải pháp>`, `Khung - <Việc>`) thì giữ khuôn đó; chỉ thêm quy tắc số và tiền tố loại phiên dưới đây.

Dự án nhỏ một phiên: `<Dự án> - <Việc>` là đủ.

## 2. Tiền tố theo loại phiên

| Loại | Tên | Vòng đời |
|---|---|---|
| Phiên làm việc dài hạn | theo khuôn mục 1 | Đổi phiên theo ngưỡng, có số |
| Phiên điều phối | `<Dự án> - Khung - Điều phối` | Như trên; mỗi dự án đúng một phiên điều phối đang sống |
| Phiên do lịch tự chạy tạo | `Lịch - <Dự án> - <Việc>` | Tự lưu trữ sau khi chạy xong |
| Phiên một lần (hỏi nhanh, thử) | `Tạm - <Việc>` | Lưu trữ khi xong việc; không bàn giao |
| Phiên kiểm / đánh giá độc lập | `<Dự án> - Kiểm - <Việc>` | Lưu trữ khi có kết quả |

## 3. Số kế nhiệm

- Phiên gốc không mang số (coi là 1). Kế nhiệm đầu tiên là ` 2`, rồi ` 3`…
- Số = "Số phiên đã tạo" trong tệp bàn giao + 1. Không đoán từ danh sách phiên.
- Phần trước số giữ **nguyên văn** tên phiên cũ (kể cả dấu). Ví dụ `Khung - Máy chủ` → `Khung - Máy chủ 2` → `Khung - Máy chủ 3`.
- Phiên cũ sau khi bàn giao: giữ nguyên tên, lưu trữ. Không thêm "(cũ)", "(đã chuyển)".
- Tên tệp bàn giao không mang số: `khung_may_chu.md` dùng cho cả dòng phiên.

## 4. Không làm

- Không để tên do máy tự sinh ("Fix bug in…", "Thiết kế skill…") cho phiên dài hạn — đặt lại ngay lượt đầu.
- Không ghi ngày, mã yêu cầu, số bản phát hành, tên người vào tên phiên.
- Không ghi chú lịch sử vào tên (`(cũ: V1)`, `(fork)`, `(viết tay)`).
- Không có hai phiên đang sống trùng phần `<Dự án> - <Phạm vi> - <Việc>`; trùng thì gộp, phiên thừa lưu trữ.
- Không đổi tên phiên người dùng tự đặt khi chưa hỏi (app sẽ hỏi xác nhận).

## 5. Tên đi kèm

| Thứ | Quy tắc |
|---|---|
| Tệp bàn giao | tên phiên → chữ thường, không dấu, gạch dưới, bỏ số: `ti_kinh_doanh_san_khach_fb.md` |
| Nhóm ở thanh bên | một nhóm cho mỗi dự án; phiên `Tạm`, `Lịch` không vào nhóm |
| Nhánh / worktree | theo luật dự án; không lấy số kế nhiệm của phiên |

## 6. Rà tên (khi dọn phiên)

Liệt kê phiên → đánh dấu: sai khuôn, trùng việc, tên máy sinh, thiếu số, phiên `Tạm` / `Lịch` chưa lưu trữ. Đổi tên phiên do máy đặt thì làm luôn; phiên người dùng đặt thì đưa bảng "tên cũ → tên đề xuất" để duyệt một lần.
