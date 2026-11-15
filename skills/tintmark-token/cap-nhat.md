# Cập nhật, quay lui, cài và gỡ plugin tintmark-tietkiem

Kênh cập nhật trên máy là **thư mục kho bản cục bộ** (`cap_nhat.py`, chỉ nhận thư mục, từ chối kênh `http…`). Kênh từ xa chính thức là **marketplace GitHub**: cài `claude plugin marketplace add <chủ>/tintmark-tietkiem` rồi `claude plugin install tintmark-tietkiem@tintmark-tietkiem`; cập nhật `claude plugin marketplace update tintmark-tietkiem` rồi `claude plugin update tintmark-tietkiem@tintmark-tietkiem`. `P` là thư mục plugin (xem `nen-lenh.md`).

## Các thành phần

- **Nguồn**: thư mục đang sửa mã.
- **Kho bản**: `<cạnh nguồn>/kho_ban/tintmark-tietkiem/<số bản>/` + `kenh.json` (danh sách bản, băm sha256 từng bản, bản mới nhất).
- **Liên kết cài đặt**: một liên kết trỏ vào một bản trong kho; Claude Code nạp plugin qua liên kết này. Cập nhật = đổi liên kết.
- **Cấu hình**: `~/.claude/plugin-tintmark-tietkiem/cap_nhat.json` có `kenh`, `lien_ket`, `nguon`, `tu_dong` (`ap_dung` | `bao` | `tat`).

## Lệnh

| Việc | Lệnh |
|---|---|
| So bản đang cài với bản mới nhất | `python3 $P/scripts/cap_nhat.py kiem` |
| Cập nhật lên bản mới nhất | `python3 $P/scripts/cap_nhat.py ap-dung` |
| Chuyển sang một bản cụ thể | `python3 $P/scripts/cap_nhat.py ap-dung --ban 0.2.1` |
| Về bản ngay trước lần cập nhật gần nhất | `python3 $P/scripts/cap_nhat.py quay-lui` |
| Xem lịch sử cập nhật | `python3 $P/scripts/cap_nhat.py lich-su` |

`ap-dung` làm theo thứ tự: kiểm băm bản mới → chạy test của bản mới → sao lưu `settings.json` vào `~/.claude/plugin-tintmark-tietkiem/sao_luu/` → đổi liên kết → thử khói. Sai băm hoặc test hỏng thì giữ bản cũ. Thử khói hỏng thì tự quay lui. Cập nhật xong, phiên đang mở nhận bản mới khi mở lại hoặc `/reload-plugins`.

## Tự cập nhật

Hook ngưỡng gọi nền `cap_nhat.py tu-dong` tối đa một lần mỗi 24 giờ và làm theo `tu_dong`: `ap_dung` tự cập nhật, `bao` chỉ báo có bản mới, `tat` không làm gì. Tắt: sửa `"tu_dong": "tat"` trong `cap_nhat.json`.

## Phát một bản mới

Chạy từ **nguồn**, không chạy từ bản trong kho:

```bash
python3 scripts/phat_ban.py --loai va --ghi-chu "đã sửa gì"
```

Test hỏng thì dừng, không đổi gì. Đạt thì tăng số bản trong `.claude-plugin/plugin.json`, ghi `NHAT_KY_THAY_DOI.md`, chép nguồn sang kho bản, ghi băm vào `kenh.json`. `--loai`: `va` (0.2.1 → 0.2.2), `nho` (→ 0.3.0), `lon` (→ 1.0.0). Phát xong chạy `cap_nhat.py ap-dung` để cài. Phát bản chỉ ghi vào thư mục trên máy, không đẩy git.

## Gộp skill vào plugin (một lần mỗi máy)

Trước khi gộp, skill `tintmark-token` và 2 hook ngưỡng nằm riêng ở `~/.claude/`. Gộp để chỉ còn một bản, cập nhật cùng plugin:

```bash
python3 <liên kết>/scripts/cai_dat.py gop --lien-ket <liên kết> --kenh <kho bản>/kenh.json --nguon <nguồn> --tu-dong ap_dung
```

Lệnh sao lưu `settings.json` (thành `settings.json.truoc-gop-token-<ngày giờ>`), bỏ 2 hook ngưỡng cũ trong `settings.json`, chuyển thư mục skill cũ vào sao lưu và thay bằng liên kết tới skill trong plugin. Kiểm:

```bash
python3 $P/scripts/cai_dat.py trang-thai
```

Phải ra "Hook ngưỡng cũ trong settings.json: 0" và "Skill người dùng: liên kết".

## Gỡ

- Trả `settings.json` và skill về trước khi gộp: `python3 $P/scripts/cai_dat.py go`. Thay đổi `settings.json` làm sau lần gộp sẽ mất (bản ngay trước khi gỡ lưu ở `settings.json.truoc-go-<ngày giờ>`).
- Tắt plugin: `claude plugin disable tintmark-tietkiem@<marketplace>`.
- Xoá dữ liệu: xoá thư mục `~/.claude/plugin-tintmark-tietkiem/`.

## Bản Claude Code ghi nhận

Marketplace dạng thư mục: phiên mới nạp plugin qua liên kết cài đặt (bản `cap_nhat.py` vừa đặt), còn `~/.claude/plugins/installed_plugins.json` chỉ ghi bản lúc `claude plugin install` / `update`. Hai số có thể lệch; `cai_dat.py trang-thai` in cả hai và báo `⚠ LỆCH`. Đồng bộ ghi chép bằng lệnh, không sửa tay JSON: `claude plugin marketplace update <marketplace>` rồi `claude plugin update tintmark-tietkiem@<marketplace>`. Kiểm thành phần đang nạp: `claude plugin details tintmark-tietkiem@<marketplace>` (phải có Hooks PostToolUse + UserPromptSubmit).
