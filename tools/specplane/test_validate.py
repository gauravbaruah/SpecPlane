#!/usr/bin/env python3
"""Smoke tests for the SpecPlane validator."""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from validate import validate  # noqa: E402


class ValidateFixtures(unittest.TestCase):
    def test_valid_tree_has_no_errors(self) -> None:
        report = validate(ROOT / "testdata" / "valid" / "specs")
        self.assertEqual(
            [f.format() for f in report.errors],
            [],
        )
        self.assertGreaterEqual(report.file_count, 5)

    def test_invalid_tree_reports_errors(self) -> None:
        report = validate(ROOT / "testdata" / "invalid" / "specs")
        rules = {f.rule for f in report.errors}
        self.assertIn("1", rules)
        self.assertIn("9", rules)
        self.assertIn("10", rules)
        self.assertIn("12", rules)

    def test_flow_mapping_requires_id_and_goal_is_optional(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "specs"
            shutil.copytree(ROOT / "testdata" / "valid" / "specs", root)
            cap = root / "capabilities" / "capability.authentication.yaml"
            text = cap.read_text(encoding="utf-8")
            broken = text.replace('  - "Login"\n', '  - goal: "Sign in"\n', 1)
            cap.write_text(broken, encoding="utf-8")
            report = validate(root)
            messages = [f.message for f in report.errors if f.rule == "22"]
            self.assertTrue(any("requires a non-empty id" in m for m in messages), messages)

            named = text.replace('  - "Login"\n', "  - id: login\n", 1)
            cap.write_text(named, encoding="utf-8")
            report = validate(root)
            self.assertEqual([f.format() for f in report.errors if f.rule == "22"], [])
            self.assertEqual([f.format() for f in report.errors], [])


if __name__ == "__main__":
    unittest.main()
