#!/usr/bin/env python3
"""Cập nhật plugin tintmark-tietkiem có kiểm, sao lưu và quay lui. Chỉ dùng kênh CỤC BỘ (thư mục trên máy).

  cap_nhat.py kiem                 so bản đang cài với bản mới nhất của kênh
  cap_nhat.py ap-dung [--ban X]    kiểm băm -> chạy test của bản mới -> sao lưu -> đổi liên kết -> thử khói
  cap_nhat.py quay-lui             về bản ngay trước lần cập nhật gần nhất
  cap_nhat.py tu-dong              hook gọi nền mỗi 24 giờ; làm theo cấu hình tu_dong: ap_dung | bao | tat
  cap_nhat.py lich-su

Cấu hình: <dữ liệu>/cap_nhat.json {"kenh": ".../kenh.json", "lien_ket": "<liên kết cài đặt>", "tu_dong": "bao"}
Bản mới test hỏng / sai băm / thử khói hỏng => KHÔNG ghi đè, giữ bản cũ, báo qua hàng thông báo.
Kênh từ xa (http…) chưa bật trong bản này (xem kế hoạch triển khai, giai đoạn 3).
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nen_loi  # noqa: E402

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
    c = nen_loi.doc_json(nen_loi.tep("cap_nhat.json"), {}) or {}
    c.setdefault("tu_dong", "bao")
    c.setdefault("lich_su", [])
    return c


def ban_dang_cai(c):
    lk = c.get("lien_ket") or ""
    d = os.path.realpath(lk) if lk else nen_loi.GOC
    return (nen_loi.doc_json(os.path.join(d, ".claude-plugin", "plugin.json"), {}) or {}).get("version", "?"), d


def doc_kenh(c):
    k = c.get("kenh") or ""
    if not k:
        raise RuntimeError("chưa cấu hình kênh (chạy cai_dat.py gop)")
    if k.startswith(("http://", "https://")):
        raise RuntimeError("kênh từ xa chưa bật: bản này chỉ nhận kênh cục bộ")
    d = nen_loi.doc_json(k)
    if not isinstance(d, dict) or "ban" not in d:
        raise RuntimeError("không đọc được kênh %s" % k)
    return d, os.path.dirname(os.path.abspath(k))


def chay_test(thu_muc):
    tam = tempfile.mkdtemp()
    env = dict(os.environ, NEN_DATA_DIR=os.path.join(tam, "nen"), TINTMARK_TOKEN_DIR=os.path.join(tam, "tt"))
    env.pop("NEN_OFF", None); env.pop("NEN_LUAT", None)
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
    """Bản vừa đổi phải chạy được hai hook với dữ liệu mẫu và thoát 0."""
    tam = tempfile.mkdtemp()
    env = dict(os.environ, NEN_DATA_DIR=tam, TINTMARK_TOKEN_DIR=tam)
    mau = json.dumps({"tool_name": "Bash", "session_id": "khoi", "hook_event_name": "PostToolUse",
                      "tool_input": {"command": "find . -name x"},
                      "tool_response": {"stdout": "a\n" * 2000, "stderr": "", "interrupted": False, "isImage": False}})
    try:
        for kich in ("scripts/hook_sau.py", "scripts/hook.py", "skills/tintmark-token/cong_cu/nguong_token.py"):
            r = subprocess.run([sys.executable, os.path.join(thu_muc, kich)], input=mau.encode(), capture_output=True,
                               env=env, timeout=20)
            if r.returncode != 0 or r.stderr.strip():
                return False, "%s: mã %d %s" % (kich, r.returncode, r.stderr.decode("utf-8", "replace")[:200])
            if kich.endswith("hook_sau.py") and "updatedToolOutput" not in r.stdout.decode("utf-8", "replace"):
                return False, "hook_sau không nén mẫu"
        return True, "ok"
    except Exception as e:
        return False, str(e)
    finally:
        shutil.rmtree(tam, ignore_errors=True)


def doi_lien_ket(lien_ket, dich):
    if os.path.exists(lien_ket) and not os.path.islink(lien_ket):
        raise RuntimeError("%s không phải liên kết; không ghi đè thư mục thật" % lien_ket)
    tam = lien_ket + ".moi%d" % os.getpid()
    if os.path.lexists(tam):
        os.remove(tam)
    os.symlink(os.path.relpath(os.path.realpath(dich), os.path.realpath(os.path.dirname(lien_ket))), tam)
    os.replace(tam, lien_ket)


def nhat_ky(viec, **kw):
    try:
        with open(nen_loi.tep("cap_nhat_nhat_ky.jsonl"), "a", encoding="utf-8") as f:
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
    sl = nen_loi.tep("sao_luu")
    os.makedirs(sl, exist_ok=True)
    st = os.path.expanduser("~/.claude/settings.json")
    if os.path.isfile(st) and not os.environ.get("NEN_DATA_DIR"):
        shutil.copy2(st, os.path.join(sl, "settings.json.truoc-%s-%s" % (dich, time.strftime("%y%m%d-%H%M%S"))))
    doi_lien_ket(lk, thu_muc)
    dat, tin = thu_khoi(lk)
    if not dat:
        doi_lien_ket(lk, thu_muc_hien)
        nhat_ky("tu-quay-lui", ban=dich, ly_do=tin)
        return False, "bản %s thử khói hỏng (%s): ĐÃ TỰ QUAY LUI về %s" % (dich, tin, hien)
    c = cau_hinh()
    c["lich_su"] = (c["lich_su"] + [{"tu": hien, "tu_duong": thu_muc_hien, "den": dich, "luc": int(time.time())}])[-20:]
    nen_loi.ghi_json(nen_loi.tep("cap_nhat.json"), c)
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
    doi_lien_ket(c["lien_ket"], cuoi["tu_duong"])
    dat, tin = thu_khoi(c["lien_ket"]) if os.path.isfile(os.path.join(cuoi["tu_duong"], "scripts", "hook_sau.py")) else (True, "")
    if not dat:
        doi_lien_ket(c["lien_ket"], thu_muc_hien)
        return False, "bản cũ %s thử khói hỏng (%s): giữ %s" % (cuoi["tu"], tin, hien)
    c["lich_su"] = c["lich_su"][:-1]
    c["khong_tu_len"] = hien   # không tự cập nhật lại đúng bản vừa bị quay lui
    nen_loi.ghi_json(nen_loi.tep("cap_nhat.json"), c)
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
                nen_loi.them_thong_bao(tin)
            else:
                nen_loi.them_thong_bao("có bản %s (đang %s): python3 <plugin>/scripts/cap_nhat.py ap-dung" % (moi, hien))
            return 0
        print(__doc__); return 2
    except Exception as e:
        if a[0] == "tu-dong":
            nhat_ky("loi", chi_tiet=str(e)); return 0
        print("Lỗi: %s" % e); return 1


if __name__ == "__main__":
    sys.exit(main())
