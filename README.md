# tintmark-tietkiemtoken — plugin tiết kiệm token cho Claude Code

Một gói gồm: nén output lệnh bash, skill `tintmark-tietkiemtoken` (ngưỡng 300k / 350k đổi phiên, bàn giao, chọn model, dọn ngữ cảnh), hook đo ngưỡng, sổ vòng lặp, đo token, sổ phản hồi, tự sửa bộ lọc, cập nhật có sao lưu và quay lui.

Python 3 thư viện chuẩn. Không cài thêm gì, không API trả phí, không gửi dữ liệu ra ngoài máy.

> **Giấy phép:** chưa cấp phép sử dụng lại, giữ mọi quyền (All rights reserved). Mã được công khai để xem; chưa cho phép sao chép, sửa, phân phối lại khi chưa có giấy phép chính thức.

## Thư mục

| Thư mục | Nội dung |
|---|---|
| `scripts/` | `hook_sau.py` (nén ở PostToolUse), `hook.py` (chế độ cũ), `nen.py` + `nen_loi.py` (lõi nén), `thong_ke.py`, `phan_hoi.py`, `tu_sua.py`, `phat_ban.py`, `cap_nhat.py`, `cai_dat.py`, `doi_ten.py` (chuyển máy từ tên cũ `nen-token`) |
| `luat/luat.json` | 19 bộ lọc: git status / diff / log / push-pull-commit-branch, pytest, unittest, node test, cargo test, build / lint, ls, find, grep, adb (+ logcat), docker (build, logs, danh sách), log dài. Luật riêng của máy: `~/.claude/plugin-tintmark-tietkiemtoken/luat_rieng.json` (đứng trước) |
| `commands/phan-hoi.md` | lệnh `/tintmark-tietkiemtoken:phan-hoi` báo nén sai |
| `hooks/hooks.json` | nối hook nén (Bash) và hook ngưỡng (PostToolUse, UserPromptSubmit) |
| `skills/tintmark-tietkiemtoken/` | skill + `cong_cu/` (`nguong_token.py`, `do_token.py`, `vong_lap.py`) |
| `mau/`, `tests/` | output mẫu (từ kho mẫu tổng hợp `tests/tao_mau.sh` hoặc viết tay) và test; `tests/phan_hoi/` là ca test sinh từ phản hồi |

Trên máy cần 3 chỗ: **nguồn** (thư mục này), **kho bản** (`../kho_ban/tintmark-tietkiemtoken/<số bản>/` + `kenh.json`), **thư mục cài** (bản sao thật của một bản trong kho, đặt trong marketplace; tên cấu hình vẫn là `lien_ket`; bản cũ hơn 0.4.0 dùng liên kết tượng trưng, lần cập nhật đầu tự thay bằng bản sao). Dữ liệu chạy: `~/.claude/plugin-tintmark-tietkiemtoken/`.

## Cài

1. Phát bản đầu vào kho bản (chạy trong nguồn): `python3 scripts/phat_ban.py --loai va --ghi-chu "bản đầu"`.
   Cài thẳng từ kho này (marketplace GitHub): `claude plugin marketplace add <chủ>/tintmark-tietkiemtoken` rồi `claude plugin install tintmark-tietkiemtoken@tintmark-tietkiemtoken`.
2. Hoặc chép bản đó thành thư mục cài, đặt trong một marketplace cục bộ, rồi `claude plugin install tintmark-tietkiemtoken@<tên marketplace>`. Thử nhanh không cài: `claude --plugin-dir <thư mục bản>`.
3. Gộp skill và hook ngưỡng cũ (nếu máy đã có skill `tintmark-tietkiemtoken` riêng), đồng thời ghi cấu hình cập nhật:

```bash
python3 <liên kết>/scripts/cai_dat.py gop --lien-ket <liên kết> --kenh <kho bản>/kenh.json --nguon <nguồn> --tu-dong ap_dung
```

4. Kiểm: `python3 <liên kết>/scripts/cai_dat.py trang-thai`.

Phiên đang mở nhận hook khi mở lại hoặc `/reload-plugins`.

Sau khi gộp, đặt `P=~/.claude/skills/tintmark-tietkiemtoken/../..` để gọi script ở mọi thư mục.

## Dùng hằng ngày

Không phải làm gì: lệnh bash đơn giản có luật khớp, chạy thành công, output đủ dài thì tự được rút gọn. Chỗ cắt có dòng `… [nén: bỏ N dòng — chạy lại với NEN_OFF=1 để xem đủ]`. Cần output đầy đủ: thêm `NEN_OFF=1 ` trước lệnh.

## Đo

```bash
python3 $P/scripts/thong_ke.py --days 7 --theo luat
```
```bash
python3 $P/skills/tintmark-tietkiemtoken/cong_cu/do_token.py 3
```

`thong_ke.py` là số byte nén được (token ≈ byte / 4, ước tính). `do_token.py` là token theo phiên từ nhật ký Claude Code.

## Phản hồi và tự sửa

```bash
python3 $P/scripts/phan_hoi.py bao --loai mat-dong --lenh "docker ps -a" --mo-ta "mất cột NAMES"
```
```bash
python3 $P/scripts/tu_sua.py quet
```

Bộ lọc bị báo 2 lần (hoặc 3 dấu hiệu tự ghi) trong 7 ngày thì tự tắt riêng bộ lọc đó. Sửa: `tu_sua.py tai-hien <mã> --giu "<dòng bị mất>"` → sửa `luat/luat.json` → `tu_sua.py xong <mã> --ghi-chu "…"` (test, phát bản vá, cập nhật, bật lại, đóng). Chi tiết: `skills/tintmark-tietkiemtoken/phan-hoi.md`, `tu-sua.md`.

## Cập nhật và quay lui

```bash
python3 $P/scripts/cap_nhat.py kiem
```
```bash
python3 $P/scripts/cap_nhat.py ap-dung
```
```bash
python3 $P/scripts/cap_nhat.py quay-lui
```

`ap-dung` kiểm băm, chạy test của bản mới, sao lưu, chép bản mới vào thư mục cài (chép xong mới tráo), thử khói; hỏng bước nào thì giữ hoặc tự về bản cũ. Tự cập nhật nền mỗi 24 giờ theo `tu_dong` trong `~/.claude/plugin-tintmark-tietkiemtoken/cap_nhat.json` (`ap_dung` | `bao` | `tat`). Chi tiết: `skills/tintmark-tietkiemtoken/cap-nhat.md`.

## Module (bật / tắt từng phần)

```bash
python3 $P/scripts/module.py ds
```
Module: `nen` (nén output), `tu_sua` (tự tắt bộ lọc hỏng), `nguong` (nhắc 300k / 350k), `vong_lap` (nhắc vòng lặp), `tu_cap_nhat` (kiểm bản mới mỗi 24 giờ), `cau_noi` (phê duyệt bằng giọng nói qua thư mục Google Drive: `scripts/cau_noi.py`, xem `skills/tintmark-tietkiemtoken/phe-duyet-giong-noi.md`). Tắt cả máy: `module.py tat <id>` (bật lại: `module.py bat <id>`). Tắt riêng một dự án: `<dự án>/.claude/tintmark-tietkiemtoken.json` có `{"module": {"<id>": false}}`. Tắt tạm: biến môi trường `TIETKIEM_TAT_MODULE=nen,nguong`. Module tắt chỉ làm hook của nó im, không chặn lệnh.

## Hội viên

Cơ chế khoá hội viên có sẵn nhưng **đang tắt** (`.claude-plugin/hoi_vien.json` `"bat": false`): mọi module chạy miễn phí. Khi bật ở bản sau, khoá được kiểm trên máy bằng chữ ký, không gọi mạng, không gửi dữ liệu ra ngoài; khoá thiếu / hết hạn chỉ làm module hội viên im, không bao giờ chặn lệnh. Xem: `python3 $P/scripts/hoi_vien.py trang-thai`.

## Test và phát bản (trong nguồn)

```bash
python3 -W ignore -m unittest discover -s tests
```
```bash
python3 scripts/phat_ban.py --loai va --ghi-chu "đã sửa gì"
```

Phát bản luôn chạy từ nguồn. Không sửa tệp trong kho bản (sai băm, bị từ chối khi cập nhật).

## Tắt và gỡ

- Tắt một phần: xem mục Module.
- Tắt nén cho một lệnh: tiền tố `NEN_OFF=1 `. Cho cả máy: `{"che_do": "tat"}` trong `~/.claude/plugin-tintmark-tietkiemtoken/cau_hinh.json`.
- Trả `settings.json` và skill về trước khi gộp: `python3 $P/scripts/cai_dat.py go`.
- Tắt plugin: `claude plugin disable tintmark-tietkiemtoken@<tên marketplace>`.
- Xoá dữ liệu: xoá `~/.claude/plugin-tintmark-tietkiemtoken/`.

## An toàn

- Hook luôn fail-open: lỗi bất kỳ thì lệnh chạy và trả output nguyên bản. Hook không chặn lệnh, không đặt quyền.
- Chế độ mặc định `sau` không đổi lệnh. Lệnh lỗi (mã thoát khác 0), lệnh ghép (`| & ; < > ( ) $`), lệnh nhiều dòng, lệnh chạy nền không bị nén. Riêng dạng `cd <thư mục> && <lệnh đơn>` được xét theo `<lệnh đơn>`.
- Thống kê chỉ lưu 2 từ đầu của lệnh và số byte. Output gốc của 8 lệnh vừa nén được giữ tạm trên máy để tái hiện khi bị báo sai; phản hồi lưu output gốc trong `~/.claude/plugin-tintmark-tietkiemtoken/phan_hoi/`.
- Giới hạn: phiên đang mở không tự nhận bản mới; kênh cập nhật từ xa chưa có (mã từ chối kênh `http…`); không có đường gửi phản hồi ra ngoài máy.
- Phản hồi mở quá 3 ngày: hook báo một dòng, tối đa 1 lần / ngày.

## English summary

`tintmark-tietkiemtoken` is a Claude Code plugin that saves tokens: it shortens the output of common bash commands (git, test runners, build, ls/find/grep, docker, adb, long logs) after they run (PostToolUse `updatedToolOutput`, the command itself is never changed), warns at 300k / 350k context and guides a hand-off to a new session, keeps a local feedback log, can disable a misbehaving filter on its own, and updates from a local release store with hash check, tests, smoke test and rollback. Pure Python 3 standard library, runs locally, sends nothing off the machine. Hooks are fail-open: any error returns the original output. Each part (compression, self-repair, context warnings, loop reminders, auto-update, voice-approval bridge via a synced Google Drive folder) can be switched off with `scripts/module.py`. A local, signature-based membership check exists but is OFF in this release; it never calls a server and never blocks a command. Documentation is in Vietnamese.

**License:** proprietary, all rights reserved (see `LICENSE`): free to read, install and use for your own personal or internal work; no copying, redistribution or resale without written permission.

---
Bản quyền © 2026 Tintmark. Bảo lưu mọi quyền. Điều khoản: `LICENSE`; tác giả và thành phần bên thứ ba: `NOTICE`.
