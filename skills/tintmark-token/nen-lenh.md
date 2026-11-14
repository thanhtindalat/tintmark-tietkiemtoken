# Nén output lệnh bash (plugin tintmark-tietkiem)

Plugin `tintmark-tietkiem` rút gọn kết quả của lệnh bash quen thuộc trước khi model đọc. Python 3 thư viện chuẩn, chạy trên máy, không gửi gì ra ngoài, không dùng API trả phí. Chỉ có ở Claude Code; Claude Chat không có phần này.

Trong các lệnh dưới đây `P` là thư mục plugin đang cài. Máy đã chạy `cai_dat.py gop` thì:

```bash
P=~/.claude/skills/tintmark-token/../..
```

## Cách hoạt động

- Mặc định là chế độ `sau`: lệnh chạy nguyên bản, xong rồi hook `PostToolUse` mới rút gọn output. Lệnh không bị đổi nên không vướng bộ duyệt quyền / auto mode.
- Chỉ nén khi đủ cả: lệnh đơn giản (không có `| & ; < > ( ) $` , không xuống dòng (riêng `cd <thư mục> && <lệnh đơn>` được xét theo lệnh đơn), không gán biến đầu lệnh, không chạy nền), có luật khớp, output đủ dài (`min_bytes` của luật), và lệnh thành công. **Lệnh lỗi (mã thoát khác 0) không bao giờ bị nén.**
- Chỗ bị cắt có dòng `… [nén: bỏ N dòng — chạy lại với NEN_OFF=1 để xem đủ]`.
- 19 bộ lọc trong `luat/luat.json`: `git-status`, `git-diff`, `git-log-gon`, `git-log`, `git-ghi` (push / pull / commit / branch…), `pytest`, `unittest`, `node-test`, `cargo-test`, `build-lint`, `ls`, `find`, `grep`, `adb-logcat`, `adb`, `docker-build`, `docker-logs`, `docker-list`, `log-dai`.
- Luật riêng của máy (script nội bộ…): `~/.claude/plugin-tintmark-tietkiem/luat_rieng.json`, cùng dạng `luat/luat.json`, đứng trước luật mặc định.
- Không nén: công cụ đọc tệp / tìm kiếm sẵn có của Claude Code, lệnh ghép, script riêng chưa có luật.
- Hook hỏng bất kỳ chỗ nào thì im lặng, model nhận output gốc. Hook không chặn lệnh.

## Kỳ vọng thật

Tác dụng: phiên phình chậm hơn. Không thay được việc đổi phiên theo ngưỡng (`ban-giao.md`). Mức giảm tuỳ lệnh: danh sách dài (`find`, log) giảm nhiều, output ngắn gần như không đổi. Số "~token" plugin báo là byte / 4, là ước tính, không phải hoá đơn.

## Lệnh dùng

| Việc | Lệnh |
|---|---|
| Xem đã nén được bao nhiêu | `python3 $P/scripts/thong_ke.py --days 7 --theo luat` (`--theo lenh` / `ngay`) |
| Cần output đầy đủ của một lệnh | thêm `NEN_OFF=1 ` trước lệnh đó |
| Chạy thử một lệnh qua bộ nén, ngoài hook | `python3 $P/scripts/nen.py -c "git status"` |
| Bản đang cài, chế độ nén, đã gộp chưa | `python3 $P/scripts/cai_dat.py trang-thai` |
| Bộ lọc nào đang bị tắt, phản hồi nào đang mở | `python3 $P/scripts/phan_hoi.py liet-ke` |
| Tắt nén cả máy | ghi `{"che_do": "tat"}` vào `~/.claude/plugin-tintmark-tietkiem/cau_hinh.json` |
| Tắt nén cho một phiên | mở phiên với biến môi trường `NEN_OFF=1` |

Dữ liệu của plugin nằm ở `~/.claude/plugin-tintmark-tietkiem/` (thống kê, phản hồi, sao lưu, cấu hình). Thống kê chỉ lưu 2 từ đầu của lệnh và số byte.

## Lưu ý quan trọng về `NEN_OFF=1`

Chạy lại **đúng lệnh vừa bị nén** với `NEN_OFF=1` trong vòng 15 phút được plugin hiểu là "nghi bộ lọc làm mất thông tin" và tự ghi một dấu hiệu. Đủ 3 dấu hiệu trong 7 ngày thì bộ lọc đó tự tắt. Vì vậy chỉ dùng `NEN_OFF=1` khi thật sự thiếu thông tin. Bộ lọc cắt mất dòng cần dùng thì báo luôn theo `phan-hoi.md`.

## Khi nghi nén làm hỏng việc

Dấu hiệu: thiếu dòng trong `git diff` / `git log`, kết quả `grep` / `find` thiếu thứ đang tìm, bảng bị cắt cột. Làm: chạy lại với `NEN_OFF=1` để lấy đủ và làm tiếp việc đang dở; rồi ghi phản hồi (`phan-hoi.md`). Sửa bộ lọc theo `tu-sua.md`.

## Phiên đang mở

Phiên chỉ nạp hook của plugin lúc khởi động. Sau khi cài hoặc cập nhật, phiên đang mở nhận bản mới khi mở lại hoặc gõ `/reload-plugins`.

## Chế độ `truoc` (cũ)

Bọc lệnh bằng `nen.py` ở `PreToolUse`. Auto mode từ chối mọi lệnh bị hook đổi, nên ở auto mode chế độ này không đổi lệnh nào. Không bật lại, không dùng `permissionDecision: allow` để lách.
