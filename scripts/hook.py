#!/usr/bin/env python3
"""Hook PreToolUse (Bash): bọc lệnh đơn giản có luật nén qua nen.py.

Chỉ hoạt động khi cấu hình che_do = "truoc" (dự phòng cho Claude Code cũ không có
updatedToolOutput). Mặc định từ 0.2.0 là "sau" (hook_sau.py), hook này im lặng.
Trong auto mode KHÔNG bọc gì: bộ duyệt từ chối lệnh bị hook đổi (đã gặp thật 15/11/2026 với cả `ls`).
Kiêm: ghi dấu hiệu nghi hỏng khi lệnh vừa nén bị chạy lại với NEN_OFF=1.

An toàn: lỗi bất kỳ => thoát im lặng (lệnh chạy nguyên bản).
Bỏ qua lệnh: có | & ; < > ( ) $ ` \\ { } # hoặc xuống dòng/heredoc; chạy nền;
đã bọc; NEN_OFF=1; không có luật khớp; ngoặc kép không cân.
Không đặt permissionDecision => quyền vẫn do Claude Code hỏi như cũ.
(NEN_AUTO_ALLOW=1 mới thêm "allow".)
"""
import json
import os
import shlex
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

NGUY_HIEM = set("|&;<>()$`\\{}#\n\r")


def co_the_boc(lenh):
    if not lenh or not lenh.strip():
        return False
    if any(c in NGUY_HIEM for c in lenh):
        return False
    if "nen.py" in lenh or lenh.lstrip().startswith("NEN_OFF=") or "NEN_OFF=1" in lenh:
        return False
    try:
        tu = shlex.split(lenh)
    except ValueError:
        return False
    if not tu or "=" in tu[0] or tu[0] in ("cd", "export", "source", ".", "exec", "eval", "time"):
        return False
    return True


def viet_lai(lenh, che_do_quyen=""):
    """Trả về lệnh đã bọc, hoặc None nếu không nên bọc."""
    if os.environ.get("NEN_OFF") == "1" or not co_the_boc(lenh):
        return None
    import nen_loi
    import nen  # noqa: F401  nen.py hỏng cú pháp => ngoại lệ ở đây => không bọc
    luat = nen_loi.tim_luat(lenh)
    if luat is None:
        return None
    if che_do_quyen == "auto":
        return None
    nen_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nen.py")
    return "%s %s -c %s" % (shlex.quote(sys.executable), shlex.quote(nen_py), shlex.quote(lenh))


def main():
    try:
        d = json.load(sys.stdin)
        if d.get("tool_name") != "Bash":
            return
        ti = d.get("tool_input") or {}
        if ti.get("run_in_background"):
            return
        import nen_loi
        lenh = (ti.get("command") or "").strip()
        che_do = nen_loi.cau_hinh()["che_do"]
        if che_do != "truoc":
            return
        if lenh.startswith("NEN_OFF=1 "):
            import hook_sau
            hook_sau.ghi_nghi(nen_loi, lenh[len("NEN_OFF=1 "):].strip(), str(d.get("session_id") or ""))
            return
        moi = viet_lai(lenh, d.get("permission_mode") or "")
        if not moi:
            return
        ti = dict(ti)
        ti["command"] = moi
        out = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "updatedInput": ti}}
        if os.environ.get("NEN_AUTO_ALLOW") == "1" and d.get("permission_mode") != "auto":
            out["hookSpecificOutput"]["permissionDecision"] = "allow"
            out["hookSpecificOutput"]["permissionDecisionReason"] = "tintmark-tietkiemtoken: bọc nén"
        sys.stdout.write(json.dumps(out, ensure_ascii=False))
    except Exception:
        return


if __name__ == "__main__":
    main()
