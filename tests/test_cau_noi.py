# Copyright (c) 2026 Tintmark. All rights reserved. Xem LICENSE / NOTICE.
"""Cầu nối phê duyệt giọng nói (scripts/cau_noi.py) với thư mục Drive giả: tạo tệp, canh nền, hook báo, đánh dấu đọc."""
import json
import os
import subprocess
import sys
import threading
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_goi import NGUONG, S, Goc, chay  # noqa: E402

CN = os.path.join(S, "cau_noi.py")
CAU = "1. Phát bản mới ngay? A: có, B: chờ\n2. Gỡ skill cũ? A: gỡ, B: giữ\nCâu 3: Bật tính năng X? A: chưa\n"


class TestCauNoi(Goc):
    def setUp(self):
        super().setUp()
        self.drive = os.path.join(self.d, "Drive")
        os.makedirs(self.drive)
        self.env["CAU_NOI_DRIVE"] = self.drive
        self.da = os.path.join(self.d, "du_an")
        os.makedirs(self.da)

    def cn(self, *args, inp=None):
        r = subprocess.run([sys.executable, CN] + list(args), capture_output=True, env=self.env,
                           input=inp.encode() if inp else None, timeout=30)
        return r.returncode, r.stdout.decode(), r.stderr.decode()

    def tao(self, ten="Duyệt bản 0.7"):
        rc, out, err = self.cn("tao", "--du-an", "Skill và Token", "--ten", ten, "--tu", "-", "--cwd", self.da, inp=CAU)
        self.assertEqual((rc, err), (0, ""), out)
        return os.path.join(self.drive, "dieu_phoi", "skill_va_token", "duyet_ban_0_7.md")

    def ghi_kq(self, ten="duyet_ban_0_7", gio="20261115-1700"):
        p = os.path.join(self.drive, "dieu_phoi", "skill_va_token", "ket_qua_%s_%s.md" % (ten, gio))
        with open(p, "w", encoding="utf-8") as f:
            f.write("# KẾT QUẢ: %s\n## Trả lời\n1. Phát bản → A\n" % ten)
        return p

    def hook(self, phien="p1"):
        r = chay(NGUONG, {"hook_event_name": "UserPromptSubmit", "session_id": phien, "transcript_path": "", "cwd": self.da}, self.env)
        self.assertEqual(r.returncode, 0)
        return r.stdout.decode()

    def test_tao_co_giao_thuc_va_dem_cau(self):
        p = self.tao()
        s = open(p, encoding="utf-8").read()
        for chu in ("GIAO THỨC CHO CLAUDE", "có 3 câu", "từng câu một", "đọc lại", "6 câu", "Chỉ đạo mới",
                    "create_file", "text/markdown", "disableConversionToGoogleType", "ket_qua_duyet_ban_0_7_<YYYYMMDD-HHMM>.md",
                    "Không sửa tệp này", "1. Phát bản mới ngay?"):
            self.assertIn(chu, s)

    def test_khong_co_drive_bao_cach_sua(self):
        self.env.pop("CAU_NOI_DRIVE")
        self.env["HOME"] = self.d   # ~/Library/CloudStorage không có
        rc, out, _ = self.cn("thu-muc")
        self.assertEqual(rc, 1)
        self.assertIn("chưa đặt tài khoản", out)
        os.makedirs(self.env["NEN_DATA_DIR"], exist_ok=True)
        with open(os.path.join(self.env["NEN_DATA_DIR"], "cau_hinh.json"), "w") as f:
            json.dump({"cau_noi": {"tai_khoan": "tai_khoan_thu"}}, f)
        rc, out, _ = self.cn("thu-muc")
        self.assertEqual(rc, 1)
        self.assertIn("tai_khoan_thu", out)
        self.assertIn("app", out)
        os.makedirs(os.path.join(self.d, "Library", "CloudStorage", "GoogleDrive-tai_khoan_thu", "My Drive"))
        rc, out, _ = self.cn("thu-muc")
        self.assertEqual(rc, 0, out)
        self.assertTrue(out.strip().endswith("My Drive/dieu_phoi"))

    def test_canh_thoat_khi_co_ket_qua(self):
        self.tao()
        threading.Timer(1.5, self.ghi_kq).start()
        t = time.time()
        rc, out, _ = self.cn("canh", "--ten", "duyet_ban_0_7", "--moi", "0.5", "--het-gio", "20")
        self.assertEqual(rc, 0, out)
        self.assertIn("ket_qua_duyet_ban_0_7_20261115-1700.md", out)
        self.assertLess(time.time() - t, 15)

    def test_canh_het_gio(self):
        self.tao()
        rc, out, _ = self.cn("canh", "--ten", "duyet_ban_0_7", "--moi", "0.2", "--het-gio", "0.5")
        self.assertEqual(rc, 3)
        self.assertIn("Hết giờ", out)

    def test_ket_qua_cu_khong_tinh(self):
        self.tao()
        p = self.ghi_kq()
        cu = time.time() - 3600
        os.utime(p, (cu, cu))
        self.assertEqual(self.hook(), "")

    def test_hook_bao_mot_lan_roi_da_doc(self):
        self.tao()
        self.assertEqual(self.hook(), "")          # chưa có kết quả: im lặng
        p = self.ghi_kq()
        o = json.loads(self.hook())["hookSpecificOutput"]["additionalContext"]
        self.assertIn("CÓ KẾT QUẢ PHÊ DUYỆT", o)
        self.assertIn(p, o)
        self.assertIn("sổ hỏi đáp", o)
        self.assertEqual(self.hook(), "")          # không báo lại trong 6 giờ
        rc, out, _ = self.cn("da-doc", p)
        self.assertIn("duyet_ban_0_7", out)
        rc, out, _ = self.cn("chua-doc", "--cwd", self.da)
        self.assertIn("Không có", out)

    def test_hook_khong_bao_du_an_khac(self):
        self.tao()
        self.ghi_kq()
        khac = os.path.join(self.d, "khac")
        os.makedirs(khac)
        r = chay(NGUONG, {"hook_event_name": "UserPromptSubmit", "session_id": "p1", "transcript_path": "", "cwd": khac}, self.env)
        self.assertNotIn("PHÊ DUYỆT", r.stdout.decode())

    def test_tat_module_cau_noi(self):
        self.tao()
        self.ghi_kq()
        self.env["TIETKIEM_TAT_MODULE"] = "cau_noi"
        self.assertEqual(self.hook(), "")

    def test_ban_sao_chi_doc(self):
        tep = os.path.join(self.d, "dieu_phoi.md")
        with open(tep, "w", encoding="utf-8") as f:
            f.write("# Điều phối\n- Việc A chờ duyệt\n")
        rc, out, _ = self.cn("ban-sao", "--du-an", "Dự án Mẫu", "--tu", tep, "--cwd", self.da)
        self.assertEqual(rc, 0, out)
        p = os.path.join(self.drive, "dieu_phoi", "du_an_mau", "dieu_phoi_dieu_phoi.md")
        s = open(p, encoding="utf-8").read()
        self.assertIn("bản sao chỉ đọc", s)
        self.assertIn("Việc A chờ duyệt", s)
        self.assertIn("ket_qua_dieu_phoi_dieu_phoi_", s)


class TestLuatKeNhiem(Goc):
    """Ngưỡng: lượt người dùng gõ mở thẳng user_asked; lượt tự động nhờ điều phối, không để thẻ chờ; chống mở trùng."""

    def test_thong_diep_doi_phien(self):
        sys.path.insert(0, os.path.dirname(NGUONG))
        import nguong_token as ng
        for chu in ("list_sessions", "KHÔNG mở thêm", "user_asked", "luật thường trực", "KHÔNG tạo thẻ chờ", "SendMessage phiên điều phối",
                    "sổ hỏi đáp"):
            self.assertIn(chu, ng.THE + ng.LUOT_DAU)

    def test_tai_lieu_skill(self):
        th = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "skills", "tintmark-tietkiemtoken")
        doc = lambda t: open(os.path.join(th, t), encoding="utf-8").read()
        bg = doc("ban-giao.md")
        dong = [l for l in bg.splitlines() if l.startswith("> LỆNH BÀN GIAO")][0]
        self.assertLess(dong.index("sổ hỏi đáp"), dong.index("tệp này"))          # đọc sổ trước tệp bàn giao
        for chu in ("ghi sổ TRƯỚC, rồi mới trả lời", "Chống mở trùng", "Không tạo thẻ", "luật thường trực"):
            self.assertIn(chu, bg)
        self.assertIn("Mở hộ phiên kế nhiệm", doc("dieu-phoi.md"))
        cc = doc("claude-chat.md")
        for chu in ("đọc lại", "6 câu", "disableConversionToGoogleType", "ket_qua_", "nút micro"):
            self.assertIn(chu, cc)
        self.assertIn("phe-duyet-giong-noi.md", doc("SKILL.md"))


if __name__ == "__main__":
    unittest.main()
