#!/usr/bin/env python3
"""Tests for cli.py init (kit copy + empty specs/ folders)."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KIT = ROOT.parent.parent
sys.path.insert(0, str(ROOT))

from cli import main as cli_main  # noqa: E402
from initkit import init_kit  # noqa: E402


class InitKitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dest = Path(self.tmp.name) / "product"
        self.dest.mkdir()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_refuses_kit_root(self) -> None:
        code, notes = init_kit(KIT, KIT)
        self.assertEqual(code, 1)
        self.assertTrue(any("kit root" in n for n in notes))

    def test_copies_kit_not_kernel_specs(self) -> None:
        code, notes = init_kit(self.dest, KIT)
        self.assertEqual(code, 0, notes)
        self.assertTrue((self.dest / "specplane" / "core_prompt").is_dir())
        self.assertTrue((self.dest / ".agents" / "skills" / "specplane-implement").is_dir())
        self.assertTrue((self.dest / ".cursor" / "skills" / "specplane-implement").is_dir())
        self.assertTrue((self.dest / ".cursor" / "rules" / "specplane-core.mdc").is_file())
        self.assertTrue((self.dest / "tools" / "specplane" / "cli.py").is_file())
        self.assertTrue((self.dest / "tools" / "specplane" / "initkit.py").is_file())
        self.assertFalse((self.dest / "tools" / "specplane" / "testdata").exists())
        self.assertFalse(
            (self.dest / "specs" / "capabilities" / "capability.specplane_retrieve.yaml").exists()
        )
        for name in ("capabilities", "foundations", "containers", "components", "changes"):
            self.assertTrue((self.dest / "specs" / name).is_dir())
        yaml_caps = list((self.dest / "specs" / "capabilities").glob("*.yaml"))
        self.assertEqual(yaml_caps, [])
        self.assertFalse((self.dest / ".github" / "workflows").exists())
        config = json.loads((self.dest / "specplane.config.json").read_text(encoding="utf-8"))
        self.assertEqual(config["schemaVersion"], "9.1.0")
        self.assertIn("kitCommit", config)
        self.assertIn("SpecPlane (this product)", (self.dest / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertEqual((self.dest / "CLAUDE.md").read_text(encoding="utf-8").strip(), "@AGENTS.md")

    def test_appends_existing_agents(self) -> None:
        (self.dest / "AGENTS.md").write_text("# My app\n\nKeep this.\n", encoding="utf-8")
        code, notes = init_kit(self.dest, KIT)
        self.assertEqual(code, 0, notes)
        text = (self.dest / "AGENTS.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# My app"))
        self.assertIn("Keep this.", text)
        self.assertIn("SpecPlane (this product)", text)

    def test_does_not_replace_existing_specplane_without_force(self) -> None:
        (self.dest / "specplane").mkdir()
        (self.dest / "specplane" / "marker.txt").write_text("mine", encoding="utf-8")
        code, notes = init_kit(self.dest, KIT)
        self.assertEqual(code, 1)
        self.assertTrue((self.dest / "specplane" / "marker.txt").is_file())
        self.assertTrue(any("--force" in n for n in notes))

    def test_kit_only_skips_cli(self) -> None:
        code, notes = init_kit(self.dest, KIT, with_cli=False)
        self.assertEqual(code, 0, notes)
        self.assertTrue((self.dest / "specplane").is_dir())
        self.assertFalse((self.dest / "tools" / "specplane" / "cli.py").exists())

    def test_cli_init_dest(self) -> None:
        code = cli_main(["init", "--dest", str(self.dest), "--kit-root", str(KIT)])
        self.assertEqual(code, 0)
        self.assertTrue((self.dest / "specplane").is_dir())


if __name__ == "__main__":
    unittest.main()
