# Vì sao tốn token — cách tính tiền

## Sáu điều cần hiểu

1. **Mỗi lượt gọi model gửi lại toàn bộ phiên** (lời hệ thống + công cụ + toàn bộ lịch sử). Chi phí một lượt tỉ lệ với kích thước ngữ cảnh. Phiên 900k đắt khoảng 4,5 lần phiên 200k cho cùng một việc.
2. **Một tin người dùng không phải một lượt gọi.** Mỗi lần dùng công cụ là thêm một lượt đọc lại. Đo thật: trung bình khoảng 10 lượt cho 1 tin. Việc 10 bước trong phiên 600k = 6 triệu token đọc lại.
3. **Cache.** Phần đã gửi ở lượt trước được tính 0,1 giá (đọc cache). Cache hết hạn sau một khoảng nghỉ (5 phút, có nơi 1 giờ). Lượt đầu sau khi cache nguội phải **ghi lại toàn bộ với giá 1,25**. Đánh thức phiên 800k đã nguội ≈ 1 triệu token quy đổi chỉ để nó nhớ lại.
4. **Đầu ra đắt gấp 5 đầu vào** nhưng thường chỉ chiếm dưới 10% tổng. Trả lời gọn có ích, không phải đòn chính.
5. **Chi phí nền.** Lời hệ thống, định nghĩa công cụ, công cụ của connector (MCP), danh sách skill được gửi ở **mọi lượt của mọi phiên**. Thường 40–70k. Cắt connector / skill thừa lợi hơn tưởng.
6. **Phiên mới không miễn phí.** Chi phí nền + đọc bàn giao (5–10k) + đọc lại tệp cần. Đổi phiên khi chưa tới 100k là lỗ.

## Quy đổi nhanh (đơn vị: token đầu vào giá gốc)

| Loại | Hệ số |
|---|---|
| Đầu vào mới | 1 |
| Ghi cache | 1,25 |
| Đọc cache | 0,1 |
| Đầu ra | 5 |

Model: Haiku rẻ hơn Sonnet, Sonnet rẻ hơn Opus nhiều lần; hệ số trên áp trong từng model.

## Đòn nào đáng làm trước

| Đòn | Tác động vào | Mức |
|---|---|---|
| Giữ phiên ≤ 300k (đổi phiên có bàn giao) | đọc cache | lớn nhất |
| Không đánh thức phiên to nguội; gom tin | ghi cache | lớn |
| Model nhỏ cho việc sổ sách, lịch, dò tìm | giá mỗi token | lớn |
| Cắt connector / skill thừa | chi phí nền mọi lượt | vừa |
| Nén kết quả lệnh (plugin tintmark-tietkiem, cắt đuôi log) | tốc độ phình của phiên | vừa |
| Trả lời gọn | đầu ra | nhỏ |

## Số đo trên máy bạn

Chạy `cong_cu/do_token.py 7` để biết chi phí nằm ở đâu (đọc cache, ghi cache, đầu ra, phiên lớn). Số đo riêng của máy (nếu đã lưu) để ở `~/.claude/tintmark-token/so_do_mau.md`, không đưa vào skill.
