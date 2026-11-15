---
name: tintmark-token
description: Tiết kiệm token, dùng cho MỌI dự án trên Claude Code và Claude Chat — ngưỡng 250k nhắc / 300k đổi phiên (hook tự đo), tệp bàn giao 7 mục, mở phiên kế nhiệm và đặt tên phiên cũ + số, quy tắc đặt tên phiên, phiên "Sắp xếp - tìm kiếm" (xếp phiên theo dự án, tìm phiên theo từ khoá), xử lý phiên cũ, phiên điều phối đầy, chọn model theo việc, dọn ngữ cảnh, trả lời gọn, nén tệp nhớ (CLAUDE.md), giao subagent trả kết quả nén, liệt kê và tắt vòng lặp / lịch tự chạy có nhắc và hạn tự tắt, cắt connector / skill thừa, plugin tintmark-tietkiem nén output bash (báo nén sai, tự sửa, cập nhật), đo token trung thực. Dùng khi nói "tiết kiệm token", "hết token", "phiên dài", "bàn giao", "đổi phiên", "đặt tên phiên", "sắp xếp phiên", "tìm phiên", "vòng lặp", "lịch tự chạy", "chọn model", "trả lời gọn", "nén CLAUDE.md", "subagent", "nén output", "nén sai", "tintmark-tietkiem", "cập nhật plugin", "đo token", "tintmark-token"; khi hook báo "[tintmark-token]"; khi bắt đầu một phiên điều phối; và ngay lượt đầu của mọi phiên dài hạn.
---

# tintmark-token

Quy trình chính về token cho mọi dự án (gồm cả trả lời gọn, nén tệp nhớ, subagent nén, đo trung thực). Không gắn với dự án nào: mọi đường dẫn tính từ **gốc dự án của phiên** (thư mục làm việc). Dự án có luật riêng (CLAUDE.md) thì luật riêng thắng khi trái nhau.

## 8 luật vàng

1. **Phiên to là tốn nhất.** Mỗi lượt gọi model đọc lại cả phiên. Nhắc ở 250k, đổi phiên trước 300k. Không chờ tự nén.
2. **Trạng thái nằm ngoài chat, viết gọn.** Mục tiêu, việc dở, quyết định ghi ra tệp bàn giao ở mỗi mốc việc. Tệp bàn giao dưới khoảng 1.500 chữ, chỉ trỏ đường dẫn, không chép nội dung; lời giao phiên kế nhiệm chỉ gồm lệnh bàn giao + việc mới nguyên văn.
3. **Không đánh thức phiên đã nghỉ quá 1 giờ khi không có việc thật.** Bộ đệm đã hết hạn: lượt đầu nạp lại cả ngữ cảnh với giá ghi gấp đôi. Mở phiên mới nhỏ, hoặc đọc tệp trạng thái của nó.
4. **Kết quả ra tệp, ngữ cảnh chính chỉ nhận kết luận.** Giữa các phiên chỉ gửi "xong X, xem `<tệp>`"; gom nhiều ý vào một tin. Dò tìm / đọc nhiều tệp: giao subagent. Gom nhiều lệnh vào một lượt; truy bảng luôn lọc + giới hạn dòng; không in cả tệp, cả nhật ký. Không đọc bản luật đầy đủ / tệp tham chiếu dài trừ khi thật cần.
5. **Model theo việc.** Phiên yêu cầu / ghi sổ, báo cáo, điều phối: Sonnet hoặc Haiku. Opus (model mạnh) cho mã khó, kiến trúc, phát hành. Xem `chon-model.md`.
6. **Vòng lặp phải có chủ và có hạn.** Lịch tự chạy nào cũng được liệt kê, hỏi, và tự tắt khi quá hạn không ai trả lời. Xem `don-ngu-canh.md`.
7. **Tên phiên theo quy tắc.** Tên nói được dự án – phạm vi – việc – số kế nhiệm. Xem `dat-ten-phien.md`.
8. **Không nhận "đã tiết kiệm" khi chưa đo.** Đo bằng `cong_cu/do_token.py`, so cùng kỳ; chưa đo thì ghi "ước tính".

## Khi nào mở tệp nào

| Tình huống | Tệp |
|---|---|
| Hook báo `[tintmark-token]`, phiên sắp đầy, cần đổi phiên, phiên cũ làm gì | `ban-giao.md` |
| Đặt / đổi tên phiên, mở phiên mới, sắp xếp danh sách phiên | `dat-ten-phien.md` |
| Sắp xếp mọi phiên theo dự án, đổi tên hàng loạt, đề xuất lưu trữ / xoá, tìm phiên cũ theo từ khoá (phiên `Sắp xếp - tìm kiếm`) | `sap-xep-phien.md` |
| Đang là phiên điều phối; phiên con đầy; điều phối đầy; dự án càng ngày càng tốn | `dieu-phoi.md` |
| Chọn model / mức nỗ lực cho phiên, subagent, lịch; sắp xếp lại model cả dự án | `chon-model.md` |
| Dọn ngữ cảnh, liệt kê / tắt vòng lặp, cắt connector và skill thừa | `don-ngu-canh.md` |
| Muốn câu trả lời ngắn, ít token đầu ra mà không mất dữ kiện | `tra-loi-gon.md` |
| CLAUDE.md / AGENTS.md / MEMORY.md dài, luật trùng nhiều tệp, chỉ mục bộ nhớ quá dài | `nen-tep-nho.md` |
| Giao subagent dò tìm / sửa / review: hợp đồng đầu ra ngắn `đường_dẫn:dòng` | `subagent-nen.md` |
| Báo "đã tiết kiệm bao nhiêu", đánh giá một thay đổi tối ưu, giữ cache | `do-trung-thuc.md` |
| Nén output lệnh bash: cách hoạt động, đo, lấy output đầy đủ (`NEN_OFF=1`), tắt | `nen-lenh.md` |
| Output nén thiếu dòng / sai, hook nhắc sai: ghi phản hồi, bộ lọc tự tắt | `phan-hoi.md` |
| Có phản hồi mở hoặc bộ lọc bị tắt: tái hiện, sửa luật, phát bản vá | `tu-sua.md` |
| Cập nhật, quay lui, phát bản, gộp skill vào plugin, gỡ | `cap-nhat.md` |
| Làm việc trên Claude Chat (claude.ai) | `claude-chat.md` |
| Giải thích vì sao tốn, cách tính tiền | `thuat-toan.md` |

## Việc làm ngay ở lượt đầu của phiên dài hạn

1. Xác định tên phiên đúng quy tắc (`dat-ten-phien.md`); sai thì đề xuất tên đúng.
2. Tạo / cập nhật tệp bàn giao của phiên với **lệnh bàn giao** ở dòng đầu (`ban-giao.md` mục 2) — để lúc nào cũng mở được phiên kế nhiệm bằng một câu.
3. Phiên kế nhiệm: đọc tệp bàn giao, xác nhận 3 dòng (mục tiêu, bước kế tiếp, tệp đang sửa), gọi `archive_session` lưu trữ mọi phiên cũ hơn 2 phiên mới nhất của chuỗi (bắt buộc; `ban-giao.md` mục 4), ghi id mới vào sổ phiên, rồi làm.

## Công cụ

- `cong_cu/nguong_token.py` — hook đo ngưỡng (plugin tintmark-tietkiem tự nối qua `hooks/hooks.json`); dưới ngưỡng thì im lặng.
- `cong_cu/do_token.py [số ngày]` — báo cáo token theo phiên từ nhật ký trên máy.
- `cong_cu/vong_lap.py` — sổ vòng lặp chờ quyết, có hạn tự tắt.
- Cấu hình chung `~/.claude/tintmark-token/cau_hinh.json`; riêng dự án `<gốc dự án>/.claude/tintmark-token.json` (ví dụ `{"nhac":150000,"doi":200000}`).
- Plugin tintmark-tietkiem (chỉ Claude Code), `P=~/.claude/skills/tintmark-token/../..`: `$P/scripts/thong_ke.py` (đã nén bao nhiêu), `phan_hoi.py` (báo nén sai), `tu_sua.py` (sửa bộ lọc), `cap_nhat.py` (cập nhật / quay lui), `cai_dat.py` (trạng thái / gộp / gỡ). Bản skill dùng trên Claude Chat không có các script này.
