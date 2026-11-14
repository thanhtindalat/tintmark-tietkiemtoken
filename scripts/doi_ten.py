#!/usr/bin/env python3
"""Chuyển máy từ plugin tên cũ `nen-token` sang `tintmark-tietkiem` (và quay lui). Python 3 thư viện chuẩn.

  doi_ten.py trang-thai --marketplace <thư mục marketplace cục bộ>
  doi_ten.py lam        --marketplace <…> --kho <kho_ban/tintmark-tietkiem> [--ban-cu <kho_ban/nen-token/0.2.7>]
  doi_ten.py quay-lui   --marketplace <…>

`lam`: (1) sao lưu settings.json + marketplace.json; (2) đổi tên thư mục dữ liệu ~/.claude/plugin-nen-token
thành ~/.claude/plugin-tintmark-tietkiem và để lại liên kết tên cũ trỏ sang (bản cũ vẫn đọc được);
(3) cap_nhat.json trỏ kênh / liên kết mới; (4) marketplace.json thêm mục tintmark-tietkiem (giữ mục cũ để quay lui);
(5) tạo liên kết <marketplace>/tintmark-tietkiem trỏ bản cũ (sau đó `cap_nhat.py ap-dung` đưa lên bản mới);
(6) ~/.claude/skills/tintmark-token trỏ skill trong liên kết mới. Bật / tắt plugin làm bằng `claude plugin` (in ra lệnh).
`quay-lui`: làm ngược lại, dữ liệu về tên cũ, không xoá gì.
"""
import argparse
import json
import os
import shutil
import sys
import time

NHA = os.environ.get("NEN_NHA") or os.path.expanduser("~/.claude")
MOI, CU = "tintmark-tietkiem", "nen-token"
DL_MOI, DL_CU = os.path.join(NHA, "plugin-" + MOI), os.path.join(NHA, "plugin-" + CU)


def doc(p, mac=None):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return mac


def ghi(p, d):
    tam = p + ".tam%d" % os.getpid()
    with open(tam, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.replace(tam, p)


def lien_ket(duong, dich, giai=True):
    """giai=True: liên kết tương đối tới đích thật; False: trỏ tuyệt đối đúng đường đưa vào (qua liên kết khác)."""
    if os.path.lexists(duong) and not os.path.islink(duong):
        raise RuntimeError("%s là thư mục thật, không ghi đè" % duong)
    tam = duong + ".moi%d" % os.getpid()
    os.symlink(os.path.relpath(os.path.realpath(dich), os.path.realpath(os.path.dirname(duong))) if giai else os.path.abspath(dich), tam)
    os.replace(tam, duong)


def thay_duong(d, cu, moi):
    s = json.dumps(d, ensure_ascii=False)
    return json.loads(s.replace(cu, moi))


def trang_thai(a):
    mk = a.marketplace
    print("Dữ liệu mới:", DL_MOI, "có" if os.path.isdir(DL_MOI) else "CHƯA có")
    print("Dữ liệu cũ :", DL_CU, ("liên kết -> " + os.readlink(DL_CU)) if os.path.islink(DL_CU) else ("thư mục thật" if os.path.isdir(DL_CU) else "không có"))
    for t in (MOI, CU):
        p = os.path.join(mk, t)
        print("Liên kết %-18s %s" % (t + ":", os.readlink(p) if os.path.islink(p) else "không có"))
    m = doc(os.path.join(mk, ".claude-plugin", "marketplace.json"), {}) or {}
    print("marketplace.json:", [x.get("name") for x in m.get("plugins", [])])
    st = doc(os.path.join(NHA, "settings.json"), {}) or {}
    ep = st.get("enabledPlugins", {})
    print("enabledPlugins:", {k: v for k, v in ep.items() if k.split("@")[0] in (MOI, CU)})
    sk = os.path.join(NHA, "skills", "tintmark-token")
    print("Skill tintmark-token ->", os.readlink(sk) if os.path.islink(sk) else ("thư mục thật" if os.path.isdir(sk) else "không có"))
    return 0


def lam(a):
    mk = os.path.abspath(a.marketplace)
    kho = os.path.abspath(a.kho)
    ban_cu = os.path.abspath(a.ban_cu) if a.ban_cu else os.path.realpath(os.path.join(mk, CU))
    if not os.path.isfile(os.path.join(kho, "kenh.json")):
        print("Thiếu %s/kenh.json: phát bản mới trước (phat_ban.py)" % kho); return 1
    luc = time.strftime("%y%m%d-%H%M%S")
    # 2. dữ liệu
    if os.path.isdir(DL_CU) and not os.path.islink(DL_CU) and not os.path.exists(DL_MOI):
        os.rename(DL_CU, DL_MOI)
        os.symlink(DL_MOI, DL_CU)
        print("Đã đổi tên dữ liệu:", DL_CU, "->", DL_MOI, "(để lại liên kết tên cũ)")
    os.makedirs(os.path.join(DL_MOI, "sao_luu"), exist_ok=True)
    sl = os.path.join(DL_MOI, "sao_luu")
    # 1. sao lưu
    st_tep = os.path.join(NHA, "settings.json")
    mf = os.path.join(mk, ".claude-plugin", "marketplace.json")
    if os.path.isfile(st_tep):
        shutil.copy2(st_tep, os.path.join(sl, "settings.json.truoc-doi-ten-" + luc))
    shutil.copy2(mf, os.path.join(sl, "marketplace.json.truoc-doi-ten-" + luc))
    # 3. cấu hình cập nhật + cài đặt
    lk_moi = os.path.join(mk, MOI)
    cn = os.path.join(DL_MOI, "cap_nhat.json")
    c = doc(cn, {}) or {}
    if "kenh_cu" not in c:   # chạy lại không ghi đè đường cũ
        c["kenh_cu"], c["lien_ket_cu"] = c.get("kenh", ""), c.get("lien_ket", "")
    c["kenh"], c["lien_ket"] = os.path.join(kho, "kenh.json"), lk_moi
    ghi(cn, thay_duong(c, DL_CU + "/", DL_MOI + "/"))
    cd = os.path.join(DL_MOI, "cai_dat.json")
    if os.path.isfile(cd):
        ghi(cd, thay_duong(doc(cd, {}), DL_CU + "/", DL_MOI + "/"))
    # 4. marketplace
    m = doc(mf, {})
    if not any(x.get("name") == MOI for x in m.get("plugins", [])):
        m.setdefault("plugins", []).append({"name": MOI, "source": "./" + MOI,
                                            "description": "Tiết kiệm token cho Claude Code: nén output lệnh bash, ngưỡng đổi phiên, đo token"})
        ghi(mf, m)
    # 5. liên kết cài đặt mới (trỏ bản cũ; ap-dung sẽ đưa lên bản mới)
    if not os.path.lexists(lk_moi):
        lien_ket(lk_moi, ban_cu)
    # 6. skill
    sk = os.path.join(NHA, "skills", "tintmark-token")
    if os.path.islink(sk) or not os.path.exists(sk):
        if os.path.isdir(os.path.join(lk_moi, "skills", "tintmark-token")):
            lien_ket(sk, os.path.join(lk_moi, "skills", "tintmark-token"), giai=False)
    ghi(os.path.join(DL_MOI, "doi_ten.json"), {"luc": int(time.time()), "settings_sao_luu": os.path.join(sl, "settings.json.truoc-doi-ten-" + luc),
                                               "marketplace_sao_luu": os.path.join(sl, "marketplace.json.truoc-doi-ten-" + luc)})
    print("Xong phần tệp. Tiếp theo:\n  python3 %s/scripts/cap_nhat.py ap-dung\n  claude plugin install %s@<marketplace>\n  claude plugin disable %s@<marketplace>"
          % (lk_moi, MOI, CU))
    return 0


def quay_lui(a):
    mk = os.path.abspath(a.marketplace)
    if os.path.islink(DL_CU) and os.path.isdir(DL_MOI):
        os.remove(DL_CU)
        os.rename(DL_MOI, DL_CU)
        print("Dữ liệu về tên cũ:", DL_CU)
    cn = os.path.join(DL_CU, "cap_nhat.json")
    c = doc(cn, {}) or {}
    if c.get("kenh_cu"):
        c["kenh"], c["lien_ket"] = c.pop("kenh_cu"), c.pop("lien_ket_cu")
        ghi(cn, thay_duong(c, DL_MOI + "/", DL_CU + "/"))
    cd = os.path.join(DL_CU, "cai_dat.json")
    if os.path.isfile(cd):
        ghi(cd, thay_duong(doc(cd, {}), DL_MOI + "/", DL_CU + "/"))
    sk = os.path.join(NHA, "skills", "tintmark-token")
    cu = os.path.join(mk, CU, "skills", "tintmark-token")
    if os.path.islink(sk) and os.path.isdir(cu):
        lien_ket(sk, cu, giai=False)
    print("Xong. Tiếp theo:\n  claude plugin disable %s@<marketplace>\n  claude plugin enable %s@<marketplace>" % (MOI, CU))
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("viec", choices=["trang-thai", "lam", "quay-lui"])
    p.add_argument("--marketplace", required=True)
    p.add_argument("--kho")
    p.add_argument("--ban-cu")
    a = p.parse_args(argv)
    if a.viec == "lam" and not a.kho:
        p.error("lam cần --kho")
    return {"trang-thai": trang_thai, "lam": lam, "quay-lui": quay_lui}[a.viec](a)


if __name__ == "__main__":
    sys.exit(main())
