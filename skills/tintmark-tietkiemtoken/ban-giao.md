# Bàn giao và đổi phiên

## 1. Ngưỡng

| Ngữ cảnh | Việc phải làm |
|---|---|
| < 300k | Làm bình thường; cập nhật tệp bàn giao ở mỗi mốc việc |
| ≥ 300k (hook báo `[tintmark-tietkiemtoken] NHẮC`) | **Câu đầu tiên** của câu trả lời báo người dùng: "Phiên đã <n>k token. Mở phiên mới để làm việc hiệu quả hơn. Ngữ cảnh đã đưa vào phiên mới." Viết / cập nhật ngay tệp bàn giao, xong phần việc dở của lượt này, rồi **mở thẳng** phiên kế nhiệm (mục 3) — không để thẻ chờ người dùng bấm |
| ≥ 350k (hook báo `[tintmark-tietkiemtoken] ĐỔI PHIÊN`) | Không nhận việc mới, kể cả tin vừa gửi. Chốt tệp bàn giao, mở phiên kế nhiệm kèm nguyên văn tin đó (mục 3), trả lời một dòng có link phiên mới |

Từ 350k, hook nhắc ở **mọi** lượt người dùng gửi tin và giữ tin lại vài giây trước khi cho qua (`cho_giay`, mặc định 8, tối đa 30; đặt 0 để tắt). Tin không bị chặn, không bị xoá.

Ngưỡng mặc định 300k / 350k. Phiên chỉ ghi sổ, chuyển tin nên đặt 150k / 200k trong `<gốc dự án>/.claude/tintmark-tietkiemtoken.json`. Không có hook (Claude Chat, máy khác): xem `claude-chat.md`.

**Sổ hỏi đáp:** xem mục 2b.

Không đổi phiên khi < 100k trừ khi đổi hẳn chủ đề. Không dùng tự nén (compact) thay cho đổi phiên: bản nén hay rơi luật và phiên vẫn tiếp tục phình.

## 2. Tệp bàn giao

Vị trí: `<gốc dự án>/ban_giao_phien/<ten_phien_khong_dau>.md` (chữ thường, không dấu, gạch dưới; bỏ số kế nhiệm — một dòng phiên dùng chung một tệp, ghi đè). Không có gốc dự án ghi được thì dùng `~/.claude/tintmark-tietkiemtoken/ban_giao/`. **Dưới khoảng 1.500 chữ.** Chỉ trỏ đường dẫn (tệp, commit, nhánh, mục sổ), không chép nội dung tệp khác, không chép lịch sử việc đã xong (lịch sử có ở nhật ký / git). Mục 2 chỉ giữ việc xong còn ảnh hưởng bước kế tiếp; mục 7 chỉ giữ cạm bẫy còn gặp được. Vượt 1.500 chữ thì cắt trước khi giao. Plugin kiểm tự động: ghi tệp `ban_giao_phien/*.md` (Write / Edit / lệnh bash) mà quá ngưỡng thì hook báo `[tintmark-tietkiemtoken] BÀN GIAO DÀI: N chữ` — cắt ngay. Ngưỡng `ban_giao_chu` trong cấu hình (0 = tắt), tắt hẳn bằng module `ban_giao`.

## 2b. Sổ hỏi đáp (mọi dự án)

- Mỗi dự án có **một** sổ hỏi đáp, mặc định `<gốc dự án>/HOI_DAP.md` (dự án đã có sổ ở chỗ khác thì ghi đường dẫn đó vào tệp luật / bàn giao). Mới nhất ở trên; mẫu một mục: `## <ngày> — <câu hỏi gọn>` · hỏi ở phiên nào · trả lời ≤10 dòng · nguồn kiểm (tệp / lệnh).
- Người dùng hỏi hoặc quyết điều gì có kết luận: **ghi sổ TRƯỚC, rồi mới trả lời** trong chat. Chat có thể trôi / bị tóm tắt; sổ thì không.
- Kết quả phê duyệt giọng nói (`phe-duyet-giong-noi.md`) cũng ghi vào sổ này trước khi làm.
- Phiên kế nhiệm đọc sổ (các mục mới nhất) **trước** tệp bàn giao. Tệp bàn giao chỉ trỏ tới sổ, không chép lại.

Mẫu:

```markdown
# Bàn giao: <tên phiên, không số>
> LỆNH BÀN GIAO: Đọc sổ hỏi đáp `<đường dẫn HOI_DAP.md>` (các mục mới nhất) và `<đường dẫn tệp này>` rồi làm tiếp từ mục 3. Phiên này là `<tên phiên> <số kế tiếp>`. Lượt đầu: xác nhận 3 dòng, gọi `detach_session "self"` TRƯỚC, rồi gọi archive_session lưu trữ mọi phiên cũ hơn 2 phiên mới nhất trong dòng `Chuỗi phiên` (ban-giao.md mục 4), thêm id của mình vào dòng đó và vào sổ phiên của dự án.
Cập nhật: <ngày giờ> · Phiên đang giữ: `<tên> <số>` (id <id nếu biết>) · Số phiên đã tạo: <n> · Model: <model>
Chuỗi phiên: <id phiên 1> (đã lưu trữ), <id phiên 2> (giữ), <id phiên hiện tại>
Sổ hỏi đáp: `<đường dẫn>`

## 1. Mục tiêu
## 2. Việc đã xong            (kèm commit / tệp / link)
## 3. Việc đang làm + bước kế tiếp   (bước kế tiếp phải làm được ngay, có lệnh / tệp cụ thể)
## 4. Tệp đã xong / đang sửa   (đường dẫn, nhánh, worktree, cái nào chưa commit)
## 5. Quyết định còn hiệu lực + việc chờ người dùng
## 6. Vòng lặp / lịch / tiến trình nền đang chạy   (id, tần suất, chủ là phiên nào)
## 7. Cạm bẫy đã gặp
```

**Lời giao phiên kế nhiệm chỉ gồm:** lệnh bàn giao + việc mới nguyên văn (nếu có). Không tóm tắt lại tệp bàn giao, không dán luật, không kể bối cảnh (đã có trong tệp).

**Lệnh bàn giao** (dòng đầu) luôn kèm bước `detach_session "self"` và bước lưu trữ phiên cũ như mẫu, và phải có từ lượt đầu của phiên: phiên treo, hết hạn mức hay cache nguội thì người dùng hoặc phiên điều phối vẫn mở phiên mới được bằng đúng một câu, không phải đánh thức phiên cũ.

Cập nhật tệp khi: xong một việc; trước khi dừng chờ người dùng; trước khi chạy việc dài; khi hook nhắc. Viết câu đủ (chữ phủ định, con số, đường dẫn) nhưng ngắn: mỗi ý một dòng.

## 3. Mở phiên kế nhiệm

1. Chốt tệp bàn giao (đủ 7 mục, tăng "Số phiên đã tạo").
2. Mở phiên **mới hoàn toàn**, không fork (fork mang theo cả lịch sử). Cùng thư mục làm việc; model theo `chon-model.md`; lời mở đầu = lệnh bàn giao.
   - **Chống mở trùng (bắt buộc):** trước khi mở, `list_sessions` tìm đúng tên `<tên cũ + số>` (cả phiên đang chạy và thẻ chờ). Đã có thì dùng phiên đó, không mở thêm; đã nhờ phiên điều phối mở hộ thì không tự mở nữa.
   - **Lượt do người dùng gõ** (app cho mở phiên): `start_session` kiểu `user_asked`, ngữ cảnh "fresh" — mở thẳng, không tạo thẻ. Việc làm theo luật thường trực của người dùng (CLAUDE.md, bộ nhớ) trong lượt đó cũng tính là lệnh của người dùng. Đã ≥ 350k thì lời giao = lệnh bàn giao + NGUYÊN VĂN tin người dùng vừa gửi; không làm việc đó ở phiên cũ; trả lời một dòng: "Mở phiên mới để làm việc hiệu quả hơn. Ngữ cảnh đã đưa vào phiên mới." kèm link phiên mới.
   - **Lượt do phiên khác gửi hoặc sự kiện tự động**: app chỉ cho tạo thẻ, mà thẻ bắt người dùng bấm "Bắt đầu" (gián đoạn). **Không tạo thẻ.** `SendMessage` phiên điều phối của dự án (id trong sổ phiên) **một** tin: "nhờ mở hộ `<tên mới>` ở lượt người dùng gõ bên đó; lệnh bàn giao ở `<tệp>`; phiên đầy: `<id>`". Trả lời phiên gửi một dòng: "phiên đã đầy, gửi lại việc này cho phiên `<tên mới>`". Chỉ khi dự án không có phiên điều phối mới tạo **một** thẻ (`own_initiative`, "fresh", tên cũ + số, mô tả có câu trên).
   - Hook không phân biệt được hai loại lượt; phiên tự xét từ nội dung lượt.
   - Claude Code app máy tính: công cụ mở phiên (`start_session`, ngữ cảnh "fresh"), rồi đặt tên bằng công cụ đổi tên phiên.
   - CLI: in lệnh bàn giao để người dùng dán vào `claude` mới.
   - Không có công cụ mở phiên: đưa lệnh bàn giao cho người dùng, nói rõ cần mở phiên mới.
3. Đặt tên phiên mới = tên phiên cũ + số (`dat-ten-phien.md` mục 3). Phải xong **trước khi phiên cũ chạm 350k**.
4. Phiên mới đọc tệp bàn giao; tệp luật dài / tệp tham chiếu chỉ đọc khi bước kế tiếp thật cần. Trả lời 3 dòng xác nhận: mục tiêu, bước kế tiếp, tệp đang sửa. Sai thì sửa tệp bàn giao, không giải thích lại bằng chat dài.
5. **Bắt buộc, ở lượt đầu của phiên mới:** `detach_session "self"` trước mọi bước lưu trữ (phiên mới là phiên con của phiên cũ: không tách thì lưu trữ phiên cũ sẽ kéo theo phiên mới, và báo cáo đi vào phiên đã lưu trữ). Sau đó lưu trữ phiên cũ hơn 2 phiên mới nhất của chuỗi (mục 4) và ghi id + tên phiên mới vào sổ phiên của dự án nếu có (bảng id phiên, ví dụ `tham_chieu/phien.md`). Chuyển chủ của vòng lặp / lịch sang phiên mới hoặc tắt.
6. Báo phiên điều phối (nếu có) **một dòng**: "`<tên cũ>` → `<tên mới>` (id …), bàn giao ở `<tệp>`".
7. **Phiên cũ (đang đầy), sau khi mở xong phiên mới:** lưu trữ phiên **trước đó** nếu có (phiên ngay trước nó trong dòng `Chuỗi phiên`; tách phiên con còn dùng trước). **Giữ** phiên đang đầy: nó là 1 trong 2 phiên mới nhất; chỉ không nhận việc mới.

## 4. Phiên cũ

- **Phiên vừa đầy được GIỮ** (1 trong 2 phiên mới nhất), không nhận việc mới; nó lưu trữ phiên trước đó của nó (mục 3 bước 7). Phiên bị lưu trữ: Archive, không xoá, không nhắn nữa; tắt điều khiển từ xa nếu đang bật.
- **Mỗi chuỗi chỉ hiện 2 phiên mới nhất.** Chuỗi = các phiên cùng vai trò: tên cũ + số, hoặc dòng `Chuỗi phiên: <id 1>, <id 2>, …` trong tệp bàn giao (id theo thứ tự tạo; phiên mới tự thêm id của mình); kể cả các lần chạy của cùng một lịch tự chạy. Chuỗi có từ 3 phiên trở lên thì chỉ giữ 2 phiên mới nhất (phiên đang chạy + phiên ngay trước), còn lại `archive_session` ngay, không cần hỏi người dùng. Phiên kế nhiệm làm việc này ở lượt đầu, sau khi đọc xong bàn giao và xác nhận 3 dòng. Chi tiết cũ vẫn tra được trong lịch sử phiên đã lưu trữ.
- **Dòng `Chuỗi phiên` phải có id thật** từ lượt đầu (id phiên hiện tại: hook báo kèm ở mức NHẮC, hoặc tra danh sách phiên). Không có id thì phiên kế nhiệm không lưu trữ được.
- **Thứ tự:** lưu trữ từ phiên **cũ nhất**.
- **Phiên con:** `archive_session` lưu trữ luôn các phiên con đã rảnh do phiên đó mở. `list_sessions` KHÔNG cho thấy quan hệ cha – con, nên trước khi lưu trữ một phiên gốc: gọi `get_session` từng phiên còn mở cùng nhóm, tìm `parentSessionId` trỏ tới phiên sắp lưu trữ (tìm cả cháu: phiên có cha là một phiên con vừa tìm được). Phiên con / cháu còn dùng (phiên ngay trước, phiên đang chạy, phiên ngoài chuỗi) thì `detach_session` tách ra **trước** khi lưu trữ phiên gốc. Lỡ bị kéo theo thì `unarchive_session` ngay.
- **Lỗi lần đầu trong chế độ tự động:** lần gọi đầu bị hook thêm trường `session` và báo lỗi (kiểu "a hook changed this call's input"). Gọi lại **đúng nguyên đầu vào mà lỗi trả về** thì qua; không dừng ở lần lỗi đầu.
- **Phiên đang chạy hoặc đang mở trên màn hình** (hoặc đang ghim) thì không lưu trữ được: không thử lại vòng vòng; ghi "(chưa lưu trữ: đang chạy / đang mở / đang ghim)" vào dòng `Chuỗi phiên` để lần sau làm, và báo người dùng một dòng tên phiên đó.
- Cần chi tiết cũ: phiên mới tìm trong lịch sử phiên cũ (tìm kiếm transcript), không mở lại để hỏi.
- Xoá hẳn: chỉ khi người dùng bảo; gợi ý sau 30 ngày không ai tra.
- Phiên cũ còn tiến trình nền / lịch gắn với nó: chuyển hoặc tắt trước khi lưu trữ, ghi ở mục 6 tệp bàn giao.

## 5. Phiên mới có hiệu quả không

Có, thường tốt hơn: ngữ cảnh ngắn thì model bám luật tốt hơn, ít nhầm việc cũ. Cái mất là sắc thái chưa ghi ra. Vì vậy: quyết định của người dùng ghi nguyên văn ở mục 5; cạm bẫy ghi ở mục 7; cái gì "ai cũng biết trong phiên" mà tệp chưa có thì phải ghi.

## 6. Kiểm nhanh trước khi rời phiên cũ

- [ ] Sổ hỏi đáp đã ghi mọi câu người dùng hỏi / quyết trong phiên; lệnh bàn giao trỏ tới sổ
- [ ] Tệp bàn giao đủ 7 mục, dưới ~1.500 chữ (`wc -w`), chỉ trỏ đường dẫn, bước kế tiếp làm được ngay
- [ ] Mọi thay đổi mã đã commit hoặc ghi rõ "chưa commit" kèm đường dẫn
- [ ] Không có hai phiên kế nhiệm cùng tên (`list_sessions`)
- [ ] Phiên mới đã xác nhận 3 dòng và đã `detach_session "self"`
- [ ] Sổ phiên đã sửa id, vòng lặp đã chuyển chủ
- [ ] Phiên đầy đã lưu trữ phiên trước đó của nó; chuỗi chỉ còn hiện 2 phiên mới nhất (lưu trữ từ cũ nhất, tách phiên con còn dùng trước, gọi lại khi lỗi hook); dòng `Chuỗi phiên` và sổ phiên có id phiên mới
