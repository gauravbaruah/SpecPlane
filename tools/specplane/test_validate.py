#!/usr/bin/env python3
"""Smoke tests for the SpecPlane validator."""

from __future__ import annotations

import sys
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


if __name__ == "__main__":
    unittest.main()
