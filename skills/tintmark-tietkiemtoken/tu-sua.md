# Tự sửa bộ lọc nén

Dùng khi có phản hồi đang mở hoặc bộ lọc bị tự tắt. Cần thư mục **nguồn** của plugin (nơi sửa mã, khác bản đang cài): khai ở `"nguon"` trong `~/.claude/plugin-tintmark-tietkiemtoken/cap_nhat.json`, hoặc đưa `--nguon <thư mục>` ngay sau `tu_sua.py`. Máy không có nguồn thì chỉ ghi phản hồi, không sửa được. `P` là thư mục plugin (xem `nen-lenh.md`).

## 4 bước

**1. Quét**

```bash
python3 $P/scripts/tu_sua.py quet
```

In phản hồi đang mở theo từng bộ lọc, bộ lọc nào đang tắt và có output gốc hay không.

**2. Tái hiện thành ca test**

```bash
python3 $P/scripts/tu_sua.py tai-hien PH-261115-015523-ac85 --giu "ten_container_bi_mat"
```

- `--giu` là chuỗi phải còn sau khi nén (dòng / cột đã bị mất); lặp `--giu` cho nhiều chuỗi.
- Lệnh chép output gốc thành `<nguồn>/tests/phan_hoi/<mã>/goc.txt` + `ca.json` rồi chạy test. Test phải **ĐỎ**. Test đạt nghĩa là luật không làm mất chuỗi đó: xem lại phản hồi, có thể đóng `khong-loi`.
- Phản hồi không có output gốc thì lệnh từ chối: chạy lại lệnh gốc với `NEN_OFF=1`, lưu ra tệp, `phan_hoi.py bao --goc <tệp>` rồi làm lại bước này.

**3. Sửa luật**

Sửa `<nguồn>/luat/luat.json` (ít khi phải sửa `scripts/nen_loi.py`). Mỗi luật có: `id`, `match` (biểu thức khớp lệnh), `exclude`, `drop` (bỏ dòng khớp), `keep` (dòng luôn giữ), `replace`, `mask`, `dedupe`, `max_line_len`, `max_lines`, `max_lines_fail`, `min_bytes`. Sửa ở mức nhỏ nhất làm ca test xanh; không nới tới mức bộ lọc hết tác dụng. Chạy test trong nguồn:

```bash
python3 -W ignore -m unittest discover -s tests
```

**4. Xong**

```bash
python3 $P/scripts/tu_sua.py xong PH-261115-015523-ac85 --ghi-chu "docker-list: không cắt cột NAMES"
```

Lệnh này chạy toàn bộ test → phát bản vá vào kho bản (tăng số, ghi nhật ký) → cập nhật bản cài → bật lại bộ lọc → đóng phản hồi. Bước nào hỏng thì dừng, phản hồi vẫn mở, bộ lọc vẫn tắt. Nhiều phản hồi cùng một lần sửa: liệt kê nhiều mã. `--khong-cap-nhat` chỉ phát bản, không đổi bản cài. `--loai nho|lon` khi thay đổi lớn hơn bản vá.

## Lưu ý

- `goc.txt` là output thật trên máy (có thể chứa tên tệp, tên máy). Làm sạch trước khi đưa kho ra ngoài.
- Không sửa tệp trong kho bản (`kho_ban/<bản>/`): sai băm, `cap_nhat.py` sẽ từ chối bản đó.
- Sau khi cập nhật, phiên đang mở nhận bộ lọc mới khi mở lại hoặc `/reload-plugins`.
