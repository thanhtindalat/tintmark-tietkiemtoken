# Copyright (c) 2026 Tintmark. All rights reserved. Xem LICENSE / NOTICE.
"""Test bản 0.2.x: hook sau (PostToolUse), phản hồi, tự tắt bộ lọc, hook ngưỡng gộp, phát bản, cập nhật, quay lui."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(GOC, "scripts")
NGUONG = os.path.join(GOC, "skills", "tintmark-tietkiemtoken", "cong_cu", "nguong_token.py")
DAI = "".join("/a/b/tep_%d.md\n" % i for i in range(600))


def chay(kich, inp=None, env=None, args=()):
    r = subprocess.run([sys.executable, kich] + list(args), capture_output=True, env=env,
                       input=json.dumps(inp).encode() if isinstance(inp, (dict, list)) else inp)
    return r


class Goc(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.env = dict(os.environ, NEN_DATA_DIR=os.path.join(self.d, "nen"),
                        TINTMARK_TOKEN_DIR=os.path.join(self.d, "tt"), NEN_NHA=os.path.join(self.d, "nha"))
        for k in ("NEN_OFF", "NEN_LUAT", "NEN_CHE_DO"):
            self.env.pop(k, None)

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def sau(self, lenh, out=DAI, err="", **kw):
        d = {"tool_name": "Bash", "session_id": "p1", "hook_event_name": "PostToolUse",
             "tool_input": {"command": lenh},
             "tool_response": dict({"stdout": out, "stderr": err, "interrupted": False, "isImage": False}, **kw)}
        r = chay(os.path.join(S, "hook_sau.py"), d, self.env)
        self.assertEqual((r.returncode, r.stderr), (0, b""))
        return json.loads(r.stdout) if r.stdout.strip() else None

    def du_lieu(self, *ten):
        return os.path.join(self.env["NEN_DATA_DIR"], *ten)

    def doc(self, *ten):
        with open(self.du_lieu(*ten), encoding="utf-8") as f:
            return json.load(f)


class TestNhacPhanHoiCu(Goc):
    def test_nhac_mot_lan_moi_ngay(self):
        for ten, luc, tt in (("PH-cu", time.time() - 4 * 86400, "mo"), ("PH-moi", time.time(), "mo"), ("PH-dong", time.time() - 9 * 86400, "dong")):
            os.makedirs(self.du_lieu("phan_hoi", ten))
            with open(self.du_lieu("phan_hoi", ten, "meta.json"), "w") as f:
                json.dump({"id": ten, "luc": luc, "trang_thai": tt}, f)
        ng = os.path.join(S, "..", "skills", "tintmark-tietkiemtoken", "cong_cu", "nguong_token.py")
        inp = {"hook_event_name": "UserPromptSubmit", "session_id": "p9", "transcript_path": ""}
        r1 = chay(ng, inp, self.env).stdout.decode()
        self.assertIn("1 phản hồi mở quá 3 ngày (PH-cu)", r1)
        self.assertNotIn("phản hồi mở", chay(ng, inp, self.env).stdout.decode())


class TestHookSau(Goc):
    def test_nen_dung_hinh_dang(self):
        o = self.sau("find /a -name x", extra="giữ")["hookSpecificOutput"]
        self.assertEqual(o["hookEventName"], "PostToolUse")
        m = o["updatedToolOutput"]
        self.assertEqual(set(m), {"stdout", "stderr", "interrupted", "isImage", "extra"})
        self.assertLess(len(m["stdout"]), len(DAI) // 3)
        self.assertIn("[nén: bỏ", m["stdout"])
        self.assertIn("/a/b/tep_0.md", m["stdout"]); self.assertIn("/a/b/tep_599.md", m["stdout"])
        self.assertEqual(self.doc("gan_day", "chi_muc.json")[0]["luat"], "find")

    def test_khong_dung_vao(self):
        for lenh, kw in [("find /a | head", {}), ("echo hi", {}), ("NEN_OFF=1 find /a", {}),
                         ("find /a", {"interrupted": True}), ("find /a", {"isImage": True}),
                         ("cd x && find . | head", {}), ("cd x && cd y && find .", {}), ("cd $X && find .", {}),
                         ("find /a -name x", {"stdout": "ngắn\n"})]:
            with self.subTest(lenh=lenh, kw=kw):
                self.assertIsNone(self.sau(lenh, **kw))

    def test_output_toi_nguong_cat_cua_cc(self):
        """stdout ≥ ngưỡng cắt của Claude Code (30000 ký tự hoặc BASH_MAX_OUTPUT_LENGTH): CC cất output gốc ra tệp,
        bản nén không tới model => không nén, không ghi thống kê."""
        self.env.pop("BASH_MAX_OUTPUT_LENGTH", None)
        to = "".join("/a/b/tep_%05d.md\n" % i for i in range(2000))    # 36000 ký tự
        self.assertGreaterEqual(len(to), 30000)
        self.assertIsNone(self.sau("find /a -name x", out=to))
        self.assertIsNone(self.sau("find /a -name x", out=to[:29990], err="e" * 20))
        self.assertFalse(os.path.exists(self.du_lieu("thong_ke.jsonl")))
        self.assertIsNotNone(self.sau("find /a -name x", out=to[:29000]))
        self.assertTrue(os.path.exists(self.du_lieu("thong_ke.jsonl")))
        self.env["BASH_MAX_OUTPUT_LENGTH"] = "50000"
        self.assertIsNotNone(self.sau("find /a -name x", out=to))
        self.env["BASH_MAX_OUTPUT_LENGTH"] = "5000"
        self.assertIsNone(self.sau("find /a -name x"))      # DAI ~9,5 KB > 5000

    def test_cd_roi_lenh(self):
        for lenh in ("cd /a/b && find . -name x", 'cd "/a b" && find .', "cd x &&find ."):
            with self.subTest(lenh=lenh):
                o = self.sau(lenh)
                self.assertIn("[nén: bỏ", o["hookSpecificOutput"]["updatedToolOutput"]["stdout"])

    def test_tool_khac_va_rac(self):
        for inp in (b"", b"{rac", b"[]", b"null", json.dumps({"tool_name": "Read"}).encode(),
                    json.dumps({"tool_name": "Bash", "tool_input": {"command": "find /a"}, "tool_response": "chuoi"}).encode()):
            r = chay(os.path.join(S, "hook_sau.py"), inp, self.env)
            self.assertEqual((r.returncode, r.stdout, r.stderr), (0, b"", b""))

    def test_luat_hong_va_che_do(self):
        os.makedirs(self.du_lieu(), exist_ok=True)
        with open(self.du_lieu("luat_rieng.json"), "w") as f:
            json.dump({"luat": [{"id": "x", "match": "^find", "drop": ["("], "min_bytes": 0}]}, f)
        self.assertIsNone(self.sau("find /a"))            # luật hỏng => output gốc
        os.remove(self.du_lieu("luat_rieng.json"))
        for cd in ("truoc", "tat"):
            self.env["NEN_CHE_DO"] = cd
            self.assertIsNone(self.sau("find /a"))

    def test_loi_ma_thoat_khong_qua_hook_nay(self):
        # Lệnh lỗi đi theo PostToolUseFailure (không đăng ký) => không có đường nào nén lỗi ở chế độ "sau".
        with open(os.path.join(GOC, "hooks", "hooks.json"), encoding="utf-8") as f:
            self.assertNotIn("PostToolUseFailure", json.load(f)["hooks"])


class TestHookTruocAuto(Goc):
    def goi(self, lenh, che_do_quyen):
        self.env["NEN_CHE_DO"] = "truoc"
        r = chay(os.path.join(S, "hook.py"), {"tool_name": "Bash", "permission_mode": che_do_quyen,
                                              "tool_input": {"command": lenh}}, self.env)
        return json.loads(r.stdout) if r.stdout.strip() else None

    def test_auto_khong_boc_gi(self):
        self.assertIsNone(self.goi("find /a", "auto"))
        self.assertIsNone(self.goi("ls -la /x", "auto"))
        self.assertIsNone(self.goi("python3 -m unittest", "auto"))
        self.assertIsNotNone(self.goi("find /a", "default"))
        self.assertIsNotNone(self.goi("python3 -m unittest", "default"))

    def test_mac_dinh_hook_truoc_im(self):
        r = chay(os.path.join(S, "hook.py"), {"tool_name": "Bash", "tool_input": {"command": "find /a"}}, self.env)
        self.assertEqual(r.stdout, b"")


class TestPhanHoiTuTat(Goc):
    def test_nghi_chay_lai_roi_tu_tat(self):
        for i in range(3):
            lenh = "find /a -name x%d" % i
            self.assertIsNotNone(self.sau(lenh))
            self.assertIsNone(self.sau("NEN_OFF=1 " + lenh, out="x"))
            self.assertIsNone(self.sau("NEN_OFF=1 " + lenh, out="x"))   # lần hai không ghi trùng
        ph = sorted(os.listdir(self.du_lieu("phan_hoi")))
        self.assertEqual(len(ph), 3)
        m = self.doc("phan_hoi", ph[0], "meta.json")
        self.assertEqual((m["luat"], m["nguon"], m["loai"]), ("find", "tu-dong", "nghi-chay-lai"))
        with open(self.du_lieu("phan_hoi", ph[0], "goc.txt")) as f:
            self.assertEqual(f.read(), DAI)
        self.assertIn("find", self.doc("tat_bo_loc.json"))
        self.assertIsNone(self.sau("find /a -name moi"))        # bộ lọc tắt => output gốc
        self.assertIsNotNone(self.sau("ls -la /a", out="-rw-r--r-- 1 a b 1 Nov 1 01:01 tep_dai_dai_dai\n" * 200))
        self.assertIn("TỰ TẮT", self.doc("thong_bao.json")[0])

    def test_chay_lai_lenh_chua_nen_khong_ghi(self):
        self.sau("NEN_OFF=1 find /chua/tung")
        self.assertFalse(os.path.isdir(self.du_lieu("phan_hoi")))

    def test_bao_tay_hai_lan_tu_tat_khong_roi_luat_chung(self):
        goc = os.path.join(self.d, "goc.txt")
        with open(goc, "w") as f:
            f.write("".join("abc%04d dong %d\n" % (i, i) for i in range(500)))
        for _ in range(2):
            r = chay(os.path.join(S, "phan_hoi.py"), env=self.env,
                     args=["bao", "--loai", "mat-dong", "--lenh", "git log --oneline", "--goc", goc, "--mo-ta", "thiếu"])
            self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("git-log-gon", self.doc("tat_bo_loc.json"))
        sys.path.insert(0, S)
        import nen_loi
        self.assertIsNone(nen_loi.tim_luat("git log --oneline", tat={"git-log-gon"}))   # không rơi xuống luật git-log
        self.assertEqual(nen_loi.tim_luat("git log", tat={"git-log-gon"})["id"], "git-log")
        out = chay(os.path.join(S, "phan_hoi.py"), env=self.env, args=["liet-ke"]).stdout.decode()
        self.assertIn("git-log-gon", out); self.assertIn("mat-dong", out)
        ph = sorted(os.listdir(self.du_lieu("phan_hoi")))[0]
        self.assertTrue(os.path.isfile(self.du_lieu("phan_hoi", ph, "nen.txt")))

    def test_nhac_sai_khong_tat_bo_loc(self):
        for _ in range(3):
            chay(os.path.join(S, "phan_hoi.py"), env=self.env, args=["bao", "--loai", "nhac-sai", "--mo-ta", "nhắc ở 100k"])
        self.assertFalse(os.path.isfile(self.du_lieu("tat_bo_loc.json")))
        self.assertEqual(len(os.listdir(self.du_lieu("phan_hoi"))), 3)


class TestNguongGop(Goc):
    def nhat_ky(self, n):
        t = os.path.join(self.d, "p.jsonl")
        with open(t, "w") as f:
            f.write(json.dumps({"message": {"model": "m", "usage": {"input_tokens": n, "output_tokens": 1}}}) + "\n")
        return t

    def setUp(self):
        super().setUp()
        self.cau_hinh(cho_giay=0)

    def cau_hinh(self, **kw):
        os.makedirs(self.env["TINTMARK_TOKEN_DIR"], exist_ok=True)
        with open(os.path.join(self.env["TINTMARK_TOKEN_DIR"], "cau_hinh.json"), "w") as f:
            json.dump(kw, f)

    def lui_gio(self, giay=10):
        t = os.path.join(self.env["TINTMARK_TOKEN_DIR"], "trang_thai", "s1.json")
        d = json.load(open(t)); d["luc_doi"] = d.get("luc_doi", 0) - giay
        json.dump(d, open(t, "w"))

    def goi(self, su_kien="UserPromptSubmit", n=310000):
        r = chay(NGUONG, {"session_id": "s1", "transcript_path": self.nhat_ky(n), "cwd": self.d,
                          "hook_event_name": su_kien, "prompt": "làm việc X"}, self.env)
        self.assertEqual((r.returncode, r.stderr), (0, b""))
        return r.stdout.decode()

    def test_tat_module_nguong_khong_nhac_bat_lai_thi_nhac(self):
        self.env["TIETKIEM_TAT_MODULE"] = "nguong"
        self.assertNotIn("NHẮC", self.goi())
        del self.env["TIETKIEM_TAT_MODULE"]
        self.assertIn("NHẮC", self.goi())

    def test_hai_hook_trung_chi_nhac_mot_lan(self):
        self.assertIn("NHẮC", self.goi())
        self.assertEqual(self.goi(), "")                  # hook thứ hai (settings + plugin cùng nối) im lặng
        self.assertEqual(self.goi("PostToolUse"), "")
        self.assertIn("ĐỔI PHIÊN", self.goi(n=360000))

    def test_nhac_co_id_phien_va_buoc_luu_tru(self):
        a = self.goi()
        self.assertIn("Chuỗi phiên", a); self.assertIn("id phiên này: s1", a)
        self.assertIn("lưu trữ phiên cũ", a)            # lời giao thẻ kế nhiệm có bước lưu trữ
        self.assertIn('detach_session \\"self\\" TRƯỚC', a)
        b = self.goi(n=360000)
        self.assertIn("lưu trữ phiên cũ theo dòng Chuỗi phiên", b); self.assertIn("id phiên này: s1", b)
        self.assertIn('detach_session \\"self\\" TRƯỚC', b)

    def test_doi_phien_luu_tru_phien_truoc_do_giu_phien_nay(self):
        """Xung đột cũ: lời nhắc bảo lưu trữ phiên đang đầy => trái luật 2 phiên mới nhất."""
        for b in (self.goi(n=360000), self.goi("PostToolUse", n=410000)):   # nhánh tin người gõ + nhánh giữa lượt
            self.assertIn("lưu trữ phiên TRƯỚC ĐÓ nếu có", b); self.assertIn("GIỮ phiên này", b)
            self.assertNotIn("lưu trữ phiên này", b)
            self.assertIn('detach_session \\"self\\"', b)

    def bg(self, ten, chu, cong_cu="Write", **kw):
        d = os.path.join(self.d, "ban_giao_phien")
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, ten)
        with open(p, "w") as f:
            f.write(" ".join(["chữ"] * chu))
        ti = {"command": kw.get("lenh", "")} if cong_cu == "Bash" else {"file_path": kw.get("duong", p)}
        r = chay(NGUONG, {"session_id": "s2", "transcript_path": self.nhat_ky(1000), "cwd": self.d,
                          "hook_event_name": kw.get("su_kien", "PostToolUse"), "tool_name": cong_cu, "tool_input": ti}, self.env)
        self.assertEqual((r.returncode, r.stderr), (0, b""))
        return r.stdout.decode()

    def test_ban_giao_dai_thi_nhac(self):
        a = self.bg("x.md", 1600)
        self.assertIn("BÀN GIAO DÀI: x.md 1600 chữ", a); self.assertIn("≤1.500", a)
        self.assertEqual(self.bg("x.md", 1500), "")                                   # đúng ngưỡng: im
        self.assertIn("BÀN GIAO DÀI", self.bg("y.md", 1600, "Edit", duong="ban_giao_phien/y.md"))   # đường tương đối
        self.assertIn("BÀN GIAO DÀI", self.bg("z.md", 1600, "Bash", lenh="python3 - <<'EOF' > ban_giao_phien/z.md"))
        self.assertIn("BÀN GIAO DÀI", self.bg("z.md", 1600, "Bash", lenh="sed -i '' 's/a/b/' %s/ban_giao_phien/z.md" % self.d))
        self.assertEqual(self.bg("x.md", 1600, su_kien="UserPromptSubmit").count("BÀN GIAO"), 0)

    def test_ban_giao_khong_nham(self):
        self.assertEqual(self.bg("x.txt", 1600), "")                                  # không phải .md
        p = os.path.join(self.d, "khac", "x.md"); os.makedirs(os.path.dirname(p))
        self.assertEqual(self.bg("x.md", 10, duong=p), "")                            # ngoài ban_giao_phien
        self.bg("cu.md", 1600)
        t = os.path.join(self.d, "ban_giao_phien", "cu.md"); os.utime(t, (time.time() - 600,) * 2)
        r = chay(NGUONG, {"session_id": "s2", "transcript_path": self.nhat_ky(1000), "cwd": self.d, "hook_event_name": "PostToolUse",
                          "tool_name": "Bash", "tool_input": {"command": "cat ban_giao_phien/cu.md"}}, self.env)
        self.assertEqual(r.stdout, b"")                                               # chỉ đọc tệp cũ: im
        self.assertEqual(self.bg("x.md", 1600, "Read"), "")

    def test_ban_giao_nguong_va_module(self):
        self.cau_hinh(cho_giay=0, ban_giao_chu=2000)
        self.assertEqual(self.bg("x.md", 1600), "")
        self.assertIn("≤2.000", self.bg("x.md", 2100))
        self.cau_hinh(cho_giay=0, ban_giao_chu=0)
        self.assertEqual(self.bg("x.md", 9000), "")
        self.cau_hinh(cho_giay=0)
        self.env["TIETKIEM_TAT_MODULE"] = "ban_giao"
        self.assertEqual(self.bg("x.md", 9000), "")

    def test_nhac_co_the_de_xuat_mot_lan_va_cau_moi(self):
        a = self.goi()
        self.assertIn("own_initiative", a); self.assertIn("Mở phiên mới để làm việc hiệu quả hơn. Ngữ cảnh đã đưa vào phiên mới.", a)
        b = self.goi(n=310000 + 50000 - 1000)          # 359k: đã qua ngưỡng đổi
        self.assertIn("ĐỔI PHIÊN", b)
        self.assertNotIn("own_initiative", b)          # thẻ chỉ được bảo tạo một lần mỗi phiên
        self.assertIn("Ngữ cảnh đã đưa vào phiên mới", b)

    def test_qua_nguong_doi_nhac_moi_luot_nguoi_dung(self):
        a = self.goi(n=360000)
        self.assertIn("user_asked", a); self.assertIn("NGUYÊN VĂN", a); self.assertIn("phiên khác gửi", a)
        self.assertEqual(self.goi(n=360000), "")       # hook nối trùng chạy cùng lúc: chỉ một cái nói
        self.lui_gio()
        self.assertIn("user_asked", self.goi(n=361000))            # lượt người dùng kế tiếp: nhắc lại, không chờ +50k
        self.lui_gio()
        self.assertEqual(self.goi("PostToolUse", n=362000), "")    # giữa lượt (sau công cụ) thì không lặp

    def test_qua_nguong_doi_giu_tin_vai_giay_khong_chan(self):
        import time
        self.cau_hinh(cho_giay=1)
        t = time.time(); a = self.goi(n=360000); cho = time.time() - t
        self.assertIn("ĐỔI PHIÊN", a); self.assertGreaterEqual(cho, 1.0)
        self.assertNotIn('"decision"', a)              # không chặn tin
        t = time.time(); self.assertIn("NHẮC", self.goi2(n=310000)); self.assertLess(time.time() - t, 1.0)  # dưới ngưỡng đổi: không chờ
        tg = json.load(open(os.path.join(GOC, "hooks", "hooks.json")))["hooks"]["UserPromptSubmit"][0]["hooks"][0]["timeout"]
        self.assertGreaterEqual(tg, 35)                # timeout hook phải lớn hơn mức chờ tối đa 30 giây

    def goi2(self, n):
        r = chay(NGUONG, {"session_id": "s2", "transcript_path": self.nhat_ky(n), "cwd": self.d,
                          "hook_event_name": "UserPromptSubmit"}, self.env)
        return r.stdout.decode()

    def test_duoi_nguong_im_va_thong_bao_mot_lan(self):
        self.assertEqual(self.goi(n=1000), "")
        os.makedirs(self.du_lieu(), exist_ok=True)
        with open(self.du_lieu("thong_bao.json"), "w") as f:
            json.dump(["bộ lọc `find` đã TỰ TẮT"], f)
        self.assertEqual(self.goi("PostToolUse", n=1000), "")       # chỉ báo ở UserPromptSubmit
        self.assertIn("[tintmark-tietkiemtoken] bộ lọc `find`", self.goi(n=1000))
        self.assertEqual(self.goi(n=1000), "")

    def test_rac_khong_no(self):
        for inp in (b"", b"{rac", b"[]"):
            r = chay(NGUONG, inp, self.env)
            self.assertEqual((r.returncode, r.stdout), (0, b""))


class TestPhatBanCapNhat(Goc):
    """Dùng bản sao plugin với bộ test giả để không chạy lồng chính bộ test này."""

    def setUp(self):
        super().setUp()
        self.nguon = os.path.join(self.d, "nguon")
        shutil.copytree(GOC, self.nguon, ignore=shutil.ignore_patterns("tests", "mau", "__pycache__", ".DS_Store"))
        os.makedirs(os.path.join(self.nguon, "tests"))
        self.dat_test(True)
        self.kho = os.path.join(self.d, "kho")
        self.lk = os.path.join(self.d, "cai", "tintmark-tietkiemtoken")
        os.makedirs(os.path.dirname(self.lk))

    def dat_test(self, dat):
        with open(os.path.join(self.nguon, "tests", "test_gia.py"), "w") as f:
            f.write("import unittest\nclass T(unittest.TestCase):\n    def test_a(self):\n        self.assertTrue(%s)\n" % dat)

    def k(self, ten, *args):
        return chay(os.path.join(self.nguon, "scripts", ten), env=self.env, args=list(args))

    def ban(self):
        with open(os.path.join(os.path.realpath(self.lk), ".claude-plugin", "plugin.json")) as f:
            return json.load(f)["version"]

    def test_vong_doi(self):
        with open(os.path.join(self.nguon, ".claude-plugin", "plugin.json")) as f:
            b0 = json.load(f)["version"]
        # 1) test hỏng => không phát bản
        self.dat_test(False)
        r = self.k("phat_ban.py", "--ghi-chu", "x", "--kho", self.kho)
        self.assertEqual(r.returncode, 1); self.assertIn("TEST HỎNG", r.stdout.decode())
        self.assertFalse(os.path.exists(self.kho))
        # 2) phát bản đầu, cài
        self.dat_test(True)
        self.assertEqual(self.k("phat_ban.py", "--ghi-chu", "bản đầu", "--kho", self.kho).returncode, 0)
        kenh = os.path.join(self.kho, "kenh.json")
        with open(kenh) as f:
            b1 = json.load(f)["ban_moi_nhat"]
        self.assertGreater(tuple(map(int, b1.split("."))), tuple(map(int, b0.split("."))))
        os.symlink(os.path.join(self.kho, b1), self.lk)
        os.makedirs(self.du_lieu(), exist_ok=True)
        with open(self.du_lieu("cap_nhat.json"), "w") as f:
            json.dump({"kenh": kenh, "lien_ket": self.lk, "tu_dong": "ap_dung"}, f)
        self.assertIn("đã mới nhất", self.k("cap_nhat.py", "kiem").stdout.decode())
        # 3) phát bản 2 rồi cập nhật
        self.assertEqual(self.k("phat_ban.py", "--loai", "nho", "--ghi-chu", "bản hai", "--kho", self.kho).returncode, 0)
        with open(os.path.join(self.nguon, "NHAT_KY_THAY_DOI.md"), encoding="utf-8") as f:
            self.assertIn("bản hai", f.read())
        with open(kenh) as f:
            b2 = json.load(f)["ban_moi_nhat"]
        self.assertIn("CÓ BẢN MỚI", self.k("cap_nhat.py", "kiem").stdout.decode())
        r = self.k("cap_nhat.py", "ap-dung"); self.assertEqual(r.returncode, 0, r.stdout.decode())
        self.assertEqual(self.ban(), b2)
        # 4) quay lui
        r = self.k("cap_nhat.py", "quay-lui"); self.assertEqual(r.returncode, 0, r.stdout.decode())
        self.assertEqual(self.ban(), b1)
        self.k("cap_nhat.py", "tu-dong")
        self.assertEqual(self.ban(), b1, "không tự lên lại bản vừa quay lui")
        # 5) bản 3 bị sửa sau khi phát (sai băm) => từ chối
        self.assertEqual(self.k("phat_ban.py", "--ghi-chu", "bản ba", "--kho", self.kho).returncode, 0)
        with open(kenh) as f:
            b3 = json.load(f)["ban_moi_nhat"]
        with open(os.path.join(self.kho, b3, "scripts", "nen_loi.py"), "a") as f:
            f.write("\n# bị sửa\n")
        r = self.k("cap_nhat.py", "ap-dung"); self.assertEqual(r.returncode, 1); self.assertIn("SAI BĂM", r.stdout.decode())
        self.assertEqual(self.ban(), b1)
        # 6) bản có test hỏng trong kho (băm đúng) => từ chối, tự động cũng không ghi đè, có thông báo
        self.dat_test(True)
        d4 = os.path.join(self.kho, "9.0.0")
        shutil.copytree(os.path.join(self.kho, b1), d4)
        with open(os.path.join(d4, "tests", "test_gia.py"), "w") as f:
            f.write("import unittest\nclass T(unittest.TestCase):\n    def test_a(self):\n        self.fail('hỏng')\n")
        sys.path.insert(0, S)
        import cap_nhat
        with open(kenh) as f:
            kd = json.load(f)
        kd["ban"]["9.0.0"] = {"duong": "9.0.0", "sha256": cap_nhat.bam_cay(d4)}; kd["ban_moi_nhat"] = "9.0.0"
        with open(kenh, "w") as f:
            json.dump(kd, f)
        self.k("cap_nhat.py", "tu-dong")
        self.assertEqual(self.ban(), b1)
        self.assertIn("TEST HỎNG", " ".join(self.doc("thong_bao.json")))
        # 7) bản qua test nhưng hook hỏng => tự quay lui sau thử khói
        d5 = os.path.join(self.kho, "9.1.0")
        shutil.copytree(os.path.join(self.kho, b1), d5)
        with open(os.path.join(d5, "scripts", "hook_sau.py"), "w") as f:
            f.write("import sys\nsys.exit(3)\n")
        kd["ban"]["9.1.0"] = {"duong": "9.1.0", "sha256": cap_nhat.bam_cay(d5)}; kd["ban_moi_nhat"] = "9.1.0"
        with open(kenh, "w") as f:
            json.dump(kd, f)
        r = self.k("cap_nhat.py", "ap-dung"); self.assertEqual(r.returncode, 1)
        self.assertIn("TỰ QUAY LUI", r.stdout.decode()); self.assertEqual(self.ban(), b1)

    def test_kenh_tu_xa_bi_tu_choi(self):
        os.makedirs(self.du_lieu(), exist_ok=True)
        with open(self.du_lieu("cap_nhat.json"), "w") as f:
            json.dump({"kenh": "https://example.invalid/kenh.json", "lien_ket": self.lk}, f)
        r = self.k("cap_nhat.py", "ap-dung")
        self.assertEqual(r.returncode, 1); self.assertIn("chưa bật", r.stdout.decode())

    def test_gop_va_go(self):
        nha = self.env["NEN_NHA"]
        os.makedirs(os.path.join(nha, "skills", "tintmark-tietkiemtoken", "cong_cu"))
        with open(os.path.join(nha, "skills", "tintmark-tietkiemtoken", "SKILL.md"), "w") as f:
            f.write("cũ")
        lenh = "f=~/.claude/skills/tintmark-tietkiemtoken/cong_cu/nguong_token.py; [ -f $f ] && python3 $f || true"
        st = {"model": "x", "hooks": {
            "PostToolUse": [{"matcher": "ArtifactData", "hooks": [{"type": "command", "command": "khac"}]},
                            {"matcher": "", "hooks": [{"type": "command", "command": lenh}]}],
            "UserPromptSubmit": [{"hooks": [{"type": "command", "command": lenh}]}]}}
        with open(os.path.join(nha, "settings.json"), "w") as f:
            json.dump(st, f)
        r = self.k("cai_dat.py", "gop", "--lien-ket", self.nguon, "--kenh", os.path.join(self.kho, "kenh.json"))
        self.assertEqual(r.returncode, 0, r.stdout.decode() + r.stderr.decode())
        with open(os.path.join(nha, "settings.json")) as f:
            moi = json.load(f)
        self.assertEqual(moi["hooks"], {"PostToolUse": [st["hooks"]["PostToolUse"][0]]})
        self.assertEqual(moi["model"], "x")
        sk = os.path.join(nha, "skills", "tintmark-tietkiemtoken")
        self.assertTrue(os.path.islink(sk)); self.assertTrue(os.path.isfile(os.path.join(sk, "cong_cu", "nguong_token.py")))
        self.assertEqual(self.k("cai_dat.py", "go").returncode, 0)
        with open(os.path.join(nha, "settings.json")) as f:
            self.assertEqual(json.load(f), st)
        with open(os.path.join(sk, "SKILL.md")) as f:
            self.assertEqual(f.read(), "cũ")


class TestTuSua(Goc):
    def test_tai_hien_can_goc_va_giu(self):
        r = chay(os.path.join(S, "phan_hoi.py"), env=self.env, args=["bao", "--lenh", "find /a", "--mo-ta", "x"])
        ma = sorted(os.listdir(self.du_lieu("phan_hoi")))[0]
        r = chay(os.path.join(S, "tu_sua.py"), env=self.env, args=["--nguon", self.d, "tai-hien", ma, "--giu", "x"])
        self.assertEqual(r.returncode, 1); self.assertIn("không có output gốc", r.stdout.decode())
        self.assertIn(ma, chay(os.path.join(S, "tu_sua.py"), env=self.env, args=["quet"]).stdout.decode())


if __name__ == "__main__":
    unittest.main()
