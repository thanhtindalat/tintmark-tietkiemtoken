#!/usr/bin/env python3
# Copyright (c) 2026 Tintmark. All rights reserved. Xem LICENSE / NOTICE.
"""Cập nhật plugin có kiểm, sao lưu và quay lui (khung plugin bản quyền Tintmark). Chỉ dùng kênh CỤC BỘ.

  cap_nhat.py kiem                 so bản đang cài với bản mới nhất của kênh
  cap_nhat.py ap-dung [--ban X]    kiểm băm -> chạy test của bản mới -> sao lưu -> cài bản sao thật -> thử khói
  cap_nhat.py quay-lui             về bản ngay trước lần cập nhật gần nhất
  cap_nhat.py tu-dong              hook gọi nền mỗi 24 giờ; làm theo cấu hình tu_dong: ap_dung | bao | tat
  cap_nhat.py lich-su
  cap_nhat.py thu-khoi [thư mục]   thử khói một thư mục plugin (mặc định thư mục cài) với dữ liệu TẠM;
                                   dùng thay cho gọi tay hook của bản cài (gọi tay ghi vào sổ thống kê thật)

Cấu hình: <dữ liệu>/cap_nhat.json {"kenh": ".../kenh.json", "lien_ket": "<thư mục cài trong marketplace>", "tu_dong": "bao"}
"lien_ket" là tên cũ của thư mục cài: từ khung 0.1.0 đây là BẢN SAO THẬT (không còn liên kết tượng trưng);
gặp liên kết cũ thì lần cập nhật kế thay bằng bản sao. Thư mục thật của plugin khác => từ chối ghi đè.
Bản mới test hỏng / sai băm / thử khói hỏng => KHÔNG ghi đè, giữ bản cũ, báo qua hàng thông báo.
Thử khói và biến môi trường của test đọc từ `.claude-plugin/khung.json` của bản đang kiểm.
Kênh từ xa (http…) chưa bật.
"""
import hashlib
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import khung_chung as kc  # noqa: E402

BO_QUA = ("__pycache__", ".DS_Store")


def bam_cay(goc):
    h = hashlib.sha256()
    for thu_muc, con, tep in os.walk(goc):
        con[:] = sorted(c for c in con if c not in BO_QUA)
        for t in sorted(tep):
            if t in BO_QUA or t.endswith(".pyc"):
                continue
            duong = os.path.join(thu_muc, t)
            h.update(os.path.relpath(duong, goc).encode("utf-8") + b"\0")
            with open(duong, "rb") as f:
                h.update(hashlib.sha256(f.read()).digest())
    return h.hexdigest()


def so(v):
    try:
        return tuple(int(x) for x in str(v).split("."))
    except ValueError:
        return (0,)


def cau_hinh():
    c = kc.doc_json(kc.tep("cap_nhat.json"), {}) or {}
    c.setdefault("tu_dong", "bao")
    c.setdefault("lich_su", [])
    return c


def ban_dang_cai(c):
    """(bản, thư mục nguồn của bản đó trong kho). Cài bằng bản sao thì nguồn là `dang_cai_tu` đã ghi."""
    lk = c.get("lien_ket") or ""
    if not lk:
        return kc.phien_ban(), kc.GOC
    d = os.path.realpath(lk)
    ban = (kc.doc_json(os.path.join(d, ".claude-plugin", "plugin.json"), {}) or {}).get("version", "?")
    if not os.path.islink(lk) and c.get("dang_cai_tu") and os.path.isdir(c["dang_cai_tu"]):
        d = c["dang_cai_tu"]
    return ban, d


def doc_kenh(c):
    k = c.get("kenh") or ""
    if not k:
        raise RuntimeError("chưa cấu hình kênh (chạy cai_dat.py gop)")
    if k.startswith(("http://", "https://")):
        raise RuntimeError("kênh từ xa chưa bật: bản này chỉ nhận kênh cục bộ")
    d = kc.doc_json(k)
    if not isinstance(d, dict) or "ban" not in d:
        raise RuntimeError("không đọc được kênh %s" % k)
    return d, os.path.dirname(os.path.abspath(k))


def _env_tam(thu_muc, tam, tach=True):
    t = kc.khung(thu_muc).get("test") or {}
    env = dict(os.environ)
    for b in t.get("bien_tam") or []:
        env[b] = os.path.join(tam, b.lower()) if tach else tam
    for b in t.get("bo_bien") or []:
        env.pop(b, None)
    return env


def chay_test(thu_muc):
    tam = tempfile.mkdtemp()
    env = _env_tam(thu_muc, tam)
    try:
        r = subprocess.run([sys.executable, "-W", "ignore", "-m", "unittest", "discover", "-s",
                            os.path.join(thu_muc, "tests")], capture_output=True, env=env, timeout=300, cwd=thu_muc)
        duoi = (r.stderr or r.stdout).decode("utf-8", "replace").strip().splitlines()[-3:]
        return r.returncode == 0, " / ".join(duoi)
    except Exception as e:
        return False, "không chạy được test: %s" % e
    finally:
        shutil.rmtree(tam, ignore_errors=True)


def thu_khoi(thu_muc):
    """Các hook ghi trong khung.json "thu_khoi" phải chạy với dữ liệu mẫu, thoát 0, không in stderr.
    "thu_khoi": {"dau_vao": {...}, "lap": {"đường.tới.chuỗi": số lần}, "kich": [{"tep"|"mau": ..., "phai_in": ...}]}"""
    tk = kc.khung(thu_muc).get("thu_khoi") or {}
    tam = tempfile.mkdtemp()
    env = _env_tam(thu_muc, tam, tach=False)
    vao = json.loads(json.dumps(tk.get("dau_vao") or {}))
    for duong, lan in (tk.get("lap") or {}).items():   # {"tool_response.stdout": 2000}: nhân chuỗi lên cho đủ dài
        cha, khoa = vao, duong.split(".")
        for k in khoa[:-1]:
            cha = cha[k]
        cha[khoa[-1]] = cha[khoa[-1]] * int(lan)
    mau = json.dumps(vao)
    try:
        for muc in tk.get("kich") or []:
            if muc.get("mau"):
                tim = sorted(glob.glob(os.path.join(thu_muc, muc["mau"])))
                if not tim:
                    return False, "thiếu %s" % muc["mau"]
                kich = tim[0]
            else:
                kich = os.path.join(thu_muc, muc.get("tep") or "")
            ten_kich = os.path.relpath(kich, thu_muc)
            r = subprocess.run([sys.executable, kich], input=mau.encode(), capture_output=True, env=env, timeout=20)
            if r.returncode != 0 or r.stderr.strip():
                return False, "%s: mã %d %s" % (ten_kich, r.returncode, r.stderr.decode("utf-8", "replace")[:200])
            if muc.get("phai_in") and muc["phai_in"] not in r.stdout.decode("utf-8", "replace"):
                return False, "%s không in %s" % (ten_kich, muc["phai_in"])
        return True, "ok"
    except Exception as e:
        return False, str(e)
    finally:
        shutil.rmtree(tam, ignore_errors=True)


def dat_ban(dich_cai, nguon):
    """Cài BẢN SAO THẬT của `nguon` vào `dich_cai` (thay liên kết cũ nếu có). Chép xong mới tráo."""
    if os.path.isdir(dich_cai) and not os.path.islink(dich_cai):
        ten_cu = kc.plugin_json(dich_cai).get("name")
        if ten_cu not in (kc.ten(), kc.ten(nguon)):
            raise RuntimeError("%s là thư mục thật của plugin khác (%s): không ghi đè" % (dich_cai, ten_cu))
    os.makedirs(os.path.dirname(os.path.abspath(dich_cai)), exist_ok=True)
    moi = "%s.moi%d" % (dich_cai, os.getpid())
    cu = "%s.cu%d" % (dich_cai, os.getpid())
    for x in (moi, cu):
        if os.path.lexists(x):
            shutil.rmtree(x) if os.path.isdir(x) and not os.path.islink(x) else os.remove(x)
    shutil.copytree(os.path.realpath(nguon), moi, ignore=shutil.ignore_patterns("__pycache__", ".DS_Store", "*.pyc"))
    if os.path.lexists(dich_cai):
        os.rename(dich_cai, cu)
    os.rename(moi, dich_cai)
    if os.path.lexists(cu):
        shutil.rmtree(cu, ignore_errors=True) if os.path.isdir(cu) and not os.path.islink(cu) else os.remove(cu)


def nhat_ky(viec, **kw):
    try:
        os.makedirs(kc.thu_muc_du_lieu(), exist_ok=True)
        with open(kc.tep("cap_nhat_nhat_ky.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(dict(kw, viec=viec, luc=int(time.time())), ensure_ascii=False) + "\n")
    except Exception:
        pass


def ap_dung(ban=None, im=False):
    c = cau_hinh()
    kenh, goc_kenh = doc_kenh(c)
    hien, thu_muc_hien = ban_dang_cai(c)
    dich = ban or kenh.get("ban_moi_nhat")
    if not ban and so(dich) <= so(hien):
        return True, "đang ở bản mới nhất (%s)" % hien
    tt = (kenh.get("ban") or {}).get(dich)
    if not tt:
        return False, "kênh không có bản %s" % dich
    thu_muc = os.path.join(goc_kenh, tt.get("duong") or dich)
    if not os.path.isdir(thu_muc):
        return False, "thiếu thư mục bản %s" % dich
    if bam_cay(thu_muc) != tt.get("sha256"):
        nhat_ky("tu-choi", ban=dich, ly_do="sai băm")
        return False, "bản %s SAI BĂM so với kênh: không cập nhật" % dich
    dat, tin = chay_test(thu_muc)
    if not dat:
        nhat_ky("tu-choi", ban=dich, ly_do="test hỏng", chi_tiet=tin)
        return False, "bản %s TEST HỎNG (%s): giữ bản %s" % (dich, tin, hien)
    lk = c.get("lien_ket")
    if not lk:
        return False, "chưa cấu hình lien_ket"
    sl = kc.tep("sao_luu")
    os.makedirs(sl, exist_ok=True)
    st = os.path.expanduser("~/.claude/settings.json")
    bien = (kc.khung().get("du_lieu") or {}).get("bien")
    if os.path.isfile(st) and not (bien and os.environ.get(bien)):
        shutil.copy2(st, os.path.join(sl, "settings.json.truoc-%s-%s" % (dich, time.strftime("%y%m%d-%H%M%S"))))
    dat_ban(lk, thu_muc)
    dat, tin = thu_khoi(lk)
    if not dat:
        dat_ban(lk, thu_muc_hien)
        nhat_ky("tu-quay-lui", ban=dich, ly_do=tin)
        return False, "bản %s thử khói hỏng (%s): ĐÃ TỰ QUAY LUI về %s" % (dich, tin, hien)
    c = cau_hinh()
    c["lich_su"] = (c["lich_su"] + [{"tu": hien, "tu_duong": thu_muc_hien, "den": dich, "luc": int(time.time())}])[-20:]
    c["dang_cai_tu"] = os.path.realpath(thu_muc)
    kc.ghi_json(kc.tep("cap_nhat.json"), c)
    nhat_ky("cap-nhat", tu=hien, den=dich)
    return True, "đã cập nhật %s -> %s (%s). Phiên đang mở nhận hook mới khi mở lại hoặc /reload-plugins. " \
                 "Quay lui: python3 %s quay-lui" % (hien, dich, tt.get("ghi_chu") or "", os.path.join(lk, "scripts", "cap_nhat.py"))


def quay_lui():
    c = cau_hinh()
    if not c["lich_su"]:
        return False, "không có lần cập nhật nào để quay lui"
    cuoi = c["lich_su"][-1]
    hien, thu_muc_hien = ban_dang_cai(c)
    if not os.path.isdir(cuoi["tu_duong"]):
        return False, "bản cũ %s không còn ở %s" % (cuoi["tu"], cuoi["tu_duong"])
    dat_ban(c["lien_ket"], cuoi["tu_duong"])
    dat, tin = thu_khoi(c["lien_ket"])
    if not dat:
        dat_ban(c["lien_ket"], thu_muc_hien)
        return False, "bản cũ %s thử khói hỏng (%s): giữ %s" % (cuoi["tu"], tin, hien)
    c["lich_su"] = c["lich_su"][:-1]
    c["khong_tu_len"] = hien   # không tự cập nhật lại đúng bản vừa bị quay lui
    c["dang_cai_tu"] = os.path.realpath(cuoi["tu_duong"])
    kc.ghi_json(kc.tep("cap_nhat.json"), c)
    nhat_ky("quay-lui", tu=hien, den=cuoi["tu"])
    return True, "đã quay lui %s -> %s" % (hien, cuoi["tu"])


def main(argv=None):
    a = (argv if argv is not None else sys.argv[1:]) or ["kiem"]
    try:
        if a[0] == "kiem":
            c = cau_hinh(); kenh, _ = doc_kenh(c); hien, _ = ban_dang_cai(c)
            moi = kenh.get("ban_moi_nhat")
            print("Đang cài: %s · Mới nhất trên kênh: %s · %s" % (hien, moi, "CÓ BẢN MỚI" if so(moi) > so(hien) else "đã mới nhất"))
            return 0
        if a[0] == "ap-dung":
            dat, tin = ap_dung(a[a.index("--ban") + 1] if "--ban" in a else None)
            print(tin); return 0 if dat else 1
        if a[0] == "quay-lui":
            dat, tin = quay_lui(); print(tin); return 0 if dat else 1
        if a[0] == "lich-su":
            for m in cau_hinh()["lich_su"]:
                print("%s  %s -> %s" % (time.strftime("%d/%m/%Y %H:%M", time.localtime(m["luc"])), m["tu"], m["den"]))
            return 0
        if a[0] == "tu-dong":
            c = cau_hinh()
            if c["tu_dong"] == "tat":
                return 0
            kenh, _ = doc_kenh(c); hien, _ = ban_dang_cai(c); moi = kenh.get("ban_moi_nhat")
            if so(moi) <= so(hien) or moi == c.get("khong_tu_len"):
                return 0
            if c["tu_dong"] == "ap_dung":
                dat, tin = ap_dung()
                kc.them_thong_bao(tin)
            else:
                kc.them_thong_bao("có bản %s (đang %s): python3 <plugin>/scripts/cap_nhat.py ap-dung" % (moi, hien))
            return 0
        if a[0] == "thu-khoi":
            tm = a[1] if len(a) > 1 else cau_hinh().get("lien_ket")
            if not tm or not os.path.isdir(tm):
                print("Lỗi: không thấy thư mục plugin %s" % tm); return 1
            dat, tin = thu_khoi(tm); print(tin); return 0 if dat else 1
        print(__doc__); return 2
    except Exception as e:
        if a[0] == "tu-dong":
            nhat_ky("loi", chi_tiet=str(e)); return 0
        print("Lỗi: %s" % e); return 1


if __name__ == "__main__":
    sys.exit(main())
