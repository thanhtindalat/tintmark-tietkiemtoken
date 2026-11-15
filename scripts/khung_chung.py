#!/usr/bin/env python3
# Copyright (c) 2026 Tintmark. All rights reserved. Xem LICENSE / NOTICE.
"""Lớp chung của khung plugin bản quyền Tintmark (chép nguyên vào scripts/ của mỗi plugin, KHÔNG sửa tại plugin).

Đọc `.claude-plugin/khung.json` của plugin chứa tệp này:
  {"ten": "<tên plugin>",
   "du_lieu": {"ten": "plugin-<tên>", "ten_cu": ["..."], "bien": "<BIẾN_MÔI_TRƯỜNG đổi thư mục dữ liệu>"},
   "bien_tat_module": "<BIẾN chứa danh sách module tắt, cách nhau dấu phẩy>",
   "test": {"bien_tam": ["BIẾN", ...], "bo_bien": ["BIẾN", ...]},
   "thu_khoi": {"dau_vao": {...}, "kich": [{"tep": "scripts/x.py", "phai_in": "chuỗi"}, {"mau": "skills/*/y.py"}]}}
Thiếu khung.json thì dùng mặc định theo tên thư mục plugin. Không gọi mạng, không in gì.
"""
import json
import os

PHIEN_BAN_KHUNG = "0.1.0"
GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def doc_json(duong, mac_dinh=None):
    try:
        with open(duong, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return mac_dinh


def ghi_json(duong, du_lieu):
    os.makedirs(os.path.dirname(duong), exist_ok=True)
    tam = "%s.tam%d" % (duong, os.getpid())
    with open(tam, "w", encoding="utf-8") as f:
        json.dump(du_lieu, f, ensure_ascii=False, indent=1)
    os.replace(tam, duong)


def khung(goc=None):
    d = doc_json(os.path.join(goc or GOC, ".claude-plugin", "khung.json"), {})
    return d if isinstance(d, dict) else {}


def plugin_json(goc=None):
    d = doc_json(os.path.join(goc or GOC, ".claude-plugin", "plugin.json"), {})
    return d if isinstance(d, dict) else {}


def ten(goc=None):
    return khung(goc).get("ten") or plugin_json(goc).get("name") or os.path.basename(goc or GOC)


def phien_ban(goc=None):
    return plugin_json(goc).get("version", "?")


def thu_muc_du_lieu():
    """~/.claude/<du_lieu.ten>; biến môi trường du_lieu.bien đổi được (dùng cho test).
    Chưa có thư mục tên mới thì đọc tiếp thư mục tên cũ (đổi tên plugin không mất dữ liệu)."""
    dl = khung().get("du_lieu") or {}
    bien = dl.get("bien")
    if bien and os.environ.get(bien):
        return os.environ[bien]
    nha = os.path.join(os.path.expanduser("~"), ".claude")
    moi = os.path.join(nha, dl.get("ten") or "plugin-" + ten())
    if not os.path.exists(moi):
        for cu in dl.get("ten_cu") or []:
            if os.path.isdir(os.path.join(nha, cu)):
                return os.path.join(nha, cu)
    return moi


def tep(*ten_tep):
    return os.path.join(thu_muc_du_lieu(), *ten_tep)


def them_thong_bao(tin):
    """Hàng chờ thông báo một dòng (tối đa 10); hook của plugin in ra một lần rồi xoá."""
    try:
        ds = doc_json(tep("thong_bao.json"), [])
        ds = ds if isinstance(ds, list) else []
        if tin not in ds:
            ds.append(tin)
            ghi_json(tep("thong_bao.json"), ds[-10:])
    except Exception:
        pass


def tep_du_an(cwd):
    """Tệp cấu hình riêng của dự án: <thư mục>/.claude/<tên>.json, tìm từ cwd lên tối đa 8 cấp."""
    d = cwd or ""
    for _ in range(8):
        if not d or d == os.path.dirname(d):
            return None
        p = os.path.join(d, ".claude", ten() + ".json")
        if os.path.isfile(p):
            return p
        d = os.path.dirname(d)
    return None
