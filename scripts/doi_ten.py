#!/usr/bin/env python3
"""Chuyển máy từ plugin tên cũ sang tên mới (và quay lui). Python 3 thư viện chuẩn.
Mặc định (15/11/2026, ): plugin `tintmark-tietkiem` -> `tintmark-tietkiemtoken`,
skill `tintmark-token` -> `tintmark-tietkiemtoken`. Lần trước: `--tu nen-token --sang tintmark-tietkiem
--skill-tu tintmark-token --skill-sang tintmark-token`.

  doi_ten.py trang-thai --marketplace <thư mục marketplace cục bộ> [--tu … --sang …]
  doi_ten.py lam        --marketplace <…> --kho <kho_ban/<tên mới>> [--ban-cu <bản đang cài>] [--tu … --sang …]
  doi_ten.py quay-lui   --marketplace <…> [--tu … --sang …]

`lam`: (1) sao lưu settings.json + marketplace.json; (2) đổi tên thư mục dữ liệu ~/.claude/plugin-<tu>
thành ~/.claude/plugin-<sang>, để lại liên kết tên cũ (các liên kết tên cũ hơn cũng trỏ lại); thư mục dữ liệu
skill ~/.claude/<skill-tu> -> ~/.claude/<skill-sang> tương tự; (3) cap_nhat.json trỏ kênh / liên kết mới;
(4) marketplace.json thêm mục <sang> (giữ mục cũ để quay lui); (5) tạo liên kết <marketplace>/<sang> trỏ bản cũ
(sau đó `cap_nhat.py ap-dung` đưa lên bản mới); (6) ~/.claude/skills/<skill-tu> (nếu là liên kết) đổi thành
~/.claude/skills/<skill-sang> trỏ skill trong liên kết mới. Bật / tắt plugin làm bằng `claude plugin` (in ra lệnh).
`quay-lui`: làm ngược lại, dữ liệu về tên cũ, không xoá gì.
"""
import argparse
import json
import os
import shutil
import sys
import time

NHA = os.environ.get("NEN_NHA") or os.path.expanduser("~/.claude")
MO_TA = "Tiết kiệm token cho Claude Code: nén output lệnh bash, ngưỡng đổi phiên, đo token"


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


def chuyen_thu_muc(cu, moi):
    """Đổi tên thư mục thật cu -> moi, để lại liên kết cu; liên kết khác trong cùng thư mục đang trỏ cu thì trỏ sang moi."""
    if not (os.path.isdir(cu) and not os.path.islink(cu) and not os.path.exists(moi)):
        return False
    me = os.path.dirname(cu)
    tro_cu = [os.path.join(me, t) for t in os.listdir(me)
              if os.path.islink(os.path.join(me, t)) and os.path.abspath(os.path.join(me, os.readlink(os.path.join(me, t)))) == os.path.abspath(cu)]
    os.rename(cu, moi)
    os.symlink(moi, cu)
    for l in tro_cu:
        os.remove(l)
        os.symlink(moi, l)
    print("Đã đổi tên:", cu, "->", moi, "(để lại liên kết tên cũ)")
    return True


def tra_thu_muc(cu, moi):
    """Ngược chuyen_thu_muc: moi về lại cu; các liên kết trỏ moi trỏ lại cu."""
    if not (os.path.islink(cu) and os.path.isdir(moi) and not os.path.islink(moi)):
        return False
    me = os.path.dirname(cu)
    os.remove(cu)
    tro_moi = [os.path.join(me, t) for t in os.listdir(me)
               if os.path.islink(os.path.join(me, t)) and os.path.abspath(os.path.join(me, os.readlink(os.path.join(me, t)))) == os.path.abspath(moi)]
    os.rename(moi, cu)
    for l in tro_moi:
        os.remove(l)
        os.symlink(cu, l)
    print("Về tên cũ:", cu)
    return True


def ten(a):
    dl_moi, dl_cu = os.path.join(NHA, "plugin-" + a.sang), os.path.join(NHA, "plugin-" + a.tu)
    sk_moi, sk_cu = os.path.join(NHA, a.skill_sang), os.path.join(NHA, a.skill_tu)
    return dl_moi, dl_cu, sk_moi, sk_cu


def trang_thai(a):
    mk = a.marketplace
    dl_moi, dl_cu, sk_moi, sk_cu = ten(a)
    for nhan, p in (("Dữ liệu mới", dl_moi), ("Dữ liệu cũ ", dl_cu), ("Skill mới  ", sk_moi), ("Skill cũ   ", sk_cu)):
        print(nhan + ":", p, ("liên kết -> " + os.readlink(p)) if os.path.islink(p) else ("thư mục thật" if os.path.isdir(p) else "không có"))
    for t in (a.sang, a.tu):
        p = os.path.join(mk, t)
        print("Liên kết %-24s %s" % (t + ":", os.readlink(p) if os.path.islink(p) else "không có"))
    m = doc(os.path.join(mk, ".claude-plugin", "marketplace.json"), {}) or {}
    print("marketplace.json:", [x.get("name") for x in m.get("plugins", [])])
    st = doc(os.path.join(NHA, "settings.json"), {}) or {}
    ep = st.get("enabledPlugins", {})
    print("enabledPlugins:", {k: v for k, v in ep.items() if k.split("@")[0] in (a.sang, a.tu)})
    for t in (a.skill_sang, a.skill_tu):
        sk = os.path.join(NHA, "skills", t)
        print("Skill %s ->" % t, os.readlink(sk) if os.path.islink(sk) else ("thư mục thật" if os.path.isdir(sk) else "không có"))
    return 0


def lam(a):
    mk = os.path.abspath(a.marketplace)
    kho = os.path.abspath(a.kho)
    dl_moi, dl_cu, sk_moi, sk_cu = ten(a)
    ban_cu = os.path.abspath(a.ban_cu) if a.ban_cu else os.path.realpath(os.path.join(mk, a.tu))
    if not os.path.isfile(os.path.join(kho, "kenh.json")):
        print("Thiếu %s/kenh.json: phát bản mới trước (phat_ban.py)" % kho); return 1
    luc = time.strftime("%y%m%d-%H%M%S")
    # 2. dữ liệu plugin + dữ liệu skill
    chuyen_thu_muc(dl_cu, dl_moi)
    if a.skill_tu != a.skill_sang:
        chuyen_thu_muc(sk_cu, sk_moi)
    os.makedirs(os.path.join(dl_moi, "sao_luu"), exist_ok=True)
    sl = os.path.join(dl_moi, "sao_luu")
    # 1. sao lưu
    st_tep = os.path.join(NHA, "settings.json")
    mf = os.path.join(mk, ".claude-plugin", "marketplace.json")
    if os.path.isfile(st_tep):
        shutil.copy2(st_tep, os.path.join(sl, "settings.json.truoc-doi-ten-" + luc))
    shutil.copy2(mf, os.path.join(sl, "marketplace.json.truoc-doi-ten-" + luc))
    # 3. cấu hình cập nhật + cài đặt
    lk_moi = os.path.join(mk, a.sang)
    cn = os.path.join(dl_moi, "cap_nhat.json")
    c = doc(cn, {}) or {}
    if c.get("lien_ket") != lk_moi:   # chạy lại không ghi đè đường cũ
        c["kenh_cu"], c["lien_ket_cu"] = c.get("kenh", ""), c.get("lien_ket", "")
    c["kenh"], c["lien_ket"] = os.path.join(kho, "kenh.json"), lk_moi
    ghi(cn, thay_duong(c, dl_cu + "/", dl_moi + "/"))
    cd = os.path.join(dl_moi, "cai_dat.json")
    if os.path.isfile(cd):
        ghi(cd, thay_duong(doc(cd, {}), dl_cu + "/", dl_moi + "/"))
    # 4. marketplace
    m = doc(mf, {})
    if not any(x.get("name") == a.sang for x in m.get("plugins", [])):
        m.setdefault("plugins", []).append({"name": a.sang, "source": "./" + a.sang, "description": MO_TA})
        ghi(mf, m)
    # 5. liên kết cài đặt mới (trỏ bản cũ; ap-dung sẽ đưa lên bản mới)
    if not os.path.lexists(lk_moi):
        lien_ket(lk_moi, ban_cu)
    # 6. skill cài tay (chỉ khi là liên kết hoặc chưa có)
    sk_l_cu, sk_l_moi = os.path.join(NHA, "skills", a.skill_tu), os.path.join(NHA, "skills", a.skill_sang)
    co_lk = os.path.islink(sk_l_cu) or os.path.islink(sk_l_moi)
    if co_lk:
        nguon_sk = os.path.join(lk_moi, "skills", a.skill_sang)
        if not os.path.isdir(nguon_sk):
            nguon_sk = os.path.join(lk_moi, "skills", a.skill_tu)
        if os.path.isdir(nguon_sk) and (os.path.islink(sk_l_moi) or not os.path.exists(sk_l_moi)):
            lien_ket(sk_l_moi, nguon_sk, giai=False)
            if sk_l_cu != sk_l_moi and os.path.islink(sk_l_cu):
                os.remove(sk_l_cu)
    ghi(os.path.join(dl_moi, "doi_ten.json"), {"luc": int(time.time()), "tu": a.tu, "sang": a.sang,
                                               "skill_tu": a.skill_tu, "skill_sang": a.skill_sang,
                                               "settings_sao_luu": os.path.join(sl, "settings.json.truoc-doi-ten-" + luc),
                                               "marketplace_sao_luu": os.path.join(sl, "marketplace.json.truoc-doi-ten-" + luc)})
    print("Xong phần tệp. Tiếp theo:\n  python3 %s/scripts/cap_nhat.py ap-dung\n  claude plugin install %s@<marketplace>\n  claude plugin disable %s@<marketplace>"
          % (lk_moi, a.sang, a.tu))
    return 0


def quay_lui(a):
    mk = os.path.abspath(a.marketplace)
    dl_moi, dl_cu, sk_moi, sk_cu = ten(a)
    tra_thu_muc(dl_cu, dl_moi)
    if a.skill_tu != a.skill_sang:
        tra_thu_muc(sk_cu, sk_moi)
    cn = os.path.join(dl_cu, "cap_nhat.json")
    c = doc(cn, {}) or {}
    if c.get("kenh_cu"):
        c["kenh"], c["lien_ket"] = c.pop("kenh_cu"), c.pop("lien_ket_cu")
        ghi(cn, thay_duong(c, dl_moi + "/", dl_cu + "/"))
    cd = os.path.join(dl_cu, "cai_dat.json")
    if os.path.isfile(cd):
        ghi(cd, thay_duong(doc(cd, {}), dl_moi + "/", dl_cu + "/"))
    sk_l_cu, sk_l_moi = os.path.join(NHA, "skills", a.skill_tu), os.path.join(NHA, "skills", a.skill_sang)
    nguon_cu = os.path.join(mk, a.tu, "skills", a.skill_tu)
    if (os.path.islink(sk_l_moi) or os.path.islink(sk_l_cu)) and os.path.isdir(nguon_cu):
        lien_ket(sk_l_cu, nguon_cu, giai=False)
        if sk_l_cu != sk_l_moi and os.path.islink(sk_l_moi):
            os.remove(sk_l_moi)
    print("Xong. Tiếp theo:\n  claude plugin disable %s@<marketplace>\n  claude plugin enable %s@<marketplace>" % (a.sang, a.tu))
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("viec", choices=["trang-thai", "lam", "quay-lui"])
    p.add_argument("--marketplace", required=True)
    p.add_argument("--kho")
    p.add_argument("--ban-cu")
    p.add_argument("--tu", default="tintmark-tietkiem")
    p.add_argument("--sang", default="tintmark-tietkiemtoken")
    p.add_argument("--skill-tu", default="tintmark-token")
    p.add_argument("--skill-sang", default="tintmark-tietkiemtoken")
    a = p.parse_args(argv)
    if a.viec == "lam" and not a.kho:
        p.error("lam cần --kho")
    return {"trang-thai": trang_thai, "lam": lam, "quay-lui": quay_lui}[a.viec](a)


if __name__ == "__main__":
    sys.exit(main())
