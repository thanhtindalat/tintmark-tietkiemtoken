# Bàn giao và đổi phiên

## 1. Ngưỡng

| Ngữ cảnh | Việc phải làm |
|---|---|
| < 250k | Làm bình thường; cập nhật tệp bàn giao ở mỗi mốc việc |
| ≥ 250k (hook báo `[tintmark-token] NHẮC`) | **Câu đầu tiên** của câu trả lời báo người dùng: "Phiên đã <n>k token. Mở phiên mới để làm việc hiệu quả hơn. Ngữ cảnh đã đưa vào phiên mới." Viết / cập nhật ngay tệp bàn giao, rồi tạo **một** thẻ đề xuất phiên kế nhiệm (mục 3) để người dùng chỉ cần bấm Bắt đầu. Vẫn được hoàn tất việc đang dở |
| ≥ 300k (hook báo `[tintmark-token] ĐỔI PHIÊN`) | Không nhận việc mới, kể cả tin vừa gửi. Chốt tệp bàn giao, mở phiên kế nhiệm kèm nguyên văn tin đó (mục 3), trả lời một dòng có link phiên mới |

Từ 300k, hook nhắc ở **mọi** lượt người dùng gửi tin và giữ tin lại vài giây trước khi cho qua (`cho_giay`, mặc định 8, tối đa 30; đặt 0 để tắt). Tin không bị chặn, không bị xoá.

Ngưỡng mặc định 250k / 300k. Phiên chỉ ghi sổ, chuyển tin nên đặt 150k / 200k trong `<gốc dự án>/.claude/tintmark-token.json`. Không có hook (Claude Chat, máy khác): xem `claude-chat.md`.

Không đổi phiên khi < 100k trừ khi đổi hẳn chủ đề. Không dùng tự nén (compact) thay cho đổi phiên: bản nén hay rơi luật và phiên vẫn tiếp tục phình.

## 2. Tệp bàn giao

Vị trí: `<gốc dự án>/ban_giao_phien/<ten_phien_khong_dau>.md` (chữ thường, không dấu, gạch dưới; bỏ số kế nhiệm — một dòng phiên dùng chung một tệp, ghi đè). Không có gốc dự án ghi được thì dùng `~/.claude/tintmark-token/ban_giao/`. Dài tối đa khoảng 6.000 ký tự; chi tiết dài thì trỏ sang tệp khác.

Mẫu:

```markdown
# Bàn giao: <tên phiên, không số>
> LỆNH BÀN GIAO: Đọc `<đường dẫn tệp này>` rồi làm tiếp từ mục 3. Phiên này là `<tên phiên> <số kế tiếp>`.
Cập nhật: <ngày giờ> · Phiên đang giữ: `<tên> <số>` (id <id nếu biết>) · Số phiên đã tạo: <n> · Model: <model>
Chuỗi phiên: <id phiên 1>, <id phiên 2>, …

## 1. Mục tiêu
## 2. Việc đã xong            (kèm commit / tệp / link)
## 3. Việc đang làm + bước kế tiếp   (bước kế tiếp phải làm được ngay, có lệnh / tệp cụ thể)
## 4. Tệp đã xong / đang sửa   (đường dẫn, nhánh, worktree, cái nào chưa commit)
## 5. Quyết định còn hiệu lực + việc chờ người dùng
## 6. Vòng lặp / lịch / tiến trình nền đang chạy   (id, tần suất, chủ là phiên nào)
## 7. Cạm bẫy đã gặp
```

**Lệnh bàn giao** (dòng đầu) phải có từ lượt đầu của phiên: phiên treo, hết hạn mức hay cache nguội thì người dùng hoặc phiên điều phối vẫn mở phiên mới được bằng đúng một câu, không phải đánh thức phiên cũ.

Cập nhật tệp khi: xong một việc; trước khi dừng chờ người dùng; trước khi chạy việc dài; khi hook nhắc. Viết bình thường, đủ chữ phủ định, con số, đường dẫn — đây là tài liệu lưu, không viết kiểu rút gọn.

## 3. Mở phiên kế nhiệm

1. Chốt tệp bàn giao (đủ 7 mục, tăng "Số phiên đã tạo").
2. Mở phiên **mới hoàn toàn**, không fork (fork mang theo cả lịch sử). Cùng thư mục làm việc; model theo `chon-model.md`; lời mở đầu = lệnh bàn giao.
   - **Lượt do người dùng gõ** (app cho mở phiên): `start_session` kiểu `user_asked`, ngữ cảnh "fresh". Đã ≥ 300k thì lời giao = lệnh bàn giao + NGUYÊN VĂN tin người dùng vừa gửi; không làm việc đó ở phiên cũ; trả lời một dòng: "Mở phiên mới để làm việc hiệu quả hơn. Ngữ cảnh đã đưa vào phiên mới." kèm link phiên mới.
   - **Lượt do phiên khác gửi hoặc sự kiện tự động**: app từ chối mở phiên kiểu `user_asked`. Tạo thẻ đề xuất (`start_session` kiểu `own_initiative`, "fresh", tên cũ + số, mô tả có câu trên) chờ người dùng bấm Bắt đầu; trả lời phiên gửi một dòng: "phiên đã đầy, gửi lại việc này cho phiên `<tên mới>` sau khi người dùng bấm Bắt đầu". Mỗi phiên chỉ một thẻ.
   - Hook không phân biệt được hai loại lượt; phiên tự xét từ nội dung lượt.
   - Claude Code app máy tính: công cụ mở phiên (`start_session`, ngữ cảnh "fresh"), rồi đặt tên bằng công cụ đổi tên phiên.
   - CLI: in lệnh bàn giao để người dùng dán vào `claude` mới.
   - Không có công cụ mở phiên: đưa lệnh bàn giao cho người dùng, nói rõ cần mở phiên mới.
3. Đặt tên phiên mới = tên phiên cũ + số (`dat-ten-phien.md` mục 3). Phải xong **trước khi phiên cũ chạm 300k**.
4. Phiên mới đọc tệp, trả lời 3 dòng xác nhận: mục tiêu, bước kế tiếp, tệp đang sửa. Sai thì sửa tệp bàn giao, không giải thích lại bằng chat dài.
5. Cập nhật sổ phiên của dự án nếu có (bảng id phiên, ví dụ `tham_chieu/phien.md`): id mới, tên mới. Chuyển chủ của vòng lặp / lịch sang phiên mới hoặc tắt.
6. Báo phiên điều phối (nếu có) **một dòng**: "`<tên cũ>` → `<tên mới>` (id …), bàn giao ở `<tệp>`".

## 4. Phiên cũ

- **Lưu trữ (Archive), không xoá, không nhắn nữa.** Tắt điều khiển từ xa của nó nếu đang bật.
- **Chỉ giữ 1 phiên trước + 1 phiên đang chạy.** Tệp bàn giao có dòng `Chuỗi phiên: <id 1>, <id 2>, …` (id theo thứ tự tạo; phiên mới tự thêm id của mình). Phiên kế nhiệm, ở lượt đầu sau khi xác nhận 3 dòng, lưu trữ mọi phiên trong chuỗi **trừ phiên ngay trước nó** (công cụ lưu trữ phiên; việc này không cần hỏi người dùng). Phiên ngay trước được giữ tới khi có phiên kế tiếp nữa.
- Cần chi tiết cũ: phiên mới tìm trong lịch sử phiên cũ (tìm kiếm transcript), không mở lại để hỏi.
- Xoá hẳn: chỉ khi người dùng bảo; gợi ý sau 30 ngày không ai tra.
- Phiên cũ còn tiến trình nền / lịch gắn với nó: chuyển hoặc tắt trước khi lưu trữ, ghi ở mục 6 tệp bàn giao.

## 5. Phiên mới có hiệu quả không

Có, thường tốt hơn: ngữ cảnh ngắn thì model bám luật tốt hơn, ít nhầm việc cũ. Cái mất là sắc thái chưa ghi ra. Vì vậy: quyết định của người dùng ghi nguyên văn ở mục 5; cạm bẫy ghi ở mục 7; cái gì "ai cũng biết trong phiên" mà tệp chưa có thì phải ghi.

## 6. Kiểm nhanh trước khi rời phiên cũ

- [ ] Tệp bàn giao đủ 7 mục, bước kế tiếp làm được ngay
- [ ] Mọi thay đổi mã đã commit hoặc ghi rõ "chưa commit" kèm đường dẫn
- [ ] Phiên mới đã xác nhận 3 dòng
- [ ] Sổ phiên đã sửa id, vòng lặp đã chuyển chủ
- [ ] Phiên cũ hơn phiên ngay trước đã lưu trữ; dòng `Chuỗi phiên` đã thêm id phiên mới
