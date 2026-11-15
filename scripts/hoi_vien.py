#!/usr/bin/env python3
# Copyright (c) 2026 Tintmark. All rights reserved. Xem LICENSE / NOTICE.
"""Cơ chế khoá hội viên (khung plugin bản quyền Tintmark). MẶC ĐỊNH TẮT.

Chỉ là cơ chế: chưa thu phí, chưa có máy chủ cấp khoá. Kiểm hoàn toàn trên máy, KHÔNG gọi mạng,
KHÔNG gửi dữ liệu ra ngoài. Đây là "cản người ngại phiền", không phải bảo vệ tuyệt đối: mã chạy
trên máy người dùng thì luôn sửa được.

Cấu hình (đi theo bản plugin, người dùng không bật / tắt): `.claude-plugin/hoi_vien.json`
  {"bat": false, "thuat_toan": null, "khoa_cong_khai": null, "tep_khoa": "khoa_hoi_vien.json", "lien_he": ""}
Khoá của người dùng: <dữ liệu máy>/<tep_khoa>
  {"noi_dung": "<base64 của JSON>", "chu_ky": "<base64>"}
  JSON nội dung: {"plugin": "<tên>", "nguoi": "...", "goi": ["<id module>" | "*"], "cap": "YYYY-MM-DD", "het_han": "YYYY-MM-DD"}
  Chữ ký ký trên đúng các byte của nội dung (sau base64), không chuẩn hoá lại JSON.

Quy tắc:
  - bat = false => mọi module chạy (trạng thái hiện tại của mọi plugin).
  - bat = true  => module có "hoi_vien": true trong module.json chỉ chạy khi khoá hợp lệ, còn hạn, đúng plugin,
    có id module trong "goi"; module thường luôn chạy.
  - Fail-open: lỗi trong chính mã kiểm (ngoại lệ) => cho chạy. Khoá thiếu / sai / hết hạn => chỉ module hội viên im,
    KHÔNG BAO GIỜ chặn lệnh của người dùng hay làm hỏng phiên.
  - Thuật toán chữ ký: đăng ký vào XAC_MINH[tên] = hàm(noi_dung_bytes, chu_ky_bytes, khoa_cong_khai) -> bool.
    Chưa đăng ký thuật toán nào (chờ chủ plugin chọn) => bat = true cũng coi mọi khoá là chưa hợp lệ.

  hoi_vien.py trang-thai           in trạng thái
  hoi_vien.py nap <tệp khoá>       kiểm rồi chép khoá vào thư mục dữ liệu máy
"""
import base64
import json
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import khung_chung as kc  # noqa: E402

XAC_MINH = {}   # tên thuật toán -> hàm xác minh; thêm khi chủ plugin chọn thuật toán


def cau_hinh():
    d = kc.doc_json(os.path.join(kc.GOC, ".claude-plugin", "hoi_vien.json"), {}) or {}
    c = {"bat": False, "thuat_toan": None, "khoa_cong_khai": None, "tep_khoa": "khoa_hoi_vien.json", "lien_he": ""}
    if isinstance(d, dict):
        c.update({k: v for k, v in d.items() if k in c})
    return c


def kiem_khoa(khoa, c, hom_nay=None):
    """(hop_le, ly_do, noi_dung). Không ném lỗi do dữ liệu khoá xấu."""
    if not isinstance(khoa, dict):
        return False, "chưa có khoá", None
    ham = XAC_MINH.get(c.get("thuat_toan") or "")
    if ham is None:
        return False, "chưa chọn thuật toán chữ ký", None
    try:
        nd_b = base64.b64decode(khoa.get("noi_dung") or "", validate=True)
        ck_b = base64.b64decode(khoa.get("chu_ky") or "", validate=True)
        nd = json.loads(nd_b.decode("utf-8"))
    except Exception:
        return False, "khoá hỏng định dạng", None
    if not isinstance(nd, dict):
        return False, "khoá hỏng định dạng", None
    if not ham(nd_b, ck_b, c.get("khoa_cong_khai")):
        return False, "chữ ký sai", nd
    if nd.get("plugin") != kc.ten():
        return False, "khoá của plugin khác (%s)" % nd.get("plugin"), nd
    hom_nay = hom_nay or time.strftime("%Y-%m-%d")
    if str(nd.get("het_han") or "") < hom_nay:
        return False, "hết hạn %s" % nd.get("het_han"), nd
    return True, "hợp lệ tới %s" % nd.get("het_han"), nd


def trang_thai(c=None, khoa=None):
    c = c or cau_hinh()
    if not c.get("bat"):
        return {"bat": False, "hop_le": True, "ly_do": "cơ chế hội viên đang tắt: mọi module chạy", "goi": ["*"]}
    if khoa is None:
        khoa = kc.doc_json(kc.tep(c.get("tep_khoa") or "khoa_hoi_vien.json"))
    hop_le, ly_do, nd = kiem_khoa(khoa, c)
    goi = (nd or {}).get("goi") if hop_le else []
    return {"bat": True, "hop_le": hop_le, "ly_do": ly_do, "goi": goi if isinstance(goi, list) else [],
            "het_han": (nd or {}).get("het_han"), "lien_he": c.get("lien_he")}


def duoc_dung(mid, tt=None):
    """Module hội viên `mid` có được chạy không. Lỗi trong mã kiểm => True (fail-open)."""
    try:
        tt = tt if tt is not None else trang_thai()
        if not tt.get("bat"):
            return True
        return bool(tt.get("hop_le")) and ("*" in tt["goi"] or mid in tt["goi"])
    except Exception:
        return True


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv) or ["trang-thai"]
    if a[0] == "trang-thai":
        tt = trang_thai()
        print("Hội viên: %s · %s" % ("BẬT" if tt["bat"] else "TẮT", tt["ly_do"]))
        if tt["bat"] and not tt["hop_le"] and tt.get("lien_he"):
            print("Liên hệ cấp khoá: %s" % tt["lien_he"])
        return 0
    if a[0] == "nap" and len(a) > 1:
        c = cau_hinh()
        khoa = kc.doc_json(a[1])
        hop_le, ly_do, _ = kiem_khoa(khoa, c)
        if not hop_le:
            print("Khoá không dùng được: %s. Không chép." % ly_do); return 1
        dich = kc.tep(c["tep_khoa"])
        os.makedirs(os.path.dirname(dich), exist_ok=True)
        shutil.copy2(a[1], dich)
        print("Đã nạp khoá (%s)%s." % (ly_do, "" if c["bat"] else "; cơ chế hội viên của bản này đang tắt"))
        return 0
    print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main())
