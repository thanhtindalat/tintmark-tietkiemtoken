# Copyright (c) 2026 Tintmark. All rights reserved. Xem LICENSE / NOTICE.
"""Lõi nén output lệnh — Python 3 thư viện chuẩn. Mã riêng, không dùng mã rtk.

Luồng: loại ANSI -> sửa dòng (replace) -> bỏ dòng (drop, trừ dòng 'keep') ->
gộp dòng trùng -> cắt dòng dài -> giới hạn số dòng (đầu + dòng quan trọng + cuối).
Mọi lỗi ở đây phải được người gọi bắt và quay về output gốc.
"""
import json
import os
import re
import time

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LUAT_MAC_DINH = os.path.join(GOC, "luat", "luat.json")


TEN_DU_LIEU = "plugin-tintmark-tietkiemtoken"
TEN_DU_LIEU_CU = ("plugin-tintmark-tietkiem", "plugin-nen-token")   # các tên trước khi đổi tên plugin (15/11/2026)


def thu_muc_du_lieu():
    """Thư mục dữ liệu máy. Chưa chuyển dữ liệu thì đọc tiếp thư mục tên cũ, không mất thống kê / phản hồi / sao lưu."""
    if os.environ.get("NEN_DATA_DIR"):
        return os.environ["NEN_DATA_DIR"]
    nha = os.path.join(os.path.expanduser("~"), ".claude")
    moi = os.path.join(nha, TEN_DU_LIEU)
    if not os.path.exists(moi):
        for ten in TEN_DU_LIEU_CU:
            cu = os.path.join(nha, ten)
            if os.path.isdir(cu):
                return cu
    return moi


ANSI = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)|\x1b[()][A-Za-z0-9]")
SO = re.compile(r"\d+")


def tai_luat():
    """Luật riêng của người dùng (nếu có) đứng trước luật mặc định."""
    duong = []
    if os.environ.get("NEN_LUAT"):
        duong.append(os.environ["NEN_LUAT"])
    else:
        duong.append(os.path.join(thu_muc_du_lieu(), "luat_rieng.json"))
        duong.append(LUAT_MAC_DINH)
    ds = []
    for p in duong:
        if not os.path.isfile(p):
            continue
        try:
            with open(p, encoding="utf-8") as f:
                ds.extend(json.load(f).get("luat", []))
        except Exception:
            continue  # tệp luật hỏng thì bỏ qua tệp đó, không chặn việc
    return ds


def tim_luat(lenh, ds=None, tat=None):
    """Luật đầu tiên khớp. Luật đó đang bị tắt (tat_bo_loc.json) thì trả None = output gốc,
    KHÔNG rơi xuống luật chung hơn phía sau."""
    ds = tai_luat() if ds is None else ds
    for r in ds:
        try:
            if not re.search(r["match"], lenh):
                continue
            if r.get("exclude") and re.search(r["exclude"], lenh):
                continue
            if r.get("id") in (bo_loc_tat() if tat is None else tat):
                return None
            return r
        except Exception:
            continue
    return None


# ---------- dữ liệu dùng chung (cấu hình, bộ lọc tắt, thông báo, output gần đây) ----------
CAU_HINH_MAC_DINH = {
    "che_do": "sau",          # "sau" = nén ở PostToolUse (không đổi lệnh); "truoc" = bọc lệnh ở PreToolUse; "tat"
    "luu_gan_day": True,      # giữ output gốc của vài lệnh vừa nén để tái hiện khi bị nghi hỏng
    "so_gan_day": 8,
    "gan_day_toi_da_byte": 400000,
    "cua_so_nghi_phut": 15,   # chạy lại cùng lệnh với NEN_OFF=1 trong ngần này phút = dấu hiệu nghi hỏng
    "nguong_nghi": 3,         # số dấu hiệu nghi (tự ghi) trong 7 ngày để tự tắt một bộ lọc
    "nguong_bao": 2,          # số phản hồi do người / phiên báo để tự tắt một bộ lọc
}


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


def tep(*ten):
    return os.path.join(thu_muc_du_lieu(), *ten)


def cau_hinh():
    c = dict(CAU_HINH_MAC_DINH)
    d = doc_json(tep("cau_hinh.json"), {})
    if isinstance(d, dict):
        c.update({k: v for k, v in d.items() if k in c})
    if os.environ.get("NEN_CHE_DO"):
        c["che_do"] = os.environ["NEN_CHE_DO"]
    return c


def bo_loc_tat():
    d = doc_json(tep("tat_bo_loc.json"), {})
    return set(d) if isinstance(d, dict) else set()


def tat_bo_loc(luat_id, ly_do, phan_hoi=()):
    d = doc_json(tep("tat_bo_loc.json"), {})
    d = d if isinstance(d, dict) else {}
    if luat_id in d:
        return False
    d[luat_id] = {"luc": int(time.time()), "ly_do": ly_do, "phan_hoi": list(phan_hoi)}
    ghi_json(tep("tat_bo_loc.json"), d)
    them_thong_bao("bộ lọc nén `%s` đã TỰ TẮT (%s); lệnh loại này giờ trả output gốc. "
                   "Sửa: skill tintmark-tietkiemtoken, tệp tu-sua.md (scripts/tu_sua.py quet)." % (luat_id, ly_do))
    return True


def bat_bo_loc(luat_id):
    d = doc_json(tep("tat_bo_loc.json"), {})
    if isinstance(d, dict) and luat_id in d:
        del d[luat_id]
        ghi_json(tep("tat_bo_loc.json"), d)
        return True
    return False


def them_thong_bao(tin):
    """Hàng chờ thông báo một dòng; hook ngưỡng (UserPromptSubmit) in ra một lần rồi xoá."""
    try:
        ds = doc_json(tep("thong_bao.json"), [])
        ds = ds if isinstance(ds, list) else []
        if tin not in ds:
            ds.append(tin)
            ghi_json(tep("thong_bao.json"), ds[-10:])
    except Exception:
        pass


def khoa_lenh(lenh):
    import hashlib
    return hashlib.sha1(" ".join(lenh.split()).encode("utf-8", "replace")).hexdigest()[:12]


def luu_gan_day(lenh, luat_id, goc, ma=0, phien=""):
    """Giữ output gốc của lệnh vừa nén (vòng xoay nhỏ, chỉ trên máy, quyền 600)."""
    try:
        c = cau_hinh()
        if not c["luu_gan_day"] or len(goc) > c["gan_day_toi_da_byte"]:
            return
        d = tep("gan_day")
        os.makedirs(d, exist_ok=True)
        k = khoa_lenh(lenh)
        with open(os.open(os.path.join(d, k + ".txt"), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "w",
                  encoding="utf-8") as f:
            f.write(goc)
        cm = [m for m in (doc_json(os.path.join(d, "chi_muc.json"), []) or []) if m.get("khoa") != k]
        cm.append({"khoa": k, "luat": luat_id, "ts": int(time.time()), "ma": ma, "lenh": lenh, "phien": phien})
        for m in cm[:-int(c["so_gan_day"])]:
            try:
                os.remove(os.path.join(d, m["khoa"] + ".txt"))
            except OSError:
                pass
        ghi_json(os.path.join(d, "chi_muc.json"), cm[-int(c["so_gan_day"]):])
        os.chmod(os.path.join(d, "chi_muc.json"), 0o600)
    except Exception:
        pass


def tim_gan_day(lenh):
    try:
        c = cau_hinh()
        k = khoa_lenh(lenh)
        for m in doc_json(tep("gan_day", "chi_muc.json"), []) or []:
            if m.get("khoa") == k and time.time() - m.get("ts", 0) <= c["cua_so_nghi_phut"] * 60:
                return m
    except Exception:
        pass
    return None


def ghi_phan_hoi(loai, lenh, luat_id="", mo_ta="", goc=None, nen_=None, ma=0, nguon="nguoi", phien=""):
    """Ghi một phản hồi vào sổ cục bộ <dữ liệu>/phan_hoi/<id>/ rồi xét tự tắt bộ lọc. Trả id."""
    ma_ph = "PH-%s-%s" % (time.strftime("%y%m%d-%H%M%S"), khoa_lenh(lenh + str(time.time()))[:4])
    d = tep("phan_hoi", ma_ph)
    os.makedirs(d, mode=0o700, exist_ok=True)
    for ten, nd in (("goc.txt", goc), ("nen.txt", nen_)):
        if nd is not None:
            with open(os.open(os.path.join(d, ten), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "w",
                      encoding="utf-8") as f:
                f.write(nd[:2000000])
    ghi_json(os.path.join(d, "meta.json"), {
        "id": ma_ph, "loai": loai, "lenh": lenh, "luat": luat_id, "mo_ta": mo_ta, "ma": ma, "nguon": nguon,
        "phien": phien, "luc": int(time.time()), "trang_thai": "mo", "ban": phien_ban()})
    try:
        xet_tu_tat(luat_id)
    except Exception:
        pass
    return ma_ph


def ds_phan_hoi(chi_mo=True):
    kq = []
    goc = tep("phan_hoi")
    if os.path.isdir(goc):
        for ten in sorted(os.listdir(goc)):
            m = doc_json(os.path.join(goc, ten, "meta.json"))
            if isinstance(m, dict) and (not chi_mo or m.get("trang_thai") == "mo"):
                kq.append(m)
    return kq


def xet_tu_tat(luat_id):
    """Bộ lọc bị báo hỏng lặp lại (trong 7 ngày) thì tự tắt riêng bộ lọc đó."""
    if not luat_id or luat_id in bo_loc_tat():
        return False
    c = cau_hinh()
    moc = time.time() - 7 * 86400
    ds = [m for m in ds_phan_hoi() if m.get("luat") == luat_id and m.get("luc", 0) >= moc
          and m.get("loai") != "nhac-sai"]
    nghi = [m for m in ds if m.get("nguon") == "tu-dong"]
    bao = [m for m in ds if m.get("nguon") != "tu-dong"]
    if len(bao) >= c["nguong_bao"] or len(nghi) >= c["nguong_nghi"]:
        return tat_bo_loc(luat_id, "%d phản hồi, %d dấu hiệu nghi hỏng trong 7 ngày" % (len(bao), len(nghi)),
                          [m["id"] for m in ds])
    return False


def phien_ban():
    try:
        return doc_json(os.path.join(GOC, ".claude-plugin", "plugin.json"), {}).get("version", "?")
    except Exception:
        return "?"


def _bo_cr(text):
    out = []
    for dong in text.replace("\r\n", "\n").split("\n"):
        if "\r" in dong:
            doan = [d for d in dong.split("\r") if d.strip()]
            dong = doan[-1] if doan else ""
        out.append(dong)
    return out


def _any(patterns, s):
    return any(p.search(s) for p in patterns)


def nen(text, luat, ma_thoat=0):
    """Trả về chuỗi đã nén (có thể bằng gốc)."""
    bien = lambda ds: [re.compile(x) for x in luat.get(ds, [])]
    dong = _bo_cr(ANSI.sub("", text) if luat.get("strip_ansi", True) else text)
    for pat, rep in luat.get("replace", []):
        pat = re.compile(pat)
        dong = [pat.sub(rep, d) for d in dong]
    giu, bo = bien("keep"), bien("drop")
    dong = [d.rstrip() for d in dong]
    if bo:
        dong = [d for d in dong if (not _any(bo, d)) or _any(giu, d)]
    # gộp dòng trống liên tiếp
    kq = []
    for d in dong:
        if d == "" and (not kq or kq[-1] == ""):
            continue
        kq.append(d)
    while kq and kq[-1] == "":
        kq.pop()
    dong = kq

    che_do = luat.get("dedupe", "none")
    khoa = (lambda d: SO.sub("#", d)) if luat.get("mask") else (lambda d: d)
    if che_do == "consecutive":
        kq, i = [], 0
        while i < len(dong):
            j = i
            while j + 1 < len(dong) and khoa(dong[j + 1]) == khoa(dong[i]) and dong[i].strip():
                j += 1
            kq.append(dong[i] + ("  (+%d dòng tương tự)" % (j - i) if j > i else ""))
            i = j + 1
        dong = kq
    elif che_do == "all":
        dem, thu_tu = {}, []
        for d in dong:
            k = khoa(d)
            if not d.strip():
                thu_tu.append((None, d))
                continue
            if k not in dem:
                dem[k] = 0
                thu_tu.append((k, d))
            dem[k] += 1
        dong = [d + ("  (x%d)" % dem[k] if k is not None and dem[k] > 1 else "") for k, d in thu_tu]

    tt = luat.get("max_line_len")
    if tt:
        dong = [d if len(d) <= tt else d[: tt - 1] + "…" for d in dong]

    toi_da = luat.get("max_lines_fail" if ma_thoat else "max_lines", luat.get("max_lines"))
    if toi_da and len(dong) > toi_da:
        cuoi = toi_da // 2
        dau = toi_da - cuoi
        giua = dong[dau: len(dong) - cuoi]
        quan_trong = [d for d in giua if _any(giu, d)][: max(10, toi_da // 3)]
        bo_di = len(giua) - len(quan_trong)
        dong = dong[:dau] + quan_trong + ["… [nén: bỏ %d dòng — chạy lại với NEN_OFF=1 để xem đủ]" % bo_di] + dong[len(dong) - cuoi:]

    if not dong and luat.get("on_empty"):
        return luat["on_empty"] + "\n"
    return "\n".join(dong) + ("\n" if dong else "")


def nen_an_toan(text, luat, ma_thoat=0):
    """Nén; nếu lỗi / không nhỏ hơn / quá ngắn thì trả bản gốc."""
    try:
        if len(text.encode("utf-8", "replace")) < luat.get("min_bytes", 600):
            return text
        kq = nen(text, luat, ma_thoat)
        if len(kq.encode("utf-8", "replace")) >= len(text.encode("utf-8", "replace")):
            return text
        return kq
    except Exception:
        return text


def ghi_thong_ke(luat_id, lenh, vao, ra, ma_thoat, ms):
    try:
        d = thu_muc_du_lieu()
        os.makedirs(d, exist_ok=True)
        # chỉ lưu 2 từ đầu của lệnh để không lộ tham số / bí mật
        ngan = " ".join(lenh.split()[:2])
        with open(os.path.join(d, "thong_ke.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": int(time.time()), "luat": luat_id, "lenh": ngan, "vao": vao,
                                "ra": ra, "ma": ma_thoat, "ms": ms}, ensure_ascii=False) + "\n")
    except Exception:
        pass
