"""Kiểm SKILL.md trước khi phát bản: mô tả ≤ 320 ký tự (≤ 1024 byte cho claude.ai), mọi tệp .md được nhắc đều có thật."""
import os
import re
import unittest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THU_MUC = os.path.join(GOC, "skills", "tintmark-tietkiemtoken")


class KiemSkillMd(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(THU_MUC, "SKILL.md"), encoding="utf-8") as f:
            self.noi_dung = f.read()

    def test_mo_ta_khong_qua_1024_ky_tu(self):
        m = re.search(r"^description:\s*(.*)$", self.noi_dung, re.M)
        self.assertIsNotNone(m, "SKILL.md thiếu dòng description")
        mo_ta = m.group(1).strip().strip('"')
        self.assertLessEqual(len(mo_ta), 320, "mô tả dài %d ký tự" % len(mo_ta))
        self.assertLessEqual(len(mo_ta.encode("utf-8")), 1024, "mô tả dài %d byte" % len(mo_ta.encode("utf-8")))
        self.assertNotIn("<", mo_ta)
        self.assertNotIn(">", mo_ta)

    def test_ten_khop_thu_muc(self):
        m = re.search(r"^name:\s*(\S+)\s*$", self.noi_dung, re.M)
        self.assertEqual(m.group(1), "tintmark-tietkiemtoken")

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

    def test_ban_giao_tim_phien_con(self):
        """Lưu trữ phiên gốc: phải dò parentSessionId và biết khôi phục phiên con lỡ bị kéo theo."""
        with open(os.path.join(THU_MUC, "ban-giao.md"), encoding="utf-8") as f:
            nd = f.read()
        for chu in ("parentSessionId", "unarchive_session", "detach_session", "get_session"):
            self.assertIn(chu, nd)


if __name__ == "__main__":
    unittest.main()


class TestBanGiao(unittest.TestCase):
    def test_mau_lenh_ban_giao_co_buoc_luu_tru(self):
        s = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "skills", "tintmark-tietkiemtoken", "ban-giao.md"), encoding="utf-8").read()
        dong = [l for l in s.splitlines() if l.startswith("> LỆNH BÀN GIAO")][0]
        self.assertIn("archive_session lưu trữ mọi phiên cũ hơn 2 phiên mới nhất", dong); self.assertIn("sổ phiên", dong)
        for y in ("a hook changed this call's input", "cũ nhất", "đang ghim", "detach_session", "2 phiên mới nhất"):
            self.assertIn(y, s)
