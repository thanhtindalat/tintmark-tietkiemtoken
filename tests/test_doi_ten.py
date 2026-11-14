"""Đổi tên nen-token -> tintmark-tietkiem: dữ liệu không mất, quay lui được."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DT = os.path.join(GOC, "scripts", "doi_ten.py")


class TestDoiTen(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.nha = os.path.join(self.d, "nha")
        cu = os.path.join(self.nha, "plugin-nen-token")
        os.makedirs(os.path.join(cu, "phan_hoi", "p1"))
        open(os.path.join(cu, "thong_ke.jsonl"), "w").write('{"x":1}\n')
        self.mk = os.path.join(self.d, "mk")
        os.makedirs(os.path.join(self.mk, ".claude-plugin"))
        json.dump({"plugins": [{"name": "nen-token", "source": "./nen-token"}]}, open(os.path.join(self.mk, ".claude-plugin", "marketplace.json"), "w"))
        self.bancu = os.path.join(self.d, "kho", "nen-token", "0.2.7")
        os.makedirs(os.path.join(self.bancu, "skills", "tintmark-token"))
        os.symlink(self.bancu, os.path.join(self.mk, "nen-token"))
        self.kho = os.path.join(self.d, "kho", "tintmark-tietkiem")
        os.makedirs(self.kho)
        json.dump({"ban": {}}, open(os.path.join(self.kho, "kenh.json"), "w"))
        json.dump({"kenh": "a/kenh.json", "lien_ket": os.path.join(self.mk, "nen-token")}, open(os.path.join(cu, "cap_nhat.json"), "w"))
        os.makedirs(os.path.join(self.nha, "skills"))
        os.symlink(os.path.join(self.mk, "nen-token", "skills", "tintmark-token"), os.path.join(self.nha, "skills", "tintmark-token"))

    def chay(self, *a):
        env = dict(os.environ, NEN_NHA=self.nha)
        r = subprocess.run([sys.executable, DT] + list(a) + ["--marketplace", self.mk], env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r.stdout

    def test_lam_va_quay_lui(self):
        self.chay("lam", "--kho", self.kho)
        moi = os.path.join(self.nha, "plugin-tintmark-tietkiem")
        cu = os.path.join(self.nha, "plugin-nen-token")
        self.assertTrue(os.path.isfile(os.path.join(moi, "thong_ke.jsonl")))
        self.assertTrue(os.path.islink(cu))
        self.assertTrue(os.path.isdir(os.path.join(cu, "phan_hoi", "p1")))   # bản cũ vẫn đọc được
        c = json.load(open(os.path.join(moi, "cap_nhat.json")))
        self.assertEqual(c["lien_ket"], os.path.join(self.mk, "tintmark-tietkiem"))
        self.assertEqual(os.path.realpath(os.path.join(self.mk, "tintmark-tietkiem")), os.path.realpath(self.bancu))
        m = json.load(open(os.path.join(self.mk, ".claude-plugin", "marketplace.json")))
        self.assertEqual([x["name"] for x in m["plugins"]], ["nen-token", "tintmark-tietkiem"])
        self.assertIn("tintmark-tietkiem", os.readlink(os.path.join(self.nha, "skills", "tintmark-token")))
        self.chay("lam", "--kho", self.kho)   # chạy lại không hỏng
        self.chay("quay-lui")
        self.assertFalse(os.path.islink(cu))
        self.assertTrue(os.path.isfile(os.path.join(cu, "thong_ke.jsonl")))
        self.assertFalse(os.path.exists(moi))
        c = json.load(open(os.path.join(cu, "cap_nhat.json")))
        self.assertEqual(c["lien_ket"], os.path.join(self.mk, "nen-token"))
        self.assertIn("nen-token", os.readlink(os.path.join(self.nha, "skills", "tintmark-token")))


if __name__ == "__main__":
    unittest.main()
