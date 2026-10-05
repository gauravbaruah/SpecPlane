#!/usr/bin/env python3
"""Tests for cli.py init (kit copy + empty specs/ folders)."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KIT = ROOT.parent.parent
sys.path.insert(0, str(ROOT))

os.environ.setdefault("SPECPLANE_TELEMETRY", "0")

from cli import main as cli_main  # noqa: E402
from initkit import default_kit_root, init_kit, uninstall_kit  # noqa: E402
from telemetry import VERSION  # noqa: E402


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
        self.assertTrue((self.dest / "tools" / "specplane" / "view.py").is_file())
        self.assertTrue((self.dest / "tools" / "specplane" / "telemetry.py").is_file())
        self.assertTrue((self.dest / "tools" / "specplane" / "ci_gate.py").is_file())
        self.assertTrue((self.dest / "tools" / "specplane" / "viewer" / "app.js").is_file())
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
        ignore = (self.dest / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("**/.specplane/view/", ignore)
        self.assertNotIn(".specplane/\n", ignore)
        self.assertNotIn(".specplane/**", ignore)
        config = json.loads((self.dest / "specplane.config.json").read_text(encoding="utf-8"))
        self.assertEqual(config["schemaVersion"], "9.1.0")
        self.assertIn("kitCommit", config)
        agents = (self.dest / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("SpecPlane (this product)", agents)
        self.assertIn("specplane-infer", agents)
        self.assertIn("Brownfield", agents)
        self.assertIn("promote --ids", agents)
        self.assertEqual((self.dest / "CLAUDE.md").read_text(encoding="utf-8").strip(), "@AGENTS.md")

    def test_appends_existing_agents(self) -> None:
        (self.dest / "AGENTS.md").write_text("# My app\n\nKeep this.\n", encoding="utf-8")
        code, notes = init_kit(self.dest, KIT)
        self.assertEqual(code, 0, notes)
        text = (self.dest / "AGENTS.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# My app"))
        self.assertIn("Keep this.", text)
        self.assertIn("SpecPlane (this product)", text)

    def test_force_replaces_kit_keeps_specs_and_clears_view(self) -> None:
        code, notes = init_kit(self.dest, KIT)
        self.assertEqual(code, 0, notes)
        kept = self.dest / "specs" / "capabilities" / "capability.mine.yaml"
        kept.write_text("meta: {id: capability.mine}\n", encoding="utf-8")
        other = self.dest / ".specplane" / "notes.txt"
        other.parent.mkdir(parents=True)
        other.write_text("keep\n", encoding="utf-8")
        generated = self.dest / ".specplane" / "view" / "payload.js"
        generated.parent.mkdir()
        generated.write_text("stale\n", encoding="utf-8")
        stale_skill = self.dest / ".agents" / "skills" / "specplane-retired"
        stale_skill.mkdir()
        (stale_skill / "SKILL.md").write_text("old\n", encoding="utf-8")
        stale_cli = self.dest / "tools" / "specplane" / "old_kit.py"
        stale_cli.write_text("old\n", encoding="utf-8")
        (self.dest / "specplane" / "retired.txt").write_text("old\n", encoding="utf-8")

        code, notes = init_kit(self.dest, KIT, force=True)
        self.assertEqual(code, 0, notes)
        self.assertTrue(kept.is_file())
        self.assertEqual(kept.read_text(encoding="utf-8"), "meta: {id: capability.mine}\n")
        self.assertTrue(other.is_file())
        self.assertFalse(generated.exists())
        self.assertFalse(stale_skill.exists())
        self.assertFalse(stale_cli.exists())
        self.assertFalse((self.dest / "specplane" / "retired.txt").exists())
        self.assertTrue((self.dest / "tools" / "specplane" / "viewer" / "app.js").is_file())
        self.assertTrue(any("next specplane view" in note for note in notes))
        self.assertIn("SpecPlane (this product)", (self.dest / "AGENTS.md").read_text(encoding="utf-8"))

    def test_partial_copy_names_what_to_delete(self) -> None:
        kept = self.dest / "specs" / "capabilities" / "capability.mine.yaml"
        kept.parent.mkdir(parents=True)
        kept.write_text("meta: {id: capability.mine}\n", encoding="utf-8")
        skills = self.dest / ".agents" / "skills"
        skills.parent.mkdir()
        skills.write_text("not a directory\n", encoding="utf-8")
        code, notes = init_kit(self.dest, KIT)
        self.assertEqual(code, 1, notes)
        text = "\n".join(notes)
        self.assertIn("Something went wrong", text)
        self.assertIn("specplane/", text)
        self.assertIn("tools/specplane/", text)
        self.assertIn("Leave specs/ alone", text)
        self.assertTrue((self.dest / "specplane").is_dir())
        self.assertEqual(kept.read_text(encoding="utf-8"), "meta: {id: capability.mine}\n")

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
        self.assertFalse((self.dest / "tools" / "specplane" / "view.py").exists())

    def test_cli_init_dest(self) -> None:
        code = cli_main(["init", "--dest", str(self.dest), "--kit-root", str(KIT)])
        self.assertEqual(code, 0)
        self.assertTrue((self.dest / "specplane").is_dir())

    def test_init_from_bundled_layout(self) -> None:
        sys.path.insert(0, str(KIT / "packaging"))
        from bundle_kit import populate_bundle

        bundle = Path(self.tmp.name) / "wheel_kit"
        populate_bundle(dest=bundle)
        dest = Path(self.tmp.name) / "from_bundle"
        dest.mkdir()
        code, notes = init_kit(dest, bundle)
        self.assertEqual(code, 0, notes)
        self.assertTrue((dest / "specplane" / "core_prompt").is_dir())
        self.assertTrue((dest / ".agents" / "skills" / "specplane-implement").is_dir())
        self.assertFalse(
            (dest / "specs" / "capabilities" / "capability.specplane_retrieve.yaml").exists()
        )

    def test_default_kit_root_prefers_checkout(self) -> None:
        self.assertEqual(default_kit_root().resolve(), KIT.resolve())

    @unittest.skipUnless(
        importlib.util.find_spec("setuptools") is not None,
        "editable metadata test needs setuptools (dev extra)",
    )
    def test_editable_metadata_without_prebuilt_bundle(self) -> None:
        import os
        import shutil

        sys.path.insert(0, str(KIT / "packaging"))
        from bundle_kit import BUNDLE
        from build_backend import prepare_metadata_for_build_editable

        stub_text = "# bundled kit root for wheel installs\n"
        if BUNDLE.exists():
            shutil.rmtree(BUNDLE)
        old_cwd = Path.cwd()
        try:
            os.chdir(KIT)
            with tempfile.TemporaryDirectory() as meta:
                prepare_metadata_for_build_editable(meta)
            self.assertTrue((BUNDLE / "__init__.py").is_file())
        finally:
            os.chdir(old_cwd)
            BUNDLE.mkdir(parents=True, exist_ok=True)
            (BUNDLE / "__init__.py").write_text(stub_text, encoding="utf-8")


class InitJourneyTests(unittest.TestCase):
    def test_live_init_has_one_journey(self) -> None:
        loaded = yaml_load(KIT / "specs" / "capabilities" / "capability.specplane_init.yaml")
        flows = loaded["flows"]
        mappings = [item for item in flows if isinstance(item, dict)]
        strings = [item for item in flows if isinstance(item, str)]
        self.assertEqual(len(mappings), 1)
        self.assertEqual(mappings[0]["id"], "init_product_repo")
        self.assertGreaterEqual(len(strings), 2)

    def test_uninstall_leaves_specs_and_removes_the_kit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "product"
            dest.mkdir()
            code, notes = init_kit(dest, KIT)
            self.assertEqual(code, 0, notes)
            kept = dest / "specs" / "capabilities" / "capability.mine.yaml"
            kept.write_text("mine: true\n", encoding="utf-8")
            (dest / "tools" / "other.txt").write_text("keep\n", encoding="utf-8")
            code, notes = uninstall_kit(dest)
            self.assertEqual(code, 0, notes)
            self.assertFalse((dest / "specplane").exists())
            self.assertFalse((dest / "tools" / "specplane").exists())
            self.assertFalse((dest / "specplane.config.json").exists())
            self.assertFalse((dest / ".agents" / "skills" / "specplane-implement").exists())
            self.assertEqual(kept.read_text(encoding="utf-8"), "mine: true\n")
            self.assertEqual((dest / "tools" / "other.txt").read_text(encoding="utf-8"), "keep\n")
            self.assertIn("left specs/ in place", notes)
            self.assertIn("left the specplane command installed", notes)

    def test_uninstall_refuses_this_checkout(self) -> None:
        code, notes = uninstall_kit(KIT)
        self.assertEqual(code, 1, notes)
        self.assertTrue((KIT / "specplane" / "core_prompt").is_dir())

    def test_first_publish_is_a_prerelease(self) -> None:
        text = (KIT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('version = "0.1.0a1"', text)
        self.assertEqual(VERSION, "0.1.0a1")

    def test_package_has_four_flows_and_diagrams(self) -> None:
        loaded = yaml_load(KIT / "specs" / "capabilities" / "capability.specplane_package.yaml")
        flows = [item for item in loaded["flows"] if isinstance(item, dict)]
        titles = [item["title"] for item in loaded["diagrams"]]
        self.assertEqual(len(flows), 4)
        self.assertEqual(len(titles), 4)
        named = " ".join(titles).lower()
        for needle in ("publish", "install from the index", "init from the installed", "install from a checkout"):
            self.assertIn(needle, named)

    def test_install_does_not_consent_or_configure_a_host(self) -> None:
        init_text = (KIT / "tools" / "specplane" / "initkit.py").read_text(encoding="utf-8").lower()
        self.assertNotIn("consent", init_text)
        self.assertNotIn("mcp.json", init_text)
        self.assertNotIn("urllib", init_text)
        self.assertNotIn("mailto:", init_text)

    def test_post_surfaces_remind_to_bind(self) -> None:
        reminder = (
            "If this change already has a check, bind it (`run.unittest` or `run.argv`). "
            "Do not invent a test so SpecPlane has something to run. "
            "Do not parse `test_strategy`. "
            "Unbound `must:` is `not_run` on `run`, not a pass and not a certificate."
        )
        surfaces = (
            "tools/specplane/initkit.py",
            ".cursor/skills/specplane-implement/SKILL.md",
            ".agents/skills/specplane-implement/SKILL.md",
            "AGENTS.md",
            ".cursor/rules/specplane-core.mdc",
            "docs/golden-journey.md",
            "docs/use-in-your-project.md",
        )
        cursor = (KIT / ".cursor/skills/specplane-implement/SKILL.md").read_text(encoding="utf-8")
        agents = (KIT / ".agents/skills/specplane-implement/SKILL.md").read_text(encoding="utf-8")
        self.assertEqual(cursor, agents)
        self.assertIn("`must:` lines are enough", cursor)
        journey = (KIT / "docs/golden-journey.md").read_text(encoding="utf-8")
        self.assertNotIn("Add tests that match", journey)
        initkit = (KIT / "tools/specplane/initkit.py").read_text(encoding="utf-8")
        item3 = next(line for line in initkit.splitlines() if line.startswith("3. Product requests"))
        use = (KIT / "docs/use-in-your-project.md").read_text(encoding="utf-8")
        self.assertIn(item3, use)
        for rel in surfaces:
            text = (KIT / rel).read_text(encoding="utf-8")
            self.assertIn(reminder, text, rel)

    def test_change_records_the_init_sentence(self) -> None:
        init = (KIT / "specs" / "capabilities" / "capability.specplane_init.yaml").read_text(encoding="utf-8")
        package = (KIT / "specs" / "capabilities" / "capability.specplane_package.yaml").read_text(encoding="utf-8")
        self.assertIn("A published specplane package may run init", init)
        self.assertIn("Init does not publish", init)
        self.assertIn("There is no npx package", init)
        self.assertIn("leaves specs/ in place", init)
        self.assertIn("specplane uninstall removes the kit copy and leaves specs/ in place", init)
        self.assertNotIn("Published PyPI / npx package is not this command", init)
        self.assertIn("0.1.0a1", package)

    def test_change_folders_stay_strings(self) -> None:
        loaded = yaml_load(KIT / "specs" / "capabilities" / "capability.specplane_change_folders.yaml")
        flows = loaded["flows"]
        self.assertTrue(flows)
        self.assertTrue(all(isinstance(item, str) for item in flows))


def yaml_load(path: Path):
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
