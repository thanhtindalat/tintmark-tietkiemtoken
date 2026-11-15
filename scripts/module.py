#!/usr/bin/env python3
# Copyright (c) 2026 Tintmark. All rights reserved. Xem LICENSE / NOTICE.
"""Bật / tắt từng module của plugin (khung plugin bản quyền Tintmark).

Danh sách module: `.claude-plugin/module.json`
  {"module": {"<id>": {"mo_ta": "...", "mac_dinh": true, "hoi_vien": false, "tep": ["scripts/..."]}}}
Thứ tự ghi đè (sau thắng trước):
  1. mac_dinh trong module.json
  2. <dữ liệu máy>/cau_hinh.json  {"module": {"<id>": false}}   (lệnh: module.py tat <id>)
  3. <dự án>/.claude/<tên plugin>.json  {"module": {"<id>": false}}   (riêng một thư mục)
  4. biến môi trường ghi trong khung.json "bien_tat_module": danh sách id tắt, cách nhau dấu phẩy
  5. module "hoi_vien": true chỉ chạy khi hoi_vien.duoc_dung(id) (mặc định cơ chế hội viên TẮT => chạy)

  module.py ds [--cwd THƯ_MỤC]     liệt kê module, trạng thái, lý do
  module.py bat <id> | tat <id>    ghi vào cấu hình máy

An toàn: lỗi bất kỳ khi đọc cấu hình => module chạy theo mặc định; id lạ => coi là bật.
Module tắt chỉ làm hook của nó im lặng, không bao giờ chặn lệnh của người dùng.
Thêm module mới: thêm một mục vào module.json rồi đầu hook của module gọi `module.bat("<id>", cwd)`.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import khung_chung as kc  # noqa: E402


def danh_sach():
    d = kc.doc_json(os.path.join(kc.GOC, ".claude-plugin", "module.json"), {}) or {}
    m = d.get("module") if isinstance(d, dict) else None
    return m if isinstance(m, dict) else {}


def _ghi_de(duong):
    d = kc.doc_json(duong, {}) if duong else {}
    m = d.get("module") if isinstance(d, dict) else None
    return {k: bool(v) for k, v in m.items()} if isinstance(m, dict) else {}


def trang_thai(cwd=None, hoi_vien_tt=None):
    """{id: (bat, nguon)}; hoi_vien_tt dùng cho test, mặc định đọc hoi_vien.trang_thai()."""
    ds = danh_sach()
    may = _ghi_de(kc.tep("cau_hinh.json"))
    du_an = _ghi_de(kc.tep_du_an(cwd or os.getcwd()))
    bien = kc.khung().get("bien_tat_module")
    tat_env = {x.strip() for x in (os.environ.get(bien, "") if bien else "").split(",") if x.strip()}
    kq = {}
    for mid, tt in ds.items():
        tt = tt if isinstance(tt, dict) else {}
        bat, nguon = bool(tt.get("mac_dinh", True)), "mặc định"
        if mid in may:
            bat, nguon = may[mid], "cấu hình máy"
        if mid in du_an:
            bat, nguon = du_an[mid], "cấu hình dự án"
        if mid in tat_env:
            bat, nguon = False, "biến %s" % bien
        if bat and tt.get("hoi_vien"):
            import hoi_vien
            if not hoi_vien.duoc_dung(mid, hoi_vien_tt):
                bat, nguon = False, "cần khoá hội viên"
        kq[mid] = (bat, nguon)
    return kq


def bat(mid, cwd=None):
    """True nếu module được chạy. Không bao giờ ném lỗi."""
    try:
        return trang_thai(cwd).get(mid, (True, ""))[0]
    except Exception:
        return True


def dat(mid, gia_tri):
    duong = kc.tep("cau_hinh.json")
    d = kc.doc_json(duong, {})
    d = d if isinstance(d, dict) else {}
    m = d.get("module") if isinstance(d.get("module"), dict) else {}
    m[mid] = bool(gia_tri)
    d["module"] = m
    kc.ghi_json(duong, d)


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv) or ["ds"]
    cwd = a[a.index("--cwd") + 1] if "--cwd" in a else None
    if a[0] == "ds":
        ds = danh_sach()
        for mid, (b, nguon) in trang_thai(cwd).items():
            tt = ds.get(mid) or {}
            print("%-14s %-4s %-18s %s%s" % (mid, "BẬT" if b else "TẮT", nguon, tt.get("mo_ta", ""),
                                              " [hội viên]" if tt.get("hoi_vien") else ""))
        return 0
    if a[0] in ("bat", "tat") and len(a) > 1:
        if a[1] not in danh_sach():
            print("Không có module %s. Có: %s" % (a[1], ", ".join(danh_sach()))); return 1
        dat(a[1], a[0] == "bat")
        print("Đã %s module %s (cấu hình máy). Phiên đang mở nhận ngay ở lần gọi hook kế." % ("bật" if a[0] == "bat" else "tắt", a[1]))
        return 0
    print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main())
