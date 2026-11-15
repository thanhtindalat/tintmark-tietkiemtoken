#!/usr/bin/env python3
# Copyright (c) 2026 Tintmark. All rights reserved. Xem LICENSE / NOTICE.
"""Gộp skill token vào plugin trên máy này, có sao lưu và gỡ được.

  cai_dat.py trang-thai
  cai_dat.py gop --lien-ket <liên kết cài đặt> --kenh <kenh.json> [--nguon <thư mục nguồn>] [--tu-dong bao|ap_dung|tat]
        1) sao lưu ~/.claude/settings.json  2) bỏ 2 hook ngưỡng cũ trong settings (plugin đã mang hook này)
        3) ~/.claude/skills/tintmark-tietkiemtoken: chuyển bản cũ vào sao lưu, thay bằng liên kết tới skill trong plugin
           (phiên đang mở vẫn gọi được hook / skill theo đường dẫn cũ)  4) ghi cấu hình cập nhật
  cai_dat.py go        trả settings.json và skill về như trước khi gộp (plugin thì `claude plugin disable tintmark-tietkiemtoken`)
KHÔNG chạy `gop` khi chưa kiểm hook ngưỡng của plugin đã chạy trong một phiên mới.
"""
import argparse
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nen_loi  # noqa: E402

NHA = os.environ.get("NEN_NHA") or os.path.expanduser("~/.claude")
DAU = "tintmark-tietkiemtoken/cong_cu/nguong_token.py"


def bo_hook_cu(st):
    """Bỏ các hook lệnh trỏ tới hook ngưỡng ở skill người dùng. Trả số mục đã bỏ."""
    n = 0
    hooks = st.get("hooks") or {}
    for su_kien in list(hooks):
        nhom_moi = []
        for nhom in hooks[su_kien]:
            con = [h for h in nhom.get("hooks", []) if not ("skills/" + DAU in (h.get("command") or ""))]
            n += len(nhom.get("hooks", [])) - len(con)
            if con:
                nhom_moi.append(dict(nhom, hooks=con))
        if nhom_moi:
            hooks[su_kien] = nhom_moi
        else:
            del hooks[su_kien]
    return n


def main(argv=None):
    p = argparse.ArgumentParser()
    s = p.add_subparsers(dest="viec", required=True)
    s.add_parser("trang-thai"); s.add_parser("go")
    g = s.add_parser("gop")
    g.add_argument("--lien-ket", required=True); g.add_argument("--kenh", required=True)
    g.add_argument("--nguon", default=""); g.add_argument("--tu-dong", default="bao", choices=["bao", "ap_dung", "tat"])
    o = p.parse_args(argv)
    st_tep = os.path.join(NHA, "settings.json")
    skill = os.path.join(NHA, "skills", "tintmark-tietkiemtoken")
    tt_tep = nen_loi.tep("cai_dat.json")
    tt = nen_loi.doc_json(tt_tep, {}) or {}

    if o.viec == "trang-thai":
        st = nen_loi.doc_json(st_tep, {}) or {}
        cu = sum(1 for ns in (st.get("hooks") or {}).values() for n in ns for h in n.get("hooks", [])
                 if "skills/" + DAU in (h.get("command") or ""))
        print("Hook ngưỡng cũ trong settings.json: %d" % cu)
        print("Skill người dùng: %s" % ("liên kết -> " + os.readlink(skill) if os.path.islink(skill)
                                        else "thư mục thật" if os.path.isdir(skill) else "không có"))
        print("Đã gộp: %s" % (time.strftime("%d/%m/%Y %H:%M", time.localtime(tt["luc"])) if tt.get("luc") else "chưa"))
        print("Bản plugin đang cài: %s · chế độ nén: %s" % (nen_loi.phien_ban(), nen_loi.cau_hinh()["che_do"]))
        ten = (nen_loi.doc_json(os.path.join(nen_loi.GOC, ".claude-plugin", "plugin.json"), {}) or {}).get("name", "")
        ghi = (nen_loi.doc_json(os.path.join(NHA, "plugins", "installed_plugins.json"), {}) or {}).get("plugins", {})
        for k, v in ghi.items():
            if k.split("@")[0] == ten and isinstance(v, list) and v:
                ban = v[-1].get("version", "?")
                print("Claude Code ghi nhận %s: bản %s%s" % (k, ban, "" if ban == nen_loi.phien_ban() else
                      "  ⚠ LỆCH (chạy: claude plugin marketplace update %s && claude plugin update %s)" % (k.split("@")[-1], k)))
        return 0
    if o.viec == "gop":
        lk = os.path.abspath(o.lien_ket)
        dich_skill = os.path.join(lk, "skills", "tintmark-tietkiemtoken")
        if not os.path.isfile(os.path.join(dich_skill, "cong_cu", "nguong_token.py")):
            print("Bản plugin ở %s chưa có skill + hook ngưỡng: cập nhật plugin trước." % lk); return 1
        dau = time.strftime("%y%m%d-%H%M%S")
        sl = nen_loi.tep("sao_luu"); os.makedirs(sl, exist_ok=True)
        st = nen_loi.doc_json(st_tep)
        if not isinstance(st, dict):
            print("Không đọc được settings.json: dừng."); return 1
        sl_st = os.path.join(NHA, "settings.json.truoc-gop-token-" + dau)
        shutil.copy2(st_tep, sl_st)
        n = bo_hook_cu(st)
        nen_loi.ghi_json(st_tep, st)
        sl_skill = ""
        if os.path.isdir(skill) and not os.path.islink(skill):
            sl_skill = os.path.join(sl, "skill-tintmark-tietkiemtoken-" + dau)
            shutil.move(skill, sl_skill)
        if os.path.islink(skill):
            os.remove(skill)
        os.symlink(dich_skill, skill)
        c = nen_loi.doc_json(nen_loi.tep("cap_nhat.json"), {}) or {}
        c.update(kenh=os.path.abspath(o.kenh), lien_ket=lk, tu_dong=o.tu_dong)
        if o.nguon:
            c["nguon"] = os.path.abspath(o.nguon)
        nen_loi.ghi_json(nen_loi.tep("cap_nhat.json"), c)
        tt.update(luc=int(time.time()), settings_sao_luu=sl_st, skill_sao_luu=sl_skill or tt.get("skill_sao_luu", ""))
        nen_loi.ghi_json(tt_tep, tt)
        print("Đã gộp: bỏ %d hook ngưỡng cũ; settings sao lưu ở %s; skill cũ ở %s; skill người dùng -> %s" % (
            n, sl_st, sl_skill or "(đã là liên kết)", dich_skill))
        print("Gỡ: python3 %s go" % os.path.abspath(__file__))
        return 0
    # go
    if not tt.get("settings_sao_luu") or not os.path.isfile(tt["settings_sao_luu"]):
        print("Không thấy bản sao lưu settings của lần gộp: không đổi gì."); return 1
    shutil.copy2(st_tep, st_tep + ".truoc-go-" + time.strftime("%y%m%d-%H%M%S"))
    shutil.copy2(tt["settings_sao_luu"], st_tep)
    if os.path.islink(skill):
        os.remove(skill)
    if tt.get("skill_sao_luu") and os.path.isdir(tt["skill_sao_luu"]) and not os.path.exists(skill):
        shutil.copytree(tt["skill_sao_luu"], skill)
    tt["luc"] = 0
    nen_loi.ghi_json(tt_tep, tt)
    print("Đã trả settings.json và skill về trước khi gộp. LƯU Ý: thay đổi settings sau lần gộp đã mất "
          "(bản ngay trước khi gỡ: settings.json.truoc-go-*). Tắt plugin: claude plugin disable tintmark-tietkiemtoken@<marketplace>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
