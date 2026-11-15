#!/usr/bin/env python3
"""Sổ phản hồi cục bộ của plugin tintmark-tietkiemtoken. KHÔNG gửi gì ra ngoài máy.

  phan_hoi.py bao --loai nen-sai|mat-dong|nhac-sai|khac --lenh "LỆNH GỐC" [--mo-ta "..."]
                  [--goc TỆP_OUTPUT_GỐC] [--nen TỆP_OUTPUT_ĐÃ_NÉN] [--chay-lai] [--luat ID] [--ma 0]
      --chay-lai: tự chạy lại LỆNH một lần để lấy output gốc (CHỈ dùng cho lệnh chỉ đọc).
      Không đưa --goc/--chay-lai thì lấy output gốc còn giữ trong vòng "gần đây" (nếu có).
  phan_hoi.py liet-ke [--tat-ca]
  phan_hoi.py xem ID
  phan_hoi.py dong ID --ket-qua da-sua|khong-loi|bo-qua [--ghi-chu "..."]
Bộ lọc bị báo lặp lại (mặc định 2 phản hồi hoặc 3 dấu hiệu tự ghi trong 7 ngày) tự tắt riêng bộ lọc đó.
"""
import argparse
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nen_loi  # noqa: E402


def doc(t):
    with open(t, encoding="utf-8", errors="replace") as f:
        return f.read()


def main(argv=None):
    p = argparse.ArgumentParser()
    s = p.add_subparsers(dest="viec", required=True)
    a = s.add_parser("bao")
    a.add_argument("--loai", default="nen-sai", choices=["nen-sai", "mat-dong", "nhac-sai", "khac"])
    a.add_argument("--lenh", default="")
    a.add_argument("--mo-ta", default="")
    a.add_argument("--goc"); a.add_argument("--nen"); a.add_argument("--luat", default="")
    a.add_argument("--ma", type=int, default=0)
    a.add_argument("--chay-lai", action="store_true")
    b = s.add_parser("liet-ke"); b.add_argument("--tat-ca", action="store_true")
    c = s.add_parser("xem"); c.add_argument("id")
    d = s.add_parser("dong"); d.add_argument("id")
    d.add_argument("--ket-qua", required=True, choices=["da-sua", "khong-loi", "bo-qua"])
    d.add_argument("--ghi-chu", default="")
    o = p.parse_args(argv)

    if o.viec == "bao":
        luat = o.luat
        if not luat and o.lenh and o.loai != "nhac-sai":
            r = nen_loi.tim_luat(o.lenh, tat=set())
            luat = r.get("id", "") if r else ""
        goc = doc(o.goc) if o.goc else None
        nen_ = doc(o.nen) if o.nen else None
        ma = o.ma
        if goc is None and o.chay_lai and o.lenh:
            r = subprocess.run(["/bin/bash", "-c", o.lenh], capture_output=True, env=dict(os.environ, NEN_OFF="1"))
            goc, ma = (r.stdout + r.stderr).decode("utf-8", "replace"), r.returncode
        if goc is None and o.lenh:
            m = nen_loi.tim_gan_day(o.lenh)
            if m:
                try:
                    goc, ma = doc(nen_loi.tep("gan_day", m["khoa"] + ".txt")), m.get("ma", 0)
                except Exception:
                    pass
        if goc is not None and nen_ is None and luat:
            r = next((x for x in nen_loi.tai_luat() if x.get("id") == luat), None)
            if r:
                nen_ = nen_loi.nen_an_toan(goc, r, ma)
        ma_ph = nen_loi.ghi_phan_hoi(o.loai, o.lenh, luat, o.mo_ta, goc, nen_, ma, "nguoi",
                                     os.environ.get("CLAUDE_SESSION_ID", ""))
        print("Đã ghi %s (bộ lọc: %s; output gốc: %s) tại %s" % (
            ma_ph, luat or "-", "có" if goc is not None else "KHÔNG CÓ, khó tái hiện", nen_loi.tep("phan_hoi", ma_ph)))
        if luat and luat in nen_loi.bo_loc_tat():
            print("Bộ lọc `%s` đang TẮT (trả output gốc) cho tới khi sửa: scripts/tu_sua.py quet" % luat)
    elif o.viec == "liet-ke":
        ds = nen_loi.ds_phan_hoi(chi_mo=not o.tat_ca)
        tat = nen_loi.doc_json(nen_loi.tep("tat_bo_loc.json"), {}) or {}
        print("Bộ lọc đang tắt: %s" % (", ".join(sorted(tat)) or "không"))
        if not ds:
            print("Không có phản hồi %s." % ("nào" if o.tat_ca else "đang mở"))
        for m in ds:
            print("- %s [%s] %s | %s | bộ lọc %s | %s | %s | %s" % (
                m["id"], m.get("trang_thai"), time.strftime("%d/%m %H:%M", time.localtime(m.get("luc", 0))),
                m.get("loai"), m.get("luat") or "-", m.get("nguon"), " ".join((m.get("lenh") or "").split()[:6]),
                m.get("mo_ta") or ""))
    elif o.viec == "xem":
        d_ = nen_loi.tep("phan_hoi", o.id)
        m = nen_loi.doc_json(os.path.join(d_, "meta.json"))
        if not m:
            print("Không có", o.id); return 1
        for k, v in m.items():
            print("%s: %s" % (k, v))
        for t in ("goc.txt", "nen.txt"):
            tp = os.path.join(d_, t)
            if os.path.isfile(tp):
                print("%s: %s (%d byte)" % (t, tp, os.path.getsize(tp)))
    else:
        tp = nen_loi.tep("phan_hoi", o.id, "meta.json")
        m = nen_loi.doc_json(tp)
        if not m:
            print("Không có", o.id); return 1
        m.update(trang_thai="dong", ket_qua=o.ket_qua, ghi_chu=o.ghi_chu, dong_luc=int(time.time()))
        nen_loi.ghi_json(tp, m)
        print("Đã đóng %s: %s" % (o.id, o.ket_qua))
    return 0


if __name__ == "__main__":
    sys.exit(main())
