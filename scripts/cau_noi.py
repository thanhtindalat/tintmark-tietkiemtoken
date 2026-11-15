#!/usr/bin/env python3
# Copyright (c) 2026 Tintmark. All rights reserved. Xem LICENSE / NOTICE.
"""Cầu nối phê duyệt bằng giọng nói: phiên Claude Code <-> Claude Chat qua thư mục Google Drive đồng bộ trên máy.

Luồng: phiên Code tạo "tệp phê duyệt" .md trong <Drive>/dieu_phoi/<du_an>/ (đầu tệp có giao thức cho Chat)
-> người dùng mở Claude Chat (điện thoại), nói "đọc tệp phê duyệt <tên>" -> Chat hỏi từng câu bằng giọng
-> Chat TẠO TỆP MỚI ket_qua_<tên>_<YYYYMMDD-HHMM>.md cùng thư mục (connector Drive không ghi đè tệp có sẵn)
-> Drive đồng bộ về máy -> `canh` (chạy nền, 0 token khi chờ) thoát -> phiên tự thức, đọc kết quả, làm.
Phiên đã tắt lúc tệp về: hook đầu lượt (nguong_token.py, UserPromptSubmit) báo "có kết quả phê duyệt chưa đọc".

  cau_noi.py thu-muc                                   thư mục Drive đang dùng (hoặc lỗi + cách sửa)
  cau_noi.py tao --du-an X --ten Y --tu cau_hoi.md [--tieu-de "…"]   tạo tệp phê duyệt (--tu - : đọc stdin)
  cau_noi.py ban-sao --du-an X --tu tep_dieu_phoi.md [--ten Y]       bản sao chỉ đọc + giao thức nhận chỉ đạo
  cau_noi.py canh --ten Y [--du-an X] [--moi 30] [--het-gio 86400]   chờ tệp ket_qua mới; có thì in đường dẫn, thoát 0
  cau_noi.py chua-doc [--cwd THƯ_MỤC]                  liệt kê kết quả chưa đọc
  cau_noi.py da-doc <tệp ket_qua> | --ten Y [--du-an X]   đánh dấu đã đọc (đóng mục chờ)
  cau_noi.py ds                                        các mục đang chờ / đã xong

Thư mục Drive (sau thắng trước): ~/Library/CloudStorage/GoogleDrive-<tai_khoan>/<My Drive|Drive của tôi>
(tai_khoan bắt buộc đặt trong cau_hinh.json, không đoán) -> cau_hinh.json của plugin {"cau_noi": {"tai_khoan": "...", "drive": "<đường dẫn>"}} -> biến CAU_NOI_DRIVE.
Tài khoản phải TRÙNG tài khoản connector Google Drive của Claude, nếu không Chat không thấy tệp.
Không gọi mạng; chỉ đọc / ghi tệp trên máy.
"""
import argparse
import glob
import os
import re
import sys
import time
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import khung_chung as kc  # noqa: E402

THU_MUC_GOC = "dieu_phoi"
HAN_CHO_NGAY = 14          # mục chờ quá chừng này ngày thì hook thôi báo
NHAC_LAI_GIAY = 6 * 3600   # hook báo lại một kết quả chưa đọc tối đa 1 lần / 6 giờ
SO_CAU_TOM_TAT = 6

GIAO_THUC = """> **GIAO THỨC CHO CLAUDE** (Claude Chat / app điện thoại đọc tệp này qua Google Drive). Làm đúng từng bước, nói câu ngắn:
> 1. Nói một câu: có {n} câu cần quyết, mã `{ma}`. Rồi đọc **từng câu một**, kèm các lựa chọn (A, B…) và lựa chọn đề xuất nếu có. Chờ trả lời xong mới sang câu kế.
> 2. Người dùng nói "đọc lại" hoặc trả lời chưa rõ: đọc lại đúng câu đó và hỏi lại. Không tự đoán, không tự chọn thay.
> 3. Cứ **{k} câu** đã trả lời: tóm tắt {k} câu trả lời đó trong 1–2 câu, hỏi "đúng chưa", sửa nếu sai, rồi hỏi tiếp.
> 4. Người dùng nói thêm chỉ đạo mới (ngoài các câu hỏi): ghi nguyên ý vào mục "Chỉ đạo mới", xác nhận một câu, rồi quay lại câu đang dở.
> 5. Hết câu, hoặc người dùng nói "dừng" / "lưu": tóm tắt toàn bộ, hỏi xác nhận, rồi **tạo tệp MỚI** bằng công cụ Google Drive `create_file`: thư mục cha = thư mục chứa tệp này (`get_file_metadata` của tệp này → `parents`), tên `{ten_kq}`, `contentMimeType` = `text/markdown`, `disableConversionToGoogleType` = true, nội dung theo mẫu dưới. **Không sửa tệp này** (connector không ghi đè được). Câu chưa trả lời ghi vào "Chưa trả lời".
> 6. Báo một câu: "Đã lưu kết quả, phiên Claude Code sẽ tự đọc." Không tạo được tệp thì đọc nguyên văn nội dung tệp kết quả để người dùng chép lại.
>
> Mẫu tệp kết quả:
> ```
> # KẾT QUẢ: {ten}
> Mã: {ma}
> Lúc: <ngày giờ>
> ## Trả lời
> 1. <câu 1, ≤10 chữ> → <trả lời, giữ nguyên ý người dùng>
> ## Chỉ đạo mới
> - <nếu có>
> ## Chưa trả lời
> - <nếu có>
> ```
"""

GIAO_THUC_BAN_SAO = """> **GIAO THỨC CHO CLAUDE** — đây là **bản sao chỉ đọc** của tệp điều phối dự án `{du_an}` (chép lúc {luc}, mã `{ma}`). Nói câu ngắn:
> 1. Đọc tóm tắt từng mục (mỗi mục 1–2 câu), mục có việc chờ quyết đọc trước. Người dùng nói "đọc lại" / "chi tiết" thì đọc kỹ mục đó.
> 2. Người dùng ra chỉ đạo hay trả lời: ghi nguyên ý, xác nhận một câu. Cứ **{k} ý** đã ghi thì tóm tắt lại rồi đi tiếp.
> 3. Người dùng nói "dừng" / "lưu": tóm tắt, hỏi xác nhận, rồi **tạo tệp MỚI** bằng Google Drive `create_file` cùng thư mục với tệp này (`get_file_metadata` → `parents`), tên `{ten_kq}`, `contentMimeType` = `text/markdown`, `disableConversionToGoogleType` = true, theo mẫu: `# KẾT QUẢ: {ten}` / `Mã: {ma}` / `## Chỉ đạo mới` (mỗi ý một dòng, ghi rõ mục nào). **Không sửa tệp này.**
> 4. Báo một câu: "Đã lưu chỉ đạo, phiên Claude Code sẽ tự đọc."
"""


def khong_dau(s):
    s = unicodedata.normalize("NFD", s.replace("đ", "d").replace("Đ", "D"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s[:60] or "phe_duyet"


def cau_hinh():
    d = kc.doc_json(kc.tep("cau_hinh.json"), {}) or {}
    c = d.get("cau_noi") if isinstance(d, dict) else None
    return c if isinstance(c, dict) else {}


def tim_drive():
    """(đường dẫn thư mục gốc Drive, None) hoặc (None, lý do + cách sửa)."""
    bien = os.environ.get("CAU_NOI_DRIVE")
    if bien:
        return (bien, None) if os.path.isdir(bien) else (None, "CAU_NOI_DRIVE=%s không phải thư mục" % bien)
    c = cau_hinh()
    if c.get("drive"):
        p = os.path.expanduser(c["drive"])
        return (p, None) if os.path.isdir(p) else (None, "cau_noi.drive=%s không có trên máy" % p)
    tk = c.get("tai_khoan")
    goc = os.path.expanduser("~/Library/CloudStorage")
    co = sorted(os.path.basename(p) for p in glob.glob(os.path.join(goc, "GoogleDrive-*")))
    if not tk:
        return None, ("chưa đặt tài khoản Drive. Ghi {\"cau_noi\": {\"tai_khoan\": \"<email của connector Google Drive trong Claude>\"}} "
                      "vào %s (thư mục Drive trên máy đang có: %s)" % (kc.tep("cau_hinh.json"), ", ".join(co) or "không có"))
    p = os.path.join(goc, "GoogleDrive-" + tk)
    if os.path.isdir(p):
        for con in ("My Drive", "Drive của tôi", unicodedata.normalize("NFD", "Drive của tôi")):
            if os.path.isdir(os.path.join(p, con)):
                return os.path.join(p, con), None
        return None, "%s chưa có thư mục My Drive (app Google Drive chưa đồng bộ xong?)" % p
    return None, ("chưa có thư mục Google Drive của tài khoản %s trên máy (đang có: %s). Thêm tài khoản này vào app "
                  "Google Drive máy tính (cùng tài khoản connector Drive của Claude), hoặc đặt "
                  "{\"cau_noi\": {\"tai_khoan\": \"...\"}} / {\"cau_noi\": {\"drive\": \"<thư mục>\"}} trong %s"
                  % (tk, ", ".join(co) or "không có", kc.tep("cau_hinh.json")))


def so():
    d = kc.doc_json(kc.tep("cau_noi.json"), {}) or {}
    d = d if isinstance(d, dict) else {}
    d.setdefault("muc", {})
    d.setdefault("da_doc", [])
    d.setdefault("bao_luc", {})
    return d


def ghi_so(d):
    d["da_doc"] = d["da_doc"][-500:]
    kc.ghi_json(kc.tep("cau_noi.json"), d)


def khoa(du_an, ten):
    return "%s/%s" % (du_an, ten)


def dem_cau(noi_dung):
    return len(re.findall(r"^\s*(?:\d+[.)]|câu\s*\d+|#+\s*câu\s*\d+)", noi_dung, re.M | re.I))


def ten_ket_qua(ten):
    return "ket_qua_%s_<YYYYMMDD-HHMM>.md" % ten


def _ghi_tep(p, noi_dung):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tam = p + ".tam%d" % os.getpid()
    with open(tam, "w", encoding="utf-8") as f:
        f.write(noi_dung)
    os.replace(tam, p)


def _dang_ky(du_an, ten, thu_muc, tep, ma, loai, cwd):
    d = so()
    d["muc"][khoa(du_an, ten)] = {"du_an": du_an, "ten": ten, "thu_muc": thu_muc, "tep": tep, "ma": ma,
                                  "loai": loai, "luc": time.time(), "cwd": os.path.realpath(cwd or os.getcwd()),
                                  "trang_thai": "cho"}
    ghi_so(d)


def _doc_vao(tu):
    if tu == "-":
        return sys.stdin.read()
    with open(os.path.expanduser(tu), encoding="utf-8") as f:
        return f.read()


def tao(du_an, ten, noi_dung, tieu_de=None, cwd=None):
    """Tạo tệp phê duyệt; trả (đường dẫn, số câu). Ném RuntimeError nếu không có thư mục Drive."""
    goc, loi = tim_drive()
    if not goc:
        raise RuntimeError(loi)
    du_an, ten = khong_dau(du_an), khong_dau(ten)
    thu_muc = os.path.join(goc, THU_MUC_GOC, du_an)
    ma = "%s-%s" % (ten, time.strftime("%y%m%d%H%M"))
    n = dem_cau(noi_dung)
    dau = "# PHÊ DUYỆT: %s\n\n" % (tieu_de or ten.replace("_", " "))
    dau += GIAO_THUC.format(n=n or "một số", ma=ma, k=SO_CAU_TOM_TAT, ten=ten, ten_kq=ten_ket_qua(ten))
    dau += "\nDự án: `%s` · Tạo lúc: %s · Kết quả về: `%s`\n\n---\n\n## Câu hỏi\n\n" % (
        du_an, time.strftime("%d/%m/%Y %H:%M"), ten_ket_qua(ten))
    p = os.path.join(thu_muc, ten + ".md")
    _ghi_tep(p, dau + noi_dung.strip() + "\n")
    _dang_ky(du_an, ten, thu_muc, p, ma, "phe_duyet", cwd)
    return p, n


def ban_sao(du_an, tu, ten=None, cwd=None):
    goc, loi = tim_drive()
    if not goc:
        raise RuntimeError(loi)
    du_an = khong_dau(du_an)
    ten = khong_dau(ten or ("dieu_phoi_" + os.path.splitext(os.path.basename(tu))[0]))
    thu_muc = os.path.join(goc, THU_MUC_GOC, du_an)
    ma = "%s-%s" % (ten, time.strftime("%y%m%d%H%M"))
    dau = "# BẢN SAO CHỈ ĐỌC: %s\n\n" % os.path.basename(tu)
    dau += GIAO_THUC_BAN_SAO.format(du_an=du_an, luc=time.strftime("%d/%m/%Y %H:%M"), ma=ma, k=SO_CAU_TOM_TAT,
                                    ten=ten, ten_kq=ten_ket_qua(ten))
    p = os.path.join(thu_muc, ten + ".md")
    _ghi_tep(p, dau + "\n---\n\n" + _doc_vao(tu).strip() + "\n")
    _dang_ky(du_an, ten, thu_muc, p, ma, "ban_sao", cwd)
    return p


def ket_qua_cua(m, da_doc=()):
    """Tệp ket_qua_<ten>_* trong thư mục của mục m, ghi sau lúc tạo (trừ 2 phút lệch đồng hồ), chưa đọc."""
    ra = []
    try:
        ds = os.listdir(m["thu_muc"])
    except OSError:
        return ra
    tien_to = "ket_qua_%s_" % m["ten"]
    for t in sorted(ds):
        if not unicodedata.normalize("NFC", t).startswith(tien_to) or t.startswith("."):
            continue
        p = os.path.join(m["thu_muc"], t)
        try:
            if os.path.getmtime(p) < float(m.get("luc") or 0) - 120:
                continue
        except OSError:
            continue
        if p not in da_doc:
            ra.append(p)
    return ra


def chua_doc(cwd=None, moi_ngay=HAN_CHO_NGAY):
    """[(mục, [tệp])] các mục đang chờ có kết quả chưa đọc, thuộc dự án của cwd (None = mọi dự án)."""
    d = so()
    cwd = os.path.realpath(cwd) if cwd else None
    nay, ra = time.time(), []
    for m in d["muc"].values():
        if not isinstance(m, dict) or m.get("trang_thai") != "cho":
            continue
        if nay - float(m.get("luc") or 0) > moi_ngay * 86400:
            continue
        g = m.get("cwd") or ""
        if cwd and g and not (cwd == g or cwd.startswith(g + os.sep) or g.startswith(cwd + os.sep)):
            continue
        tep = ket_qua_cua(m, set(d["da_doc"]))
        if tep:
            ra.append((m, tep))
    return ra


def nhac_hook(cwd):
    """Dòng báo cho hook UserPromptSubmit, hoặc None. Mỗi tệp báo tối đa 1 lần / NHAC_LAI_GIAY."""
    ds = chua_doc(cwd)
    if not ds:
        return None
    d = so()
    nay, dong, doi = time.time(), [], False
    for m, tep in ds[:5]:
        moi = [p for p in tep if nay - float(d["bao_luc"].get(p) or 0) > NHAC_LAI_GIAY]
        if not moi:
            continue
        for p in moi:
            d["bao_luc"][p] = nay
        doi = True
        dong.append("%s (dự án %s): %s" % (m["ten"], m["du_an"], ", ".join(moi)))
    if not doi:
        return None
    d["bao_luc"] = {k: v for k, v in d["bao_luc"].items() if nay - v < 30 * 86400}
    ghi_so(d)
    return ("[tintmark-tietkiemtoken] CÓ KẾT QUẢ PHÊ DUYỆT chưa đọc: %s. Đọc tệp; ghi sổ hỏi đáp dự án TRƯỚC khi trả lời; "
            "làm việc được duyệt, chỉ đạo mới ghi sổ yêu cầu; xong chạy `cau_noi.py da-doc <tệp>`. "
            "Tệp .gdoc (bị đổi sang Google Docs) thì đọc bằng connector Drive. (Báo người dùng một dòng.)" % " | ".join(dong))


def canh(ten, du_an=None, moi=30, het_gio=86400):
    """Chờ (ngủ, không in gì) tới khi có tệp ket_qua mới cho mục `ten`. Trả mã thoát."""
    ten = khong_dau(ten)
    d = so()
    muc = [m for k, m in d["muc"].items() if m.get("ten") == ten and (not du_an or m.get("du_an") == khong_dau(du_an))]
    if not muc:
        print("Không có mục chờ tên %s. Tạo trước bằng `cau_noi.py tao`." % ten)
        return 2
    m = max(muc, key=lambda x: float(x.get("luc") or 0))
    het = time.time() + float(het_gio)
    while True:
        tep = ket_qua_cua(m, set(so()["da_doc"]))
        if tep:
            print("CÓ KẾT QUẢ PHÊ DUYỆT %s:\n%s\nĐọc tệp; ghi sổ hỏi đáp dự án trước khi trả lời; làm việc được duyệt; "
                  "xong chạy `cau_noi.py da-doc <tệp>`." % (ten, "\n".join(tep)))
            return 0
        if time.time() >= het:
            print("Hết giờ chờ (%d giây) chưa có kết quả cho %s. Hook đầu lượt sẽ báo khi tệp về." % (int(het_gio), ten))
            return 3
        time.sleep(max(1.0, min(float(moi), het - time.time())))


def da_doc(tep=None, ten=None, du_an=None):
    d = so()
    xong = []
    if tep:
        p = os.path.abspath(os.path.expanduser(tep))
        if p not in d["da_doc"]:
            d["da_doc"].append(p)
        for m in d["muc"].values():
            if os.path.dirname(p) == m.get("thu_muc") and os.path.basename(p).startswith("ket_qua_%s_" % m.get("ten")):
                m["trang_thai"], m["xong_luc"] = "xong", time.time()
                xong.append(m["ten"])
    if ten:
        ten = khong_dau(ten)
        for m in d["muc"].values():
            if m.get("ten") == ten and (not du_an or m.get("du_an") == khong_dau(du_an)):
                for p in ket_qua_cua(m, set(d["da_doc"])):
                    d["da_doc"].append(p)
                m["trang_thai"], m["xong_luc"] = "xong", time.time()
                xong.append(m["ten"])
    ghi_so(d)
    return xong


def main(argv=None):
    ap = argparse.ArgumentParser(prog="cau_noi.py", description="Cầu nối phê duyệt giọng nói qua Google Drive")
    sp = ap.add_subparsers(dest="lenh")
    sp.add_parser("thu-muc")
    a = sp.add_parser("tao")
    a.add_argument("--du-an", required=True); a.add_argument("--ten", required=True)
    a.add_argument("--tu", required=True); a.add_argument("--tieu-de"); a.add_argument("--cwd")
    a = sp.add_parser("ban-sao")
    a.add_argument("--du-an", required=True); a.add_argument("--tu", required=True)
    a.add_argument("--ten"); a.add_argument("--cwd")
    a = sp.add_parser("canh")
    a.add_argument("--ten", required=True); a.add_argument("--du-an")
    a.add_argument("--moi", type=float, default=30); a.add_argument("--het-gio", type=float, default=86400)
    a = sp.add_parser("chua-doc"); a.add_argument("--cwd")
    a = sp.add_parser("da-doc")
    a.add_argument("tep", nargs="?"); a.add_argument("--ten"); a.add_argument("--du-an")
    sp.add_parser("ds")
    x = ap.parse_args(argv)
    try:
        if x.lenh == "thu-muc":
            goc, loi = tim_drive()
            print(os.path.join(goc, THU_MUC_GOC) if goc else "LỖI: " + loi)
            return 0 if goc else 1
        if x.lenh == "tao":
            p, n = tao(x.du_an, x.ten, _doc_vao(x.tu), x.tieu_de, x.cwd)
            print("Đã tạo %s (%d câu). Người dùng nói với Claude Chat: \"đọc tệp phê duyệt %s\". "
                  "Chờ nền: cau_noi.py canh --ten %s" % (p, n, os.path.splitext(os.path.basename(p))[0],
                                                          os.path.splitext(os.path.basename(p))[0]))
            if not n:
                print("CẢNH BÁO: không thấy câu đánh số (\"1.\" hoặc \"Câu 1\"); Chat vẫn đọc được nhưng khó tóm tắt.")
            return 0
        if x.lenh == "ban-sao":
            p = ban_sao(x.du_an, x.tu, x.ten, x.cwd)
            print("Đã chép bản sao chỉ đọc: %s. Chờ nền: cau_noi.py canh --ten %s"
                  % (p, os.path.splitext(os.path.basename(p))[0]))
            return 0
        if x.lenh == "canh":
            return canh(x.ten, x.du_an, x.moi, x.het_gio)
        if x.lenh == "chua-doc":
            ds = chua_doc(x.cwd)
            for m, tep in ds:
                print("%s/%s: %s" % (m["du_an"], m["ten"], ", ".join(tep)))
            if not ds:
                print("Không có kết quả chưa đọc.")
            return 0
        if x.lenh == "da-doc":
            if not x.tep and not x.ten:
                print("Cần <tệp> hoặc --ten"); return 2
            xong = da_doc(x.tep, x.ten, x.du_an)
            print("Đã đánh dấu đọc%s." % (" (đóng: %s)" % ", ".join(xong) if xong else ""))
            return 0
        if x.lenh == "ds":
            for k, m in sorted(so()["muc"].items(), key=lambda kv: -float(kv[1].get("luc") or 0))[:30]:
                print("%-5s %-40s %s  %s" % (m.get("trang_thai"), k, time.strftime("%d/%m %H:%M", time.localtime(m.get("luc") or 0)), m.get("tep")))
            return 0
    except RuntimeError as e:
        print("LỖI: %s" % e)
        return 1
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
