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
  - Thuật toán chữ ký: XAC_MINH[tên] = hàm(noi_dung_bytes, chu_ky_bytes, khoa_cong_khai) -> bool.
    Có sẵn "ed25519" (RFC 8032, Python thuần, chỉ XÁC MINH; chọn 15/11): khoa_cong_khai = base64 của 32 byte.
    Khoá bí mật và việc ký nằm ở `khung_plugin_ban_quyen/cong_cu/cap_khoa.py`, KHÔNG đi theo plugin.
    thuat_toan null / lạ => bat = true cũng coi mọi khoá là chưa hợp lệ.

  hoi_vien.py trang-thai           in trạng thái
  hoi_vien.py nap <tệp khoá>       kiểm rồi chép khoá vào thư mục dữ liệu máy
"""
import base64
import hashlib
import json
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import khung_chung as kc  # noqa: E402

# ---- Ed25519 (RFC 8032 mục 5.1, bản tham chiếu), Python thuần, không thư viện ngoài ----
_P = 2 ** 255 - 19
_Q = 2 ** 252 + 27742317777372353535851937790883648493


def _inv(x):
    return pow(x, _P - 2, _P)


_D = -121665 * _inv(121666) % _P
_CAN_M1 = pow(2, (_P - 1) // 4, _P)


def _cong(a, b):
    A = (a[1] - a[0]) * (b[1] - b[0]) % _P
    B = (a[1] + a[0]) * (b[1] + b[0]) % _P
    C = 2 * a[3] * b[3] * _D % _P
    D = 2 * a[2] * b[2] % _P
    E, F, G, H = B - A, D - C, D + C, B + A
    return (E * F % _P, G * H % _P, F * G % _P, E * H % _P)


def _nhan(s, a):
    kq = (0, 1, 1, 0)
    while s > 0:
        if s & 1:
            kq = _cong(kq, a)
        a = _cong(a, a)
        s >>= 1
    return kq


def _bang(a, b):
    return (a[0] * b[2] - b[0] * a[2]) % _P == 0 and (a[1] * b[2] - b[1] * a[2]) % _P == 0


def _tim_x(y, dau):
    if y >= _P:
        return None
    x2 = (y * y - 1) * _inv(_D * y * y + 1) % _P
    if x2 == 0:
        return None if dau else 0
    x = pow(x2, (_P + 3) // 8, _P)
    if (x * x - x2) % _P:
        x = x * _CAN_M1 % _P
    if (x * x - x2) % _P:
        return None
    return _P - x if (x & 1) != dau else x


_GY = 4 * _inv(5) % _P
_GX = _tim_x(_GY, 0)
_G = (_GX, _GY, 1, _GX * _GY % _P)


def _nen_diem(a):
    zi = _inv(a[2])
    x, y = a[0] * zi % _P, a[1] * zi % _P
    return (y | ((x & 1) << 255)).to_bytes(32, "little")


def _mo_diem(b):
    if len(b) != 32:
        return None
    y = int.from_bytes(b, "little")
    dau, y = y >> 255, y & ((1 << 255) - 1)
    x = _tim_x(y, dau)
    return None if x is None else (x, y, 1, x * y % _P)


def _bam_q(b):
    return int.from_bytes(hashlib.sha512(b).digest(), "little") % _Q


def ed25519_xac_minh(cong_khai, thong_diep, chu_ky):
    """True nếu chu_ky (64 byte) là chữ ký Ed25519 hợp lệ của thong_diep theo khoá công khai 32 byte."""
    if len(cong_khai) != 32 or len(chu_ky) != 64:
        return False
    A, R = _mo_diem(cong_khai), _mo_diem(chu_ky[:32])
    if A is None or R is None:
        return False
    s = int.from_bytes(chu_ky[32:], "little")
    if s >= _Q:
        return False
    h = _bam_q(chu_ky[:32] + cong_khai + thong_diep)
    return _bang(_nhan(s, _G), _cong(R, _nhan(h, A)))


def _xm_ed25519(nd_b, ck_b, khoa_cong_khai):
    try:
        ck = base64.b64decode(khoa_cong_khai or "", validate=True)
    except Exception:
        return False
    return ed25519_xac_minh(ck, nd_b, ck_b)


XAC_MINH = {"ed25519": _xm_ed25519}   # tên thuật toán -> hàm xác minh


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
