#!/usr/bin/env python3
"""Chạy lệnh thật, nén output, giữ nguyên mã thoát.

  nen.py -c "git status"        chạy chuỗi lệnh qua bash -c
  nen.py -- git status          chạy theo argv
  nen.py --raw -c "..."         không nén (hoặc đặt NEN_OFF=1)
Mọi lỗi của phần nén => in output gốc. Không bao giờ chặn lệnh.
"""
import os
import shlex
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import nen_loi  # noqa: E402
except Exception:  # lõi nén hỏng => chạy lệnh nguyên bản, không chặn
    nen_loi = None


def main(argv):
    raw = os.environ.get("NEN_OFF") == "1" or nen_loi is None
    if argv and argv[0] == "--raw":
        raw, argv = True, argv[1:]
    if len(argv) >= 2 and argv[0] == "-c":
        lenh = argv[1]
    elif argv and argv[0] == "--":
        lenh = " ".join(shlex.quote(a) for a in argv[1:])
    else:
        lenh = " ".join(shlex.quote(a) for a in argv)
    if not lenh.strip():
        sys.stderr.write("nen.py: thiếu lệnh\n")
        return 2
    sh = "/bin/bash" if os.path.exists("/bin/bash") else "/bin/sh"

    luat = None
    if not raw:
        try:
            luat = nen_loi.tim_luat(lenh)
        except Exception:
            luat = None
    if luat is None:  # không nén: chạy thẳng, output đi thẳng ra
        return _ma(subprocess.call([sh, "-c", lenh]))

    t0 = time.time()
    p = subprocess.Popen([sh, "-c", lenh], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for s in (signal.SIGTERM, signal.SIGINT):
        signal.signal(s, lambda n, f: (p.send_signal(n), None)[1])
    out_b, err_b = p.communicate()
    ma = _ma(p.returncode)
    ra_out, ra_err = out_b, err_b
    try:
        so = nen_loi.nen_an_toan(out_b.decode("utf-8", "replace"), luat, ma)
        se = nen_loi.nen_an_toan(err_b.decode("utf-8", "replace"), luat, ma)
        # chỉ dùng bản nén nếu thật sự đã nén (nen_an_toan trả nguyên chuỗi khi không nén)
        if so != out_b.decode("utf-8", "replace"):
            ra_out = so.encode("utf-8")
        if se != err_b.decode("utf-8", "replace"):
            ra_err = se.encode("utf-8")
    except Exception:
        pass
    sys.stdout.buffer.write(ra_out)
    sys.stdout.buffer.flush()
    sys.stderr.buffer.write(ra_err)
    sys.stderr.buffer.flush()
    if ra_out != out_b or ra_err != err_b:
        nen_loi.luu_gan_day(lenh, luat.get("id", "?"), (out_b + err_b).decode("utf-8", "replace"), ma)
    nen_loi.ghi_thong_ke(luat.get("id", "?"), lenh, len(out_b) + len(err_b), len(ra_out) + len(ra_err),
                         ma, int((time.time() - t0) * 1000))
    return ma


def _ma(rc):
    return 128 - rc if rc < 0 else rc


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except BrokenPipeError:
        sys.exit(141)
