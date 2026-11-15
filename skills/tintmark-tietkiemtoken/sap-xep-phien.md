# Phiên "Sắp xếp - tìm kiếm"

Một phiên riêng lo việc dọn danh sách phiên: xếp phiên vào đúng dự án, đổi tên cho dễ tìm, đề xuất lưu trữ / xoá, và tìm lại phiên cũ theo từ khoá. Dùng cho mọi dự án. Cần Claude Code app máy tính (có công cụ quản lý phiên); CLI và Claude Chat xem mục 7.

## 1. Mở phiên này

- Tên phiên đúng nguyên văn: **`Sắp xếp - tìm kiếm`** (tên cố định, là ngoại lệ của khuôn tên ở mục 4). Mỗi máy chỉ một phiên tên này; đã có thì dùng lại, không mở thêm.
- Model nhỏ là đủ (`chon-model.md`): việc ở đây là liệt kê, đặt tên, ghi sổ.
- Phiên này không làm việc của dự án, không sửa mã, không nhắn vào phiên khác để hỏi (đánh thức phiên to đã nguội là tốn nhất). Chỉ đọc danh sách phiên, tên, thư mục, nhóm thanh bên, thời điểm hoạt động cuối, và tìm trong lịch sử khi cần.
- Người dùng gọi skill với ý "sắp xếp phiên", "dọn danh sách phiên", "tìm phiên" ở một phiên khác: phiên đó đề xuất mở phiên `Sắp xếp - tìm kiếm` (hoặc chỉ sang phiên đã có), không tự dọn tại chỗ.

## 2. Quét (lượt đầu, và mỗi khi người dùng bảo "quét lại")

1. Liệt kê mọi phiên **một lần duy nhất** bằng công cụ liệt kê phiên với giới hạn lớn và cả phiên đã lưu trữ. Công cụ chỉ lọc được theo nhóm thanh bên và theo họ phiên, không lọc theo thư mục hay ngày, nên kết quả rất dài (máy vài trăm phiên là vài trăm nghìn ký tự) và app tự lưu ra tệp: xử lý tệp đó bằng script (`python3`, `jq`), chỉ in số đếm và bảng đã gom. Không gọi lại nhiều lần, không in danh sách vào chat. Phiên đang gọi không nằm trong danh sách.
2. Với mỗi phiên ghi: id, tên hiện tại, thư mục làm việc, nhóm thanh bên, hoạt động cuối, đang chạy hay rảnh, đã lưu trữ chưa, phiên nào mở ra nó. Danh sách không có nhánh git và không cho biết phiên nào đang chờ người dùng trả lời.
3. Xếp nhóm theo **dự án** = gốc thư mục làm việc sau khi chuẩn hoá: đường dẫn cũ / lối tắt của cùng một dự án gộp về đường dẫn mới; thư mục worktree gộp về gốc kho; thư mục tạm do app sinh (scratch) không phải dự án, xếp vào "Việc tự sinh" hoặc "Việc lẻ" theo tên. Trong dự án xếp theo **phạm vi** (khung / phòng ban / giải pháp) suy từ tên. Phiên không rõ dự án để vào nhóm "Chưa rõ" và hỏi, không đoán.
4. Ghi kết quả ra sổ `~/.claude/tintmark-tietkiemtoken/so_phien.md` (bảng: dự án · phạm vi · tên · id · hoạt động cuối · trạng thái · từ khoá chính). Sổ này là thứ để tìm kiếm về sau; trả lời trong chat chỉ tóm tắt số lượng.
5. Dự án có sổ phiên riêng (ví dụ `tham_chieu/phien.md`) thì sổ riêng là chuẩn về id và tên; phiên này chỉ đề xuất sửa, không tự ghi đè.

## 3. Thẻ đề xuất

Mỗi đề xuất là một thẻ ngắn để người dùng bấm chọn, không phải gõ. Gom theo loại, mỗi lượt tối đa 4 thẻ, mỗi thẻ tối đa 10 phiên, thẻ quan trọng nhất trước. Mỗi thẻ có: việc sẽ làm, danh sách phiên (tên cũ → tên mới nếu là đổi tên), lý do một dòng, hệ quả, và nút "Làm" / "Bỏ qua" / "Sửa".

| Loại thẻ | Khi nào đề xuất | Sau khi người dùng đồng ý |
|---|---|---|
| **Đổi tên** | Tên sai quy tắc `dat-ten-phien.md`, tên mặc định, tên trùng, thiếu số kế nhiệm, tên dài | Đổi bằng công cụ đổi tên phiên; ghi tên cũ vào sổ để còn tìm được |
| **Xếp nhóm** | Phiên nằm sai nhóm / chưa có nhóm theo dự án | Tạo nhóm / mục ở thanh bên theo cây `dự án › phạm vi`, chuyển phiên vào |
| **Lưu trữ** | Phiên đã có kế nhiệm; việc đã xong; rảnh quá 7 ngày; phiên > 350k đã nguội | Lưu trữ (không xoá). Còn vòng lặp / tiến trình nền gắn với nó thì chuyển chủ hoặc tắt trước (`don-ngu-canh.md`) |
| **Xoá** | Phiên rỗng / thử nghiệm, phiên trùng không có nội dung, phiên đã lưu trữ quá 30 ngày không ai tra | Xoá từng nhóm nhỏ. Luôn nêu "không khôi phục được" |
| **Gộp việc** | Nhiều phiên cùng làm một việc | Chỉ đề xuất giữ phiên nào, phiên còn lại lưu trữ; không gộp nội dung |
| **Cụm tự sinh** | Hàng chục / hàng trăm phiên cùng tên do lịch hoặc hook sinh ra | Một thẻ cho cả cụm (không tính vào giới hạn 10 phiên): lưu trữ theo ngày, giữ lại vài phiên mới nhất; kèm đề xuất tắt hoặc giãn nguồn sinh (`don-ngu-canh.md` mục 2–4) để khỏi phình lại |

Quy tắc duyệt:

- **Xoá luôn phải có người dùng đồng ý rõ ràng cho đúng danh sách đó**, không bao giờ tự làm, không suy từ lần đồng ý trước. App cũng tự hỏi người dùng ở mỗi lần xoá, dù đang ở chế độ quyền nào.
- Đổi tên, xếp nhóm, lưu trữ: mặc định cũng chờ đồng ý. Người dùng đã dặn trước "việc sắp xếp / đổi tên / lưu trữ tự làm" (trong luật dự án hay bộ nhớ) thì làm luôn rồi báo một bảng tóm tắt.
- Không đụng: phiên đang chạy việc, phiên vừa hoạt động trong 24 giờ (danh sách không cho biết phiên nào đang chờ trả lời, nên coi phiên mới hoạt động là đang chờ), phiên điều phối và các phiên có tên trong sổ phiên của dự án (chỉ đề xuất, nêu rõ là phiên có vai trò).
- Mỗi việc đã làm ghi một dòng vào `~/.claude/tintmark-tietkiemtoken/so_phien_nhat_ky.md` (giờ, việc, id, tên cũ → mới) để hoàn tác được: đổi tên lại, bỏ lưu trữ. Xoá thì không hoàn tác được.

## 4. Đặt tên cho khoa học, dễ tìm

Theo `dat-ten-phien.md`. Tóm tắt để áp dụng nhanh:

- Khuôn của `dat-ten-phien.md`; dự án có khuôn riêng thì dùng khuôn riêng, ví dụ `<Phạm vi> - <Việc> [số]` như `Khung - Plugin nén token 3`. Ngắn, 2–5 từ cho phần việc, danh từ đứng trước.
- Cùng một dòng việc giữ nguyên tên, chỉ tăng số kế nhiệm.
- Cần ngày thì viết ngắn `dd/mm` ở cuối (ví dụ `Báo cáo tuần 15/11`); không ghi năm, không ghi giờ.
- Không dùng tên chung chung ("Phiên mới", "Sửa lỗi", "Test"). Từ đầu tiên phải là thứ người dùng sẽ gõ khi tìm.
- Dự án có quy ước riêng (tiếng Việt không dấu, theo khối phòng ban…) thì theo quy ước đó.

## 5. Cây sắp xếp

Đề xuất một cây gọn rồi mới chuyển phiên. Nhóm thanh bên của app là **nhóm phẳng một tầng** (không có nhóm con): tầng trên của cây là nhóm, tầng dưới thể hiện bằng tiền tố tên phiên. Máy chỉ có một dự án lớn thì mỗi phạm vi là một nhóm.

```
<Dự án A>
  Khung (điều phối, yêu cầu, phát hành, kiểm thử, báo cáo)
  <Phòng ban / giải pháp 1>
  <Phòng ban / giải pháp 2>
<Dự án B>
Việc lẻ (phiên một lần, không thuộc dự án)
Lưu trữ gần đây
```

- Nhóm dưới 2 phiên thì không tạo, để ở tầng trên.
- Thứ tự trong nhóm: phiên đang chạy trước, rồi theo hoạt động cuối.
- Dự án có cây thư mục rõ (theo phòng ban, theo giải pháp) thì cây phiên đi theo cây thư mục đó.
- Đề xuất cây trước bằng một thẻ; người dùng đồng ý cây rồi mới ra các thẻ chuyển phiên.

## 6. Tìm phiên theo từ khoá

Người dùng hỏi "phiên nào làm X", "tìm phiên về Y", "hôm trước làm Z ở đâu":

1. Tra sổ `so_phien.md` trước (tên, tên cũ, từ khoá chính, dự án).
2. Chưa ra thì tìm trong lịch sử các phiên (công cụ tìm transcript), kể cả phiên đã lưu trữ. Công cụ khớp chuỗi con, mỗi phiên trả một kết quả, không xếp hạng theo độ liên quan: phiên chỉ nhắc tới từ khoá (kể cả trong danh mục tệp bị dán vào) lẫn với phiên chuyên việc đó. Vì vậy lấy giới hạn rộng (20–30) rồi tự lọc; từ khoá ngắn hoặc viết tắt thì thử thêm tên đầy đủ, tên không dấu, mã yêu cầu.
3. Trả lời tối đa 5 kết quả, mỗi dòng: link phiên · dự án · ngày hoạt động cuối · một câu vì sao khớp. Kết quả đã lưu trữ ghi rõ "đã lưu trữ".
4. Gợi ý 2–3 từ khoá gần nghĩa khi không thấy hoặc thấy quá nhiều (tên cũ của tính năng, mã yêu cầu, tên tệp, tên người).
5. Không mở lại, không nhắn vào phiên tìm được. Người dùng muốn làm tiếp việc đó: trỏ tệp bàn giao của phiên ấy, hoặc đề xuất mở phiên kế nhiệm (`ban-giao.md`).
6. Tìm xong bổ sung từ khoá vừa dùng vào dòng của phiên đó trong sổ, lần sau tra sổ là ra.

## 7. Giới hạn

- CLI và Claude Chat không có công cụ đổi tên / lưu trữ / xếp nhóm phiên: phiên chỉ lập bảng đề xuất (tên cũ → tên mới, nên lưu trữ, nên xoá) để người dùng tự làm tay.
- Xếp nhóm ở thanh bên phụ thuộc app; app không có công cụ nhóm thì dùng tiền tố tên (`<Dự án> · <Phạm vi> - <Việc>`) thay cho nhóm.
- Tên công cụ trong app máy tính (bản 11/2026, kiểm bằng tìm công cụ trước khi dùng vì có thể đổi): liệt kê `list_sessions`, tìm `search_session_transcripts`, đổi tên `set_session_title`, lưu trữ `archive_session` / `unarchive_session`, xoá `delete_session` (nhóm `ccd_session_mgmt`); nhóm thanh bên `list_groups`, `create_group`, `move_sessions`, `set_pinned` (nhóm `ccd_sidebar`).
- Lưu trữ một phiên có thể kéo theo các phiên con đã xong của nó: trước khi lưu trữ phiên từng mở phiên khác, xem phiên con nào cần giữ.
- Hai tệp sổ nằm ở `~/.claude/tintmark-tietkiemtoken/`, ngoài thư mục dự án. Dự án có luật "chỉ ghi trong thư mục dự án" thì hỏi người dùng một lần nơi đặt sổ, rồi ghi nơi đó vào `cau_hinh.json`.
- Phiên `Sắp xếp - tìm kiếm` cũng theo ngưỡng 300k / 350k như mọi phiên; trạng thái nằm ở hai tệp sổ nên đổi phiên không mất gì.

## Bổ sung 15/11 từ lượt chạy thử đầu
- `list_sessions` chỉ lọc theo `group` và `linked`, mặc định 20 dòng; 697 phiên ≈ 353k ký tự. Gọi một lần `limit=1000, include_archived=true`, xử lý tệp kết quả bằng `python3 -I`/`jq`, chỉ in số đếm; đừng gọi lại nhiều lần.
- Danh sách không có trường nhánh, chỉ có `cwd`, `group`, `isRunning`, `lastActivityAt`, `name`, `startedBy`, `link`; phiên đang chạy này bị loại. Không biết phiên nào đang chờ người dùng trả lời (chỉ có `isRunning`).
- Chuẩn hoá `cwd` trước khi gom dự án: đường dẫn cũ đã đổi tên / lối tắt → đường dẫn hiện hành của dự án; worktree `.claude/worktrees/*` → gốc; thư mục scratch của app → "Việc tự sinh".
- Nhóm thanh bên chỉ một tầng (`create_group` không có cha): dùng nhóm + tiền tố tên, không có cây 2 tầng.
- Khuôn tên: dự án có luật đặt tên riêng (tiền tố theo khối / phòng ban) thì theo luật đó; `Sắp xếp - tìm kiếm` là ngoại lệ ghi rõ.
- Phiên tự sinh số lượng lớn (sửa lỗi bản vá, lịch quét): lưu trữ theo cụm tên + ngày, giữ phiên có hoạt động trong khoảng người dùng nói; hỏi người dùng có tắt nguồn sinh (lịch, hook) không. Tên cụm cần lọc theo `lastActivityAt` chứ không chỉ theo tên.
- Quyền: `archive_session` hỏi từng phiên; 9 lần bị chặn/từ chối liên tiếp thì bộ phân loại auto mode dừng cả lô. Lưu trữ hàng loạt nên chia cụm ≤ 10 và báo trước để người dùng bấm cho phép; `unarchive_session` có thể bị hook chèn trường `session`, khi đó gọi lại một lần đúng input hook nêu. `delete_session` luôn hỏi người dùng.
- `search_session_transcripts`: một hit mỗi phiên, khớp chuỗi con, không xếp hạng, có thể khớp tên tệp trong danh mục dán vào transcript; lấy ≥10 hit rồi tự lọc 5.
- Hai tệp sổ (`so_phien.md`, `so_phien_nhat_ky.md`) nằm trong thư mục dữ liệu của skill (`~/.claude/tintmark-tietkiemtoken/`, máy cũ có thể còn tên `tintmark-token`); chỉ ghi khi người dùng đã cho phép.
- Cách làm sai cần tránh: lệnh "lưu trữ hết trừ 3 phiên mới nhất" mâu thuẫn với câu trả lời "từ 08/11 để lại"; trước khi lưu trữ hàng loạt phải đối chiếu mọi chỉ dẫn của người dùng, lưu trữ theo ngưỡng ngày, rồi mới chạy.
