# Copyright (c) 2026 Tintmark. All rights reserved. Xem LICENSE / NOTICE.
"""Bật / tắt module (khung): tắt `nen` thì hook nén im, tắt `nguong` thì hook ngưỡng không nhắc; lệnh không bị chặn."""
import json
import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_goi import DAI, NGUONG, Goc, chay  # noqa: E402


class TestModuleHook(Goc):
    def test_tat_nen_qua_bien_va_cau_hinh(self):
        self.assertIsNotNone(self.sau("find . -name x"))
        self.env["TIETKIEM_TAT_MODULE"] = "nen"
        self.assertIsNone(self.sau("find . -name x"))
        del self.env["TIETKIEM_TAT_MODULE"]
        r = subprocess.run([sys.executable, os.path.join(os.path.dirname(NGUONG), "..", "..", "..", "scripts", "module.py"),
                            "tat", "nen"], capture_output=True, env=self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIsNone(self.sau("find . -name x"))

    def test_tat_nen_rieng_du_an(self):
        da = os.path.join(self.d, "du_an")
        os.makedirs(os.path.join(da, ".claude"))
        with open(os.path.join(da, ".claude", "tintmark-tietkiemtoken.json"), "w") as f:
            json.dump({"module": {"nen": False}}, f)
        d = {"tool_name": "Bash", "session_id": "p1", "hook_event_name": "PostToolUse", "cwd": da,
             "tool_input": {"command": "find . -name x"},
             "tool_response": {"stdout": DAI, "stderr": "", "interrupted": False, "isImage": False}}
        r = chay(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "hook_sau.py"), d, self.env)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, b"", b""))


if __name__ == "__main__":
    unittest.main()
