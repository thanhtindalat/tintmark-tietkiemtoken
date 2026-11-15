#!/usr/bin/env python3
# Copyright (c) 2026 Tintmark. All rights reserved. Xem LICENSE / NOTICE.
"""Hook PostToolUse (Bash): nén output SAU khi lệnh đã chạy (chế độ "sau", mặc định từ 0.2.0).

Không đổi lệnh => không đụng bộ duyệt quyền / auto mode; lệnh lỗi (mã thoát khác 0) đi theo
PostToolUseFailure nên không bao giờ bị nén. Trả `updatedToolOutput` cùng hình dạng tool_response.
Kiêm: ghi dấu hiệu nghi hỏng khi cùng lệnh vừa nén bị chạy lại với NEN_OFF=1.
An toàn: lỗi bất kỳ => không in gì (model nhận output gốc).
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


CD = re.compile(r"""^cd\s+("[^"$`\\]*"|'[^']*'|[^\s|&;<>()$`\\{}#"']+)\s*&&\s*(\S.*)$""", re.S)


def bo_cd(lenh):
    """`cd <thư mục> && <lệnh>` -> `<lệnh>` để khớp luật (chỉ đọc kết quả, lệnh không bị đổi).
    Phần sau `&&` vẫn phải qua co_the_boc như mọi lệnh khác."""
    m = CD.match(lenh)
    return m.group(2).strip() if m else lenh


def xu_ly(d):
    import hook
    import nen_loi
    if d.get("tool_name") != "Bash":
        return None
    lenh = ((d.get("tool_input") or {}).get("command") or "").strip()
    phien = str(d.get("session_id") or "")
    if lenh.startswith("NEN_OFF=1 "):
        ghi_nghi(nen_loi, lenh[len("NEN_OFF=1 "):].strip(), phien)
        return None
    if os.environ.get("NEN_OFF") == "1" or nen_loi.cau_hinh()["che_do"] != "sau":
        return None
    import module
    if not module.bat("nen", d.get("cwd")):
        return None
    tr = d.get("tool_response")
    if not isinstance(tr, dict) or tr.get("interrupted") or tr.get("isImage"):
        return None
    lenh = bo_cd(lenh)
    if (d.get("tool_input") or {}).get("run_in_background") or not hook.co_the_boc(lenh):
        return None
    luat = nen_loi.tim_luat(lenh)
    if luat is None:
        return None
    moi, doi, vao, ra = dict(tr), False, 0, 0
    for k in ("stdout", "stderr"):
        goc = tr.get(k)
        if not isinstance(goc, str) or not goc:
            continue
        kq = nen_loi.nen_an_toan(goc, luat, 0)
        vao += len(goc.encode("utf-8", "replace"))
        ra += len(kq.encode("utf-8", "replace"))
        if kq != goc:
            moi[k], doi = kq, True
    if not doi:
        return None
    nen_loi.luu_gan_day(lenh, luat.get("id", "?"), (tr.get("stdout") or "") + (tr.get("stderr") or ""), 0, phien)
    nen_loi.ghi_thong_ke(luat.get("id", "?"), lenh, vao, ra, 0, 0)
    return {"hookSpecificOutput": {"hookEventName": "PostToolUse", "updatedToolOutput": moi}}


def ghi_nghi(nen_loi, lenh, phien=""):
    """Lệnh vừa được nén mà bị chạy lại ngay ở chế độ đầy đủ => ghi phản hồi tự động."""
    m = nen_loi.tim_gan_day(lenh)
    if not m:
        return None
    goc = None
    try:
        with open(nen_loi.tep("gan_day", m["khoa"] + ".txt"), encoding="utf-8") as f:
            goc = f.read()
    except Exception:
        pass
    da = [p for p in nen_loi.ds_phan_hoi() if p.get("nguon") == "tu-dong" and p.get("lenh") == lenh
          and p.get("luc", 0) >= m.get("ts", 0)]
    if da:  # một lần nén chỉ ghi nghi một lần
        return None
    return nen_loi.ghi_phan_hoi("nghi-chay-lai", lenh, m.get("luat", ""),
                                "tự ghi: lệnh vừa nén bị chạy lại với NEN_OFF=1", goc=goc, nguon="tu-dong",
                                phien=phien)


def main():
    try:
        kq = xu_ly(json.load(sys.stdin))
        if kq:
            sys.stdout.write(json.dumps(kq, ensure_ascii=False))
    except Exception:
        return


if __name__ == "__main__":
    main()
