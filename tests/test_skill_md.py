"""Kiểm SKILL.md trước khi phát bản: mô tả ≤ 1024 ký tự, mọi tệp .md được nhắc đều có thật."""
import os
import re
import unittest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THU_MUC = os.path.join(GOC, "skills", "tintmark-token")


class KiemSkillMd(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(THU_MUC, "SKILL.md"), encoding="utf-8") as f:
            self.noi_dung = f.read()

    def test_mo_ta_khong_qua_1024_ky_tu(self):
        m = re.search(r"^description:\s*(.*)$", self.noi_dung, re.M)
        self.assertIsNotNone(m, "SKILL.md thiếu dòng description")
        mo_ta = m.group(1).strip().strip('"')
        self.assertLessEqual(len(mo_ta), 1024, "mô tả dài %d ký tự" % len(mo_ta))
        self.assertNotIn("<", mo_ta)
        self.assertNotIn(">", mo_ta)

    def test_ten_khop_thu_muc(self):
        m = re.search(r"^name:\s*(\S+)\s*$", self.noi_dung, re.M)
        self.assertEqual(m.group(1), "tintmark-token")

    def test_tep_duoc_nhac_deu_co(self):
        for thu_muc, _, tep in os.walk(THU_MUC):
            for t in tep:
                if not t.endswith(".md"):
                    continue
                with open(os.path.join(thu_muc, t), encoding="utf-8") as f:
                    nd = f.read()
                for ten in set(re.findall(r"`([a-z0-9-]+\.md)`", nd)):
                    self.assertTrue(os.path.exists(os.path.join(THU_MUC, ten)),
                                    "%s nhắc %s nhưng không có tệp" % (t, ten))


if __name__ == "__main__":
    unittest.main()
