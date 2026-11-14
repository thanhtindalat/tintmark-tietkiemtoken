# Phản hồi khi nén sai

Sổ phản hồi nằm trên máy (`~/.claude/plugin-tintmark-tietkiem/phan_hoi/`). Không gửi gì ra ngoài máy. `P` là thư mục plugin (xem `nen-lenh.md`).

## Khi nào ghi

- Output đã nén thiếu dòng cần dùng, cắt mất cột, hoặc làm hiểu sai kết quả lệnh: loại `mat-dong` hoặc `nen-sai`.
- Hook ngưỡng nhắc sai lúc (nhắc khi phiên còn nhỏ, không nhắc khi đã đầy): loại `nhac-sai`.
- Việc khác của plugin: loại `khac`.

Người dùng nói "nén sai", "mất dòng", "thiếu kết quả" về một lệnh thì phiên tự ghi phản hồi, không cần hỏi lại.

## Ghi một phản hồi

```bash
python3 $P/scripts/phan_hoi.py bao --loai mat-dong --lenh "docker ps -a" --mo-ta "mất cột NAMES"
```

- `--lenh` là lệnh gốc, viết đúng như đã chạy. Plugin tự tìm bộ lọc khớp và lấy output gốc còn giữ của 8 lệnh vừa nén gần nhất.
- Không còn output gốc thì thêm `--chay-lai` (plugin tự chạy lại lệnh một lần; **chỉ dùng cho lệnh chỉ đọc**), hoặc chạy lại tay với `NEN_OFF=1`, lưu ra tệp và đưa `--goc <tệp>`.
- Tuỳ chọn khác: `--nen <tệp output đã nén>`, `--luat <mã bộ lọc>`, `--ma <mã thoát>`.
- Lệnh in mã phản hồi dạng `PH-<ngày>-<giờ>-<4 ký tự>` và báo có output gốc hay không. Không có output gốc thì khó tái hiện.

## Xem và đóng

```bash
python3 $P/scripts/phan_hoi.py liet-ke
```
```bash
python3 $P/scripts/phan_hoi.py liet-ke --tat-ca
```
```bash
python3 $P/scripts/phan_hoi.py xem PH-261115-015523-ac85
```
```bash
python3 $P/scripts/phan_hoi.py dong PH-261115-015523-ac85 --ket-qua khong-loi --ghi-chu "output gốc cũng không có dòng đó"
```

`--ket-qua`: `da-sua`, `khong-loi`, `bo-qua`. Phản hồi đã sửa bằng quy trình `tu-sua.md` thì lệnh `tu_sua.py xong` tự đóng, không đóng tay.

## Tự tắt bộ lọc

Một bộ lọc bị tắt riêng (các bộ lọc khác vẫn chạy) khi trong 7 ngày có:

- 2 phản hồi do người / phiên báo, hoặc
- 3 dấu hiệu tự ghi (cùng một lệnh vừa nén bị chạy lại với `NEN_OFF=1` trong 15 phút).

Bộ lọc đang tắt thì lệnh đó trả output gốc. `liet-ke` in dòng "Bộ lọc đang tắt". Bật lại sau khi sửa: `tu_sua.py xong` tự bật; bật tay: `python3 $P/scripts/tu_sua.py bat <mã bộ lọc>`.

Ngưỡng đổi được trong `~/.claude/plugin-tintmark-tietkiem/cau_hinh.json`: `nguong_bao` (mặc định 2), `nguong_nghi` (3), `cua_so_nghi_phut` (15), `so_gan_day` (8).
