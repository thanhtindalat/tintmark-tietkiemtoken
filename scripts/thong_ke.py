#!/usr/bin/env python3
# Copyright (c) 2026 Tintmark. All rights reserved. Xem LICENSE / NOTICE.
"""Xem tổng tiết kiệm. Ước lượng token ≈ byte/4.

  thong_ke.py [--days N] [--theo lenh|luat|ngay]
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nen_loi  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--theo", choices=["lenh", "luat", "ngay"], default="lenh")
    a = ap.parse_args()
    tep = os.path.join(nen_loi.thu_muc_du_lieu(), "thong_ke.jsonl")
    if not os.path.isfile(tep):
        print("Chưa có số liệu (chưa lệnh nào được nén).")
        return
    tu = time.time() - a.days * 86400
    nhom = {}
    for dong in open(tep, encoding="utf-8"):
        try:
            r = json.loads(dong)
        except Exception:
            continue
        if r["ts"] < tu:
            continue
        k = {"lenh": r["lenh"], "luat": r["luat"], "ngay": time.strftime("%Y-%m-%d", time.localtime(r["ts"]))}[a.theo]
        g = nhom.setdefault(k, [0, 0, 0])
        g[0] += 1; g[1] += r["vao"]; g[2] += r["ra"]
    if not nhom:
        print("Không có số liệu trong %d ngày qua." % a.days)
        return
    print("%-28s %6s %10s %10s %7s %9s" % (a.theo, "lần", "byte vào", "byte ra", "giảm", "~token"))
    tong = [0, 0, 0]
    for k in sorted(nhom):
        n, v, r = nhom[k]
        tong = [tong[0] + n, tong[1] + v, tong[2] + r]
        print("%-28s %6d %10d %10d %6.0f%% %9d" % (k[:28], n, v, r, 100.0 * (v - r) / v if v else 0, (v - r) // 4))
    n, v, r = tong
    print("-" * 76)
    print("%-28s %6d %10d %10d %6.0f%% %9d" % ("TỔNG", n, v, r, 100.0 * (v - r) / v if v else 0, (v - r) // 4))
    print("(~token = byte/4, ước lượng — không phải hoá đơn)")
    print("tintmark-tietkiemtoken · by Tintmark")


if __name__ == "__main__":
    main()
