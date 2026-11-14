#!/usr/bin/env python3
"""Quy trình tự sửa bộ lọc nén từ sổ phản hồi.

  tu_sua.py quet                          phản hồi đang mở theo bộ lọc + bộ lọc đang tắt
  tu_sua.py tai-hien ID --giu "dòng phải còn" [--giu ...]
        chép output gốc của phản hồi thành ca test <nguồn>/tests/phan_hoi/<ID>/ (test sẽ ĐỎ cho tới khi sửa luật)
  tu_sua.py xong ID [ID...] --ghi-chu "đã sửa gì" [--loai va] [--khong-cap-nhat]
        chạy toàn bộ test -> phát bản (tăng số, nhật ký) -> cập nhật bản cài -> bật lại bộ lọc -> đóng phản hồi
  tu_sua.py bat LUAT_ID                   bật lại tay một bộ lọc
Việc "sửa bộ lọc" (sửa luat/luat.json hoặc mã) do phiên làm ở giữa tai-hien và xong; xem skill tu-sua.md.
Thư mục nguồn: --nguon, hoặc "nguon" trong <dữ liệu>/cap_nhat.json.
"""
import argparse
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cap_nhat  # noqa: E402
import nen_loi  # noqa: E402
import phat_ban  # noqa: E402


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--nguon")
    s = p.add_subparsers(dest="viec", required=True)
    s.add_parser("quet")
    a = s.add_parser("tai-hien"); a.add_argument("id"); a.add_argument("--giu", action="append", default=[])
    b = s.add_parser("xong"); b.add_argument("id", nargs="+"); b.add_argument("--ghi-chu", required=True)
    b.add_argument("--loai", default="va"); b.add_argument("--khong-cap-nhat", action="store_true")
    c = s.add_parser("bat"); c.add_argument("luat")
    o = p.parse_args(argv)
    nguon = os.path.abspath(o.nguon or cap_nhat.cau_hinh().get("nguon") or nen_loi.GOC)

    if o.viec == "quet":
        tat = nen_loi.doc_json(nen_loi.tep("tat_bo_loc.json"), {}) or {}
        nhom = {}
        for m in nen_loi.ds_phan_hoi():
            nhom.setdefault(m.get("luat") or "(không rõ bộ lọc)", []).append(m)
        if not nhom and not tat:
            print("Không có phản hồi mở, không bộ lọc nào bị tắt."); return 0
        for luat in sorted(set(nhom) | set(tat)):
            print("== %s%s" % (luat, "  [ĐANG TẮT: %s]" % tat[luat]["ly_do"] if luat in tat else ""))
            for m in nhom.get(luat, []):
                print("   %s  %s  %s  gốc:%s  %s" % (m["id"], m.get("loai"), m.get("nguon"),
                      "có" if os.path.isfile(nen_loi.tep("phan_hoi", m["id"], "goc.txt")) else "không",
                      " ".join((m.get("lenh") or "").split()[:8])))
        print("Bước kế: tu_sua.py tai-hien <ID> --giu \"<dòng bị mất>\" → sửa luật → tu_sua.py xong <ID…> --ghi-chu …")
        return 0
    if o.viec == "tai-hien":
        d = nen_loi.tep("phan_hoi", o.id)
        m = nen_loi.doc_json(os.path.join(d, "meta.json"))
        if not m or not os.path.isfile(os.path.join(d, "goc.txt")):
            print("Phản hồi %s không có output gốc: chạy lại lệnh với NEN_OFF=1, lưu ra tệp, rồi "
                  "phan_hoi.py bao --goc <tệp>." % o.id); return 1
        if not o.giu:
            print("Cần ít nhất một --giu \"<chuỗi phải còn sau khi nén>\"."); return 1
        dich = os.path.join(nguon, "tests", "phan_hoi", o.id)
        os.makedirs(dich, exist_ok=True)
        shutil.copy2(os.path.join(d, "goc.txt"), os.path.join(dich, "goc.txt"))
        nen_loi.ghi_json(os.path.join(dich, "ca.json"), {"id": o.id, "lenh": m.get("lenh"), "luat": m.get("luat"),
                                                         "ma": m.get("ma", 0), "giu": o.giu, "mo_ta": m.get("mo_ta")})
        dat, tin = cap_nhat.chay_test(nguon)
        print("Đã tạo ca test %s. Test hiện %s (%s)." % (dich, "ĐẠT — luật không làm mất các dòng --giu, xem lại phản hồi"
                                                       if dat else "ĐỎ như mong đợi — sửa luật rồi chạy `xong`", tin))
        print("LƯU Ý: goc.txt là output thật trên máy; làm sạch trước khi công khai kho.")
        return 0
    if o.viec == "xong":
        ds = [nen_loi.doc_json(nen_loi.tep("phan_hoi", i, "meta.json")) for i in o.id]
        if not all(ds):
            print("Có mã phản hồi không tồn tại."); return 1
        if phat_ban.main(["--loai", o.loai, "--ghi-chu", "%s (phản hồi %s)" % (o.ghi_chu, ", ".join(o.id)),
                          "--nguon", nguon]) != 0:
            print("Chưa đóng phản hồi, bộ lọc vẫn tắt."); return 1
        ban = (nen_loi.doc_json(os.path.join(nguon, ".claude-plugin", "plugin.json")) or {}).get("version")
        if not o.khong_cap_nhat:
            dat, tin = cap_nhat.ap_dung()
            print(tin)
            if not dat:
                print("Cập nhật không thành: chưa đóng phản hồi, bộ lọc vẫn tắt."); return 1
        import time
        for m in ds:
            m.update(trang_thai="dong", ket_qua="da-sua", ghi_chu=o.ghi_chu, sua_o_ban=ban, dong_luc=int(time.time()))
            nen_loi.ghi_json(nen_loi.tep("phan_hoi", m["id"], "meta.json"), m)
            if m.get("luat") and not [x for x in nen_loi.ds_phan_hoi() if x.get("luat") == m["luat"]]:
                if nen_loi.bat_bo_loc(m["luat"]):
                    print("Đã bật lại bộ lọc `%s`." % m["luat"])
        print("Đã đóng %d phản hồi, sửa ở bản %s." % (len(ds), ban))
        return 0
    print("Đã bật lại `%s`." % o.luat if nen_loi.bat_bo_loc(o.luat) else "`%s` không ở trạng thái tắt." % o.luat)
    return 0


if __name__ == "__main__":
    sys.exit(main())
