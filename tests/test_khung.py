# Copyright (c) 2026 Tintmark. All rights reserved. Xem LICENSE / NOTICE.
"""Test chung của khung plugin bản quyền (chép nguyên vào tests/ của mỗi plugin, KHÔNG sửa tại plugin).

Kiểm: tệp bản quyền, khai báo plugin / khung / module / hội viên, bật tắt module, cơ chế hội viên mặc định tắt và fail-open.
"""
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(GOC, "scripts")
sys.path.insert(0, S)
import khung_chung as kc  # noqa: E402
import hoi_vien  # noqa: E402
import module  # noqa: E402

BIEN = (kc.khung().get("du_lieu") or {}).get("bien")


class GocKhung(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.cu = {k: os.environ.get(k) for k in (BIEN, kc.khung().get("bien_tat_module")) if k}
        if BIEN:
            os.environ[BIEN] = os.path.join(self.d, "du_lieu")
        b = kc.khung().get("bien_tat_module")
        if b:
            os.environ.pop(b, None)

    def tearDown(self):
        for k, v in self.cu.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(self.d, ignore_errors=True)


class TestBanQuyen(unittest.TestCase):
    def test_tep_bat_buoc(self):
        for t in ("LICENSE", "NOTICE", "README.md", ".claude-plugin/plugin.json", ".claude-plugin/khung.json",
                  ".claude-plugin/module.json", ".claude-plugin/hoi_vien.json"):
            self.assertTrue(os.path.isfile(os.path.join(GOC, t)), t)
        with open(os.path.join(GOC, "LICENSE"), encoding="utf-8") as f:
            self.assertIn("Copyright (c)", f.read())

    def test_dong_ban_quyen_moi_tep_ma(self):
        thieu = []
        for goc, con, tep in os.walk(GOC):
            con[:] = [c for c in con if c not in ("__pycache__", ".git", "mau")]
            for t in tep:
                if t.endswith((".py", ".sh")):
                    with open(os.path.join(goc, t), encoding="utf-8") as f:
                        dau = "".join(f.readline() for _ in range(3))
                    if "Copyright (c)" not in dau:
                        thieu.append(os.path.relpath(os.path.join(goc, t), GOC))
        self.assertEqual(thieu, [])

    def test_plugin_json(self):
        p = kc.plugin_json()
        self.assertTrue(re.fullmatch(r"[a-z0-9][a-z0-9-]*", p.get("name", "")))
        self.assertTrue(re.fullmatch(r"\d+\.\d+\.\d+", p.get("version", "")))
        self.assertEqual(p.get("license"), "SEE LICENSE IN LICENSE")
        self.assertEqual(kc.ten(), p["name"])

    def test_khai_bao_module(self):
        ds = module.danh_sach()
        self.assertTrue(ds)
        for mid, tt in ds.items():
            self.assertTrue(re.fullmatch(r"[a-z0-9_]+", mid), mid)
            self.assertIn("mo_ta", tt)
            for t in tt.get("tep") or []:
                self.assertTrue(os.path.exists(os.path.join(GOC, t)), "%s: thiếu %s" % (mid, t))


class TestModule(GocKhung):
    def test_mac_dinh_va_ghi_de(self):
        ds = module.danh_sach()
        mid = next(m for m, t in ds.items() if not t.get("hoi_vien"))
        self.assertEqual(module.bat(mid), bool(ds[mid].get("mac_dinh", True)))
        module.dat(mid, False)
        self.assertFalse(module.bat(mid))
        self.assertEqual(module.trang_thai()[mid][1], "cấu hình máy")
        # dự án bật lại riêng một thư mục
        da = os.path.join(self.d, "du_an", "con")
        os.makedirs(os.path.join(self.d, "du_an", ".claude"))
        os.makedirs(da)
        with open(os.path.join(self.d, "du_an", ".claude", kc.ten() + ".json"), "w") as f:
            json.dump({"module": {mid: True}}, f)
        self.assertTrue(module.bat(mid, da))
        b = kc.khung().get("bien_tat_module")
        if b:
            os.environ[b] = "x," + mid
            self.assertFalse(module.bat(mid, da))
        self.assertTrue(module.bat("khong_co_module_nay"))

    def test_cau_hinh_hong_khong_no(self):
        os.makedirs(kc.thu_muc_du_lieu(), exist_ok=True)
        with open(kc.tep("cau_hinh.json"), "w") as f:
            f.write("{hỏng")
        for mid in module.danh_sach():
            module.bat(mid)   # không ném lỗi

    def test_dong_lenh(self):
        mid = next(iter(module.danh_sach()))
        env = dict(os.environ)
        r = subprocess.run([sys.executable, os.path.join(S, "module.py"), "tat", mid], capture_output=True, env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        r = subprocess.run([sys.executable, os.path.join(S, "module.py"), "ds"], capture_output=True, env=env)
        self.assertIn("TẮT", r.stdout.decode())
        r = subprocess.run([sys.executable, os.path.join(S, "module.py"), "tat", "khong_co"], capture_output=True, env=env)
        self.assertEqual(r.returncode, 1)

    def test_thu_khoi_khong_ghi_du_lieu_that(self):
        """Thử khói một thư mục plugin chỉ dùng dữ liệu tạm: không tạo / ghi gì trong HOME (sổ thống kê thật)."""
        nha = os.path.join(self.d, "nha")
        os.makedirs(nha)
        env = dict(os.environ, HOME=nha)
        for b in ((kc.khung().get("test") or {}).get("bien_tam") or []) + [BIEN]:
            if b:
                env.pop(b, None)
        r = subprocess.run([sys.executable, os.path.join(S, "cap_nhat.py"), "thu-khoi", GOC], capture_output=True, env=env,
                           timeout=60)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        con = [os.path.join(g, t) for g, _, ts in os.walk(nha) for t in ts]
        self.assertEqual(con, [])


def _khoa(nd, ck=b"chu-ky-dung"):
    return {"noi_dung": base64.b64encode(json.dumps(nd).encode()).decode(), "chu_ky": base64.b64encode(ck).decode()}


class TestHoiVien(GocKhung):
    """Thuật toán thật chưa chọn: dùng thuật toán giả chỉ trong test."""

    def setUp(self):
        super().setUp()
        hoi_vien.XAC_MINH["gia"] = lambda nd, ck, kcc: ck == b"chu-ky-dung"
        self.c = {"bat": True, "thuat_toan": "gia", "khoa_cong_khai": None, "tep_khoa": "k.json", "lien_he": ""}
        self.nd = {"plugin": kc.ten(), "nguoi": "a", "goi": ["hv"], "cap": "2026-01-01", "het_han": "2999-01-01"}

    def tearDown(self):
        hoi_vien.XAC_MINH.pop("gia", None)
        super().tearDown()

    def test_mac_dinh_tat_moi_module_chay(self):
        self.assertFalse(hoi_vien.cau_hinh()["bat"], "bản phát hành phải để cơ chế hội viên TẮT")
        self.assertTrue(hoi_vien.duoc_dung("bat_ky"))

    def test_khoa_hop_le_het_han_sai(self):
        tt = hoi_vien.trang_thai(self.c, _khoa(self.nd))
        self.assertTrue(tt["hop_le"]); self.assertTrue(hoi_vien.duoc_dung("hv", tt))
        self.assertFalse(hoi_vien.duoc_dung("khac", tt))
        self.assertFalse(hoi_vien.trang_thai(self.c, _khoa(self.nd, b"sai"))["hop_le"])
        self.assertFalse(hoi_vien.trang_thai(self.c, _khoa(dict(self.nd, het_han="2000-01-01")))["hop_le"])
        self.assertFalse(hoi_vien.trang_thai(self.c, _khoa(dict(self.nd, plugin="khac")))["hop_le"])
        self.assertFalse(hoi_vien.trang_thai(self.c, {"noi_dung": "%%%", "chu_ky": ""})["hop_le"])
        self.assertFalse(hoi_vien.trang_thai(self.c, None)["hop_le"])
        self.assertFalse(hoi_vien.duoc_dung("hv", hoi_vien.trang_thai(self.c, None)))

    def test_chua_chon_thuat_toan(self):
        tt = hoi_vien.trang_thai(dict(self.c, thuat_toan=None), _khoa(self.nd))
        self.assertFalse(tt["hop_le"]); self.assertIn("thuật toán", tt["ly_do"])

    def test_loi_ma_kiem_thi_cho_chay(self):
        def no(*a):
            raise ValueError("lỗi")
        hoi_vien.XAC_MINH["gia"] = no
        self.assertTrue(hoi_vien.duoc_dung("hv", {"bat": True, "hop_le": True, "goi": None}))   # goi hỏng => ngoại lệ => cho chạy

    def test_module_hoi_vien_chi_tat_khi_khoa_sai(self):
        ds = {"thuong": {"mo_ta": "t"}, "hv": {"mo_ta": "h", "hoi_vien": True}}
        goc = module.danh_sach
        module.danh_sach = lambda: ds
        try:
            tt_sai = hoi_vien.trang_thai(self.c, None)
            kq = module.trang_thai(None, tt_sai)
            self.assertEqual((kq["thuong"][0], kq["hv"][0]), (True, False))
            kq = module.trang_thai(None, hoi_vien.trang_thai(self.c, _khoa(self.nd)))
            self.assertEqual((kq["thuong"][0], kq["hv"][0]), (True, True))
        finally:
            module.danh_sach = goc


class TestEd25519(GocKhung):
    """Thuật toán thật (chọn 15/11): vector RFC 8032 + khoá mẫu ký bằng khoá bí mật CÔNG KHAI của RFC (chỉ để test)."""
    RFC = [("d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a", "",
            "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"),
           ("3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c", "72",
            "92a009a9f0d4cab8720e820b5f642540a2b27b5416503f8fb3762223ebdb69da085ac1e43e15996e458f3613d0f11d8c387b2eaeb4302aeeb00d291612bb0c00")]
    CONG_KHAI = "11qYAYKxCrfVS/7TyWQHOg7hcvPapiMlrwIaaPcHURo="
    HOP_LE = {"noi_dung": "eyJwbHVnaW4iOiJwbHVnaW4tdGh1Iiwibmd1b2kiOiJ0ZXN0IiwiZ29pIjpbImh2Il0sImNhcCI6IjIwMjYtMTEtMTUiLCJoZXRfaGFuIjoiMjk5OS0wMS0wMSJ9",
              "chu_ky": "kOTeNKEc4VNAwJkQLztqbxX2o7QiVMT1U7u2lmfq2WqZlczhomJL+D/66sSTcXwn8kHg4uLiJzBNZ7A1LGpABg=="}
    HET_HAN = {"noi_dung": "eyJwbHVnaW4iOiJwbHVnaW4tdGh1Iiwibmd1b2kiOiJ0ZXN0IiwiZ29pIjpbImh2Il0sImNhcCI6IjIwMjYtMTEtMTUiLCJoZXRfaGFuIjoiMjAwMC0wMS0wMSJ9",
               "chu_ky": "fFpzUBRXn6R5axxo0Erj6C+TCqwVZXio6i9DA9oMbbIZr7HqcB5IJPzyrZmnCCXE6XSlKNqeOuXX9fPA07tkDw=="}
    PLUGIN_KHAC = {"noi_dung": "eyJwbHVnaW4iOiJraGFjIiwibmd1b2kiOiJ0ZXN0IiwiZ29pIjpbImh2Il0sImNhcCI6IjIwMjYtMTEtMTUiLCJoZXRfaGFuIjoiMjk5OS0wMS0wMSJ9",
                   "chu_ky": "9Z8EdlfdzQgjpICIchGVj8VPOTTsj0WOw1+QGEtlnyz99YiUbEvLb2A9m+dqQAvmRDyNJ5M8Xs0SxhumwUPPBQ=="}

    def setUp(self):
        super().setUp()
        self.ten_goc = hoi_vien.kc.ten
        hoi_vien.kc.ten = lambda *a: "plugin-thu"
        self.c = {"bat": True, "thuat_toan": "ed25519", "khoa_cong_khai": self.CONG_KHAI, "tep_khoa": "k.json", "lien_he": ""}

    def tearDown(self):
        hoi_vien.kc.ten = self.ten_goc
        super().tearDown()

    def test_vector_rfc8032(self):
        for ck, td, cky in self.RFC:
            ck, td, cky = bytes.fromhex(ck), bytes.fromhex(td), bytes.fromhex(cky)
            self.assertTrue(hoi_vien.ed25519_xac_minh(ck, td, cky))
            self.assertFalse(hoi_vien.ed25519_xac_minh(ck, td + b"x", cky))
            self.assertFalse(hoi_vien.ed25519_xac_minh(ck, td, cky[:-1] + bytes([cky[-1] ^ 1])))
            self.assertFalse(hoi_vien.ed25519_xac_minh(ck, td, cky[:32] + (2 ** 253).to_bytes(32, "little")))  # s >= q
            self.assertFalse(hoi_vien.ed25519_xac_minh(ck[:31], td, cky))

    def test_khoa_that(self):
        tt = hoi_vien.trang_thai(self.c, self.HOP_LE)
        self.assertTrue(tt["hop_le"], tt["ly_do"]); self.assertTrue(hoi_vien.duoc_dung("hv", tt))
        self.assertFalse(hoi_vien.duoc_dung("khac", tt))
        self.assertIn("hết hạn", hoi_vien.trang_thai(self.c, self.HET_HAN)["ly_do"])
        self.assertIn("plugin khác", hoi_vien.trang_thai(self.c, self.PLUGIN_KHAC)["ly_do"])
        sua = dict(self.HOP_LE, noi_dung=self.HET_HAN["noi_dung"])     # đổi nội dung, giữ chữ ký => sai
        self.assertEqual(hoi_vien.trang_thai(self.c, sua)["ly_do"], "chữ ký sai")
        for ck in (None, "", "%%%", "AAAA"):
            self.assertFalse(hoi_vien.trang_thai(dict(self.c, khoa_cong_khai=ck), self.HOP_LE)["hop_le"])

    def test_ban_phat_hanh_van_tat(self):
        c = hoi_vien.cau_hinh()
        self.assertFalse(c["bat"])
        if c.get("thuat_toan"):
            self.assertIn(c["thuat_toan"], hoi_vien.XAC_MINH)


if __name__ == "__main__":
    unittest.main()
