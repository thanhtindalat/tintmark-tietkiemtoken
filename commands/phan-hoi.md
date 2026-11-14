---
description: Báo plugin tintmark-tietkiem nén sai / mất dòng / nhắc sai (ghi sổ trên máy, không gửi ra ngoài)
argument-hint: "<lệnh bị nén sai> | <mô tả ngắn>"
---
Người dùng báo phản hồi về plugin tintmark-tietkiem: $ARGUMENTS

1. Xác định loại: `nen-sai` (nén làm sai nghĩa), `mat-dong` (mất dòng cần), `nhac-sai` (hook ngưỡng nhắc sai) hoặc `khac`.
2. Chạy (thư mục plugin `P=~/.claude/skills/tintmark-token/../..`):
   `python3 $P/scripts/phan_hoi.py bao --loai <loại> --lenh "<lệnh>" --chay-lai --mo-ta "<mô tả>"`
   (`--chay-lai` chạy lại lệnh với `NEN_OFF=1` để lưu output gốc; bỏ cờ này nếu lệnh có tác dụng phụ.)
3. Báo người dùng một dòng: mã phản hồi và việc tiếp theo (`skills/tintmark-token/phan-hoi.md`, `tu-sua.md`).
