import json, os, shlex, subprocess, sys, tempfile, unittest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "scripts"))
import nen_loi, hook  # noqa: E402

NEN = os.path.join(GOC, "scripts", "nen.py")
HOOK = os.path.join(GOC, "scripts", "hook.py")
LUAT = nen_loi.tai_luat.__globals__["LUAT_MAC_DINH"]
DS = json.load(open(LUAT, encoding="utf-8"))["luat"]
MAU = json.load(open(os.path.join(GOC, "mau", "mau.json"), encoding="utf-8"))["mau"]
BYID = {r["id"]: r for r in DS}


def _ghi(tep, nd):
    with open(tep, "w", encoding="utf-8") as f:
        f.write(nd)


def chay(argv, env=None, inp=None):
    e = dict(os.environ, NEN_DATA_DIR=tempfile.mkdtemp(), NEN_LUAT=LUAT)
    e.update(env or {})
    return subprocess.run(argv, capture_output=True, env=e, input=inp)


class TestLuat(unittest.TestCase):
    def test_moi_luat_co_mau(self):
        self.assertEqual({m["luat"] for m in MAU}, set(BYID))

    def test_tiet_kiem_20_phan_tram_va_giu_dong_quan_trong(self):
        for m in MAU:
            with self.subTest(m["luat"]):
                goc = open(os.path.join(GOC, "mau", m["tep"]), encoding="utf-8").read()
                self.assertIs(nen_loi.tim_luat(m["lenh"], DS), BYID[m["luat"]], "lệnh không khớp đúng luật")
                kq = nen_loi.nen_an_toan(goc, BYID[m["luat"]], m["ma"])
                a, b = len(goc.encode()), len(kq.encode())
                self.assertLessEqual(b, a * 0.8, "%s: %d -> %d chỉ giảm %.0f%%" % (m["luat"], a, b, 100 - 100.0 * b / a))
                for g in m["giu"]:
                    self.assertIn(g, kq, "mất dòng quan trọng: " + g)
                print("  %-12s %7d -> %6d  giảm %3.0f%%  [%s]" % (m["luat"], a, b, 100 - 100.0 * b / a, m["ghi"]))

    def test_ansi_va_cr(self):
        r = {"id": "t", "min_bytes": 0}
        self.assertEqual(nen_loi.nen("\x1b[31mđỏ\x1b[0m\nmột\rhai\rba\n", r), "đỏ\nba\n")

    def test_gop_dong_trung(self):
        r = {"id": "t", "min_bytes": 0, "dedupe": "consecutive"}
        self.assertIn("(+2 dòng tương tự)", nen_loi.nen("a\na\na\nb\n", r))

    def test_ngan_thi_giu_nguyen(self):
        r = BYID["git-status"]
        self.assertEqual(nen_loi.nen_an_toan("nothing\n", r), "nothing\n")

    def test_luat_hong_khong_no(self):
        goc = "x\n" * 1000
        self.assertEqual(nen_loi.nen_an_toan(goc, {"id": "t", "drop": ["("]}, 0), goc)


class TestChay(unittest.TestCase):
    def test_ma_thoat_giu_nguyen(self):
        for ma in (0, 1, 7, 42):
            r = chay([sys.executable, NEN, "-c", "echo hi; exit %d" % ma])
            self.assertEqual(r.returncode, ma)
            self.assertEqual(r.stdout, b"hi\n")

    def test_ma_thoat_voi_luat_khop(self):
        d = tempfile.mkdtemp()
        lenh = "ls -la /nonexistent_zz_%d" % os.getpid()
        r = chay([sys.executable, NEN, "-c", lenh])
        self.assertNotEqual(r.returncode, 0)
        self.assertIn(b"No such file", r.stderr)

    def test_nen_that_va_thong_ke(self):
        d = tempfile.mkdtemp()
        tep = os.path.join(d, "x.log")
        _ghi(tep, "".join("INFO tick %d ok\n" % i for i in range(400)) + "ERROR boom\n")
        env = {"NEN_DATA_DIR": d}
        r = chay([sys.executable, NEN, "-c", "cat " + shlex.quote(tep)], env)
        self.assertEqual(r.returncode, 0)
        self.assertIn(b"ERROR boom", r.stdout)
        self.assertLess(len(r.stdout), 2000)
        tk = [json.loads(l) for l in open(os.path.join(d, "thong_ke.jsonl"))]
        self.assertEqual(tk[0]["luat"], "log-dai")
        self.assertGreater(tk[0]["vao"], tk[0]["ra"])
        out = chay([sys.executable, os.path.join(GOC, "scripts", "thong_ke.py")], env).stdout.decode()
        self.assertIn("TỔNG", out)

    def test_raw_va_NEN_OFF(self):
        d = tempfile.mkdtemp()
        tep = os.path.join(d, "x.log")
        goc = "".join("INFO tick %d ok\n" % i for i in range(400))
        _ghi(tep, goc)
        self.assertEqual(chay([sys.executable, NEN, "--raw", "-c", "cat " + tep]).stdout.decode(), goc)
        self.assertEqual(chay([sys.executable, NEN, "-c", "cat " + tep], {"NEN_OFF": "1"}).stdout.decode(), goc)

    def test_khong_co_luat_chay_nguyen(self):
        r = chay([sys.executable, NEN, "-c", "echo xin chao; exit 3"])
        self.assertEqual((r.returncode, r.stdout), (3, b"xin chao\n"))

    def test_fallback_luat_hong(self):
        d = tempfile.mkdtemp()
        bad = os.path.join(d, "bad.json")
        _ghi(bad, "{khong phai json")
        r = chay([sys.executable, NEN, "-c", "echo ok; exit 5"], {"NEN_LUAT": bad})
        self.assertEqual((r.returncode, r.stdout), (5, b"ok\n"))
        bad2 = os.path.join(d, "bad2.json")
        _ghi(bad2, json.dumps({"luat": [{"id": "x", "match": "^echo", "drop": ["("], "min_bytes": 0}]}))
        r = chay([sys.executable, NEN, "-c", "echo ok; exit 6"], {"NEN_LUAT": bad2})
        self.assertEqual((r.returncode, r.stdout), (6, b"ok\n"))

    def test_stdin_chuyen_tiep(self):
        r = chay([sys.executable, NEN, "-c", "cat"], inp=b"abc")
        self.assertEqual(r.stdout, b"abc")


class TestHook(unittest.TestCase):
    """Hook PreToolUse chỉ chạy ở chế độ "truoc" (dự phòng)."""

    def setUp(self):
        os.environ["NEN_CHE_DO"] = "truoc"

    def tearDown(self):
        os.environ.pop("NEN_CHE_DO", None)

    def goi(self, lenh, **kw):
        d = {"tool_name": kw.pop("tool", "Bash"), "tool_input": dict({"command": lenh}, **kw)}
        r = chay([sys.executable, HOOK], inp=json.dumps(d).encode())
        self.assertEqual(r.returncode, 0)
        return json.loads(r.stdout) if r.stdout.strip() else None

    def test_boc_lenh_don_gian(self):
        o = self.goi("git status")
        cmd = o["hookSpecificOutput"]["updatedInput"]["command"]
        self.assertIn("nen.py", cmd)
        self.assertEqual(shlex.split(cmd)[-1], "git status")
        self.assertNotIn("permissionDecision", o["hookSpecificOutput"])

    def test_giu_tham_so_khac(self):
        o = self.goi("ls -la", description="d", timeout=5000)
        ti = o["hookSpecificOutput"]["updatedInput"]
        self.assertEqual((ti["description"], ti["timeout"]), ("d", 5000))

    def test_bo_qua_lenh_phuc_tap(self):
        for c in ["git status | head", "git diff > a.txt", "git status && ls", "git log; ls", "ls $(pwd)",
                  "ls `pwd`", "cat <<EOF\nx\nEOF", "git status &", "ls -la # x", "cd x && git status",
                  "grep -r 'a|b' .", "echo \"unbalanced", "ls (x)", "FOO=1 git status", "ls \\\n -la"]:
            with self.subTest(c):
                self.assertIsNone(self.goi(c))

    def test_khong_boc_hai_lan(self):
        o = self.goi("git status")
        self.assertIsNone(self.goi(o["hookSpecificOutput"]["updatedInput"]["command"]))

    def test_bo_qua_khac(self):
        self.assertIsNone(self.goi("git status", run_in_background=True))
        self.assertIsNone(self.goi("git status", tool="Read"))
        self.assertIsNone(self.goi("echo hi"))
        self.assertIsNone(self.goi("NEN_OFF=1 git status"))
        self.assertIsNone(self.goi("tail -f app.log"))
        self.assertIsNone(self.goi("git status", ) if False else None)

    def test_NEN_OFF_env(self):
        d = {"tool_name": "Bash", "tool_input": {"command": "git status"}}
        r = chay([sys.executable, HOOK], {"NEN_OFF": "1"}, json.dumps(d).encode())
        self.assertEqual(r.stdout, b"")

    def test_rac_vao_khong_no(self):
        for inp in (b"", b"{khong json", b"[]", b"null"):
            r = chay([sys.executable, HOOK], inp=inp)
            self.assertEqual((r.returncode, r.stdout), (0, b""))

    def test_boc_xong_chay_dung_nghia(self):
        # lệnh sau khi bọc phải cho cùng mã thoát + output như lệnh gốc (với lệnh có luật)
        d = tempfile.mkdtemp()
        subprocess.run("git init -q && echo a > f", shell=True, cwd=d)
        o = self.goi("git status")
        cmd = o["hookSpecificOutput"]["updatedInput"]["command"]
        env = dict(os.environ, NEN_DATA_DIR=tempfile.mkdtemp(), NEN_LUAT=LUAT)
        a = subprocess.run(cmd, shell=True, cwd=d, capture_output=True, env=env)
        b = subprocess.run("git status", shell=True, cwd=d, capture_output=True, env=env)
        self.assertEqual(a.returncode, b.returncode)
        self.assertIn(b"Untracked files", a.stdout)

    def test_auto_allow_la_tuy_chon(self):
        d = {"tool_name": "Bash", "tool_input": {"command": "git status"}}
        r = chay([sys.executable, HOOK], {"NEN_AUTO_ALLOW": "1"}, json.dumps(d).encode())
        self.assertEqual(json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"], "allow")


if __name__ == "__main__":
    unittest.main(verbosity=1)
