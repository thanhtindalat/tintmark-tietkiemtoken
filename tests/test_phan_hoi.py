"""Ca tái hiện từ sổ phản hồi: tests/phan_hoi/<ID>/{goc.txt, ca.json}. Mỗi chuỗi `giu` phải còn sau khi nén."""
import json
import os
import sys
import unittest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "scripts"))
import nen_loi  # noqa: E402

THU_MUC = os.path.join(GOC, "tests", "phan_hoi")
DS = json.load(open(os.path.join(GOC, "luat", "luat.json"), encoding="utf-8"))["luat"]


class TestPhanHoi(unittest.TestCase):
    def test_ca_tai_hien(self):
        for ten in sorted(os.listdir(THU_MUC)) if os.path.isdir(THU_MUC) else []:
            ca_tep = os.path.join(THU_MUC, ten, "ca.json")
            if not os.path.isfile(ca_tep):
                continue
            with self.subTest(ten):
                with open(ca_tep, encoding="utf-8") as f:
                    ca = json.load(f)
                with open(os.path.join(THU_MUC, ten, "goc.txt"), encoding="utf-8") as f:
                    goc = f.read()
                luat = nen_loi.tim_luat(ca["lenh"], DS, tat=set())
                kq = goc if luat is None else nen_loi.nen_an_toan(goc, luat, ca.get("ma", 0))
                for g in ca["giu"]:
                    self.assertIn(g, kq, "%s: nén làm mất %r" % (ten, g))


if __name__ == "__main__":
    unittest.main()
