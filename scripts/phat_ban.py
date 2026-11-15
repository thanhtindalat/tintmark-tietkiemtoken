#!/usr/bin/env python3
# Copyright (c) 2026 Tintmark. All rights reserved. Xem LICENSE / NOTICE.
"""Phát một bản mới vào kho bản CỤC BỘ (khung plugin bản quyền Tintmark; không đẩy git, không ra ngoài máy).

  phat_ban.py --loai va|nho|lon --ghi-chu "đã sửa gì" [--kho THƯ_MỤC] [--nguon THƯ_MỤC_NGUỒN]

Chạy toàn bộ test trước; test hỏng => dừng, không đổi gì. Đạt => tăng số bản trong plugin.json,
ghi NHAT_KY_THAY_DOI.md, chép nguồn sang <kho>/<bản>/, ghi băm vào <kho>/kenh.json.
"""
import argparse
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cap_nhat  # noqa: E402
import khung_chung as kc  # noqa: E402


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--loai", choices=["va", "nho", "lon"], default="va")
    p.add_argument("--ghi-chu", required=True)
    p.add_argument("--kho"); p.add_argument("--nguon")
    o = p.parse_args(argv)
    nguon = os.path.abspath(o.nguon or kc.GOC)
    mf = os.path.join(nguon, ".claude-plugin", "plugin.json")
    d = kc.doc_json(mf)
    if not d:
        print("Không đọc được", mf); return 1
    kho = os.path.abspath(o.kho or os.path.join(os.path.dirname(nguon), "kho_ban", d["name"]))
    if os.path.commonpath([nguon, kho]) == kho:
        print("Nguồn nằm trong kho bản: phát bản phải chạy từ thư mục nguồn đang sửa."); return 1
    dat, tin = cap_nhat.chay_test(nguon)
    if not dat:
        print("TEST HỎNG, không phát bản: %s" % tin); return 1
    a = list(cap_nhat.so(d["version"])) + [0, 0]
    a = {"lon": [a[0] + 1, 0, 0], "nho": [a[0], a[1] + 1, 0], "va": [a[0], a[1], a[2] + 1]}[o.loai]
    moi = ".".join(str(x) for x in a)
    dich = os.path.join(kho, moi)
    if os.path.exists(dich):
        print("Bản %s đã có trong kho." % moi); return 1
    cu = d["version"]
    d["version"] = moi
    kc.ghi_json(mf, d)
    nk = os.path.join(nguon, "NHAT_KY_THAY_DOI.md")
    dau = "# Nhật ký thay đổi — " + d["name"] + "\n"
    than = open(nk, encoding="utf-8").read().replace(dau, "", 1) if os.path.isfile(nk) else ""
    with open(nk, "w", encoding="utf-8") as f:
        f.write("%s\n## %s — %s\n- %s\n%s" % (dau, moi, time.strftime("%d/%m/%Y"), o.ghi_chu, than))
    shutil.copytree(nguon, dich, ignore=shutil.ignore_patterns("__pycache__", ".DS_Store", "*.pyc"))
    tk = os.path.join(kho, "kenh.json")
    k = kc.doc_json(tk, {}) or {}
    k.setdefault("ten", d["name"]); k.setdefault("ban", {})
    k["ban"][moi] = {"duong": moi, "sha256": cap_nhat.bam_cay(dich), "ngay": time.strftime("%Y-%m-%d"),
                     "ghi_chu": o.ghi_chu, "tu_ban": cu}
    k["ban_moi_nhat"] = moi
    kc.ghi_json(tk, k)
    print("Đã phát bản %s (từ %s) vào %s · test: %s" % (moi, cu, dich, tin))
    return 0


if __name__ == "__main__":
    sys.exit(main())
