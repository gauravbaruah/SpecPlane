#!/usr/bin/env python3
"""CI compose: default check_sync on a PR diff, then run when a change folder is in it."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
GOLDEN = ROOT / "testdata" / "golden" / "messy_auth" / "specs"
GATE = ROOT / "ci_gate.py"

sys.path.insert(0, str(ROOT))

from ci_gate import change_slugs, open_change_slugs  # noqa: E402
from initkit import CLI_FILES  # noqa: E402


def _git(repo: Path, *args: str) -> None:
    subprocess.check_call(
        ["git", "-c", "user.email=ci@example.com", "-c", "user.name=ci", *args],
        cwd=repo,
        stdout=subprocess.DEVNULL,
    )


def _repo_with_golden() -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="specplane-ci-"))
    shutil.copytree(GOLDEN, tmp / "specs")
    _git(tmp, "init")
    _git(tmp, "add", "specs")
    _git(tmp, "commit", "-m", "base")
    return tmp


def _run_gate(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(GATE),
            "--repo",
            str(repo),
            "--base",
            "HEAD~1",
            "--spec-root",
            str(repo / "specs"),
            "--apply-diff",
        ],
        cwd=repo,
        text=True,
        capture_output=True,
    )


class CiGateTests(unittest.TestCase):
    def test_change_slugs_skip_archive(self) -> None:
        slugs = change_slugs(
            [
                "specs/changes/ci_compose/proposal.yaml",
                "specs/changes/_archive/old/proposal.yaml",
                "specs/capabilities/capability.widget.yaml",
                "notes/changes/nope/proposal.yaml",
            ]
        )
        self.assertEqual(slugs, ["ci_compose"])

    def test_archived_folder_is_not_an_open_slug(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            slugs = open_change_slugs(
                repo,
                ["specs/changes/promote_completed/proposal.yaml"],
            )
        self.assertEqual(slugs, [])

    def test_skip_skill_spec_edit_fails(self) -> None:
        repo = _repo_with_golden()
        try:
            banner = next((repo / "specs").rglob("component.banner.yaml"))
            banner.write_text(banner.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            _git(repo, "add", "specs")
            _git(repo, "commit", "-m", "edit banner")
            result = _run_gate(repo)
        finally:
            shutil.rmtree(repo)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("coverage: fail", result.stdout)
        self.assertIn("component.banner", result.stdout)
        self.assertIn("ci_gate slugs: (none)", result.stdout)
        self.assertNotIn("sensors: executed", result.stdout)
        self.assertNotIn("\nrun\n", result.stdout)

    def test_cooperating_change_runs(self) -> None:
        repo = _repo_with_golden()
        try:
            banner = next((repo / "specs").rglob("component.banner.yaml"))
            banner.write_text(banner.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            folder = repo / "specs" / "changes" / "cover_banner"
            folder.mkdir(parents=True)
            (folder / "proposal.yaml").write_text(
                'id: "cover_banner"\nkind: "fix"\nstatus: "in-flight"\n'
                "promise_ids:\n  - component.banner\n",
                encoding="utf-8",
            )
            (folder / "success.yaml").write_text(
                "sensors:\n"
                "  - id: ok\n"
                "    must: bound argv exits 0\n"
                "    run:\n"
                "      argv:\n"
                f'        - "{sys.executable}"\n'
                '        - "-c"\n'
                '        - "raise SystemExit(0)"\n',
                encoding="utf-8",
            )
            _git(repo, "add", "specs")
            _git(repo, "commit", "-m", "cover banner")
            result = _run_gate(repo)
        finally:
            shutil.rmtree(repo)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ci_gate slugs: cover_banner", result.stdout)
        self.assertIn("change: cover_banner", result.stdout)
        self.assertIn("\nrun\n", result.stdout)
        self.assertIn("result: pass", result.stdout)
        self.assertNotIn("sensors: executed", result.stdout)

    def test_unmapped_app_file_does_not_fail(self) -> None:
        repo = _repo_with_golden()
        try:
            app = repo / "src" / "app.py"
            app.parent.mkdir()
            app.write_text("ttl = 15\n", encoding="utf-8")
            _git(repo, "add", "src")
            _git(repo, "commit", "-m", "unmapped")
            result = _run_gate(repo)
        finally:
            shutil.rmtree(repo)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("unmapped_changed:", result.stdout)
        self.assertIn("src/app.py", result.stdout)
        self.assertIn("coverage: pass", result.stdout)

    def test_init_does_not_write_workflow(self) -> None:
        self.assertIn("ci_gate.py", CLI_FILES)
        init_src = (ROOT / "initkit.py").read_text(encoding="utf-8")
        self.assertIn("did not write GitHub Actions or git hooks", init_src)
        workflow = (REPO / ".github" / "workflows" / "specplane-gate.yml").read_text(encoding="utf-8")
        docs = (REPO / "docs" / "ci.md").read_text(encoding="utf-8")
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        self.assertIn("pull_request:", workflow)
        self.assertIn("ci_gate.py", workflow)
        self.assertIn("--apply-diff", workflow)
        self.assertIn("specplane init does not write this file", workflow)
        self.assertIn("does not write this file", docs)
        self.assertIn("check_sync", docs)
        self.assertIn("run --change", docs)
        self.assertIn("does not turn the check into a required GitHub check", docs)
        guide = (REPO / "docs" / "use-in-your-project.md").read_text(encoding="utf-8")
        self.assertIn("Init does not write that workflow", guide)
        self.assertIn("not a required GitHub check", guide)
        self.assertIn("a required GitHub check", readme)
        self.assertNotIn("**In development:**", readme)

    def test_public_docs_match_what_ships(self) -> None:
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        specs_readme = (REPO / "specs" / "README.md").read_text(encoding="utf-8")
        guide = (REPO / "docs" / "use-in-your-project.md").read_text(encoding="utf-8")
        ci = (REPO / "docs" / "ci.md").read_text(encoding="utf-8")
        public = "\n".join(
            [
                readme,
                guide,
                ci,
                (REPO / "docs" / "try.md").read_text(encoding="utf-8"),
                (REPO / "AGENTS.md").read_text(encoding="utf-8"),
            ]
        )
        self.assertIn("specplane view", readme)
        out_of_slice = specs_readme.split("## Out of slice", 1)[1]
        self.assertNotIn("Viewer", out_of_slice)
        not_yet = guide.split("## Not included yet", 1)[1]
        self.assertNotIn("supported spec viewer", not_yet)
        self.assertNotIn("Git hooks or CI/CD wiring", not_yet)
        self.assertNotIn("pip install -e .", ci)
        self.assertIn("pip install -r tools/specplane/requirements.txt", ci)
        self.assertNotIn("CI checks at the intent level", public)
        self.assertIn("declared intent and bound evidence", ci)

    def test_checkout_tiny_saas_auth_edit_fails_coverage(self) -> None:
        tiny = REPO / "examples" / "tiny-saas"
        auth = tiny / "src" / "auth.py"
        original = auth.read_text(encoding="utf-8")
        cli = ROOT / "cli.py"
        try:
            auth.write_text(original.replace("60", "15", 1), encoding="utf-8")
            nested = _check_sync(tiny, tiny, tiny / "specs")
            toplevel = _check_sync(REPO, tiny, tiny / "specs")
        finally:
            auth.write_text(original, encoding="utf-8")
        self.assertEqual(nested.returncode, 1, nested.stdout + nested.stderr)
        self.assertIn("component.password_reset", nested.stdout)
        self.assertIn("coverage: fail", nested.stdout)
        self.assertNotIn("examples/tiny-saas/src/auth.py", nested.stdout)
        self.assertEqual(toplevel.returncode, 1, toplevel.stdout + toplevel.stderr)
        self.assertIn("component.password_reset", toplevel.stdout)
        self.assertIn("coverage: fail", toplevel.stdout)

    def test_nested_apply_diff_fails_mapped_edit(self) -> None:
        repo = _nested_tiny()
        try:
            auth = repo / "app" / "src" / "auth.py"
            auth.write_text(
                auth.read_text(encoding="utf-8").replace("60", "15", 1),
                encoding="utf-8",
            )
            _git(repo, "add", "app/src/auth.py")
            _git(repo, "commit", "-m", "ttl")
            result = subprocess.run(
                [
                    sys.executable,
                    str(GATE),
                    "--repo",
                    str(repo),
                    "--base",
                    "HEAD~1",
                    "--spec-root",
                    str(repo / "app" / "specs"),
                    "--apply-diff",
                ],
                cwd=repo,
                text=True,
                capture_output=True,
            )
        finally:
            shutil.rmtree(repo)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("component.password_reset", result.stdout)
        self.assertIn("coverage: fail", result.stdout)

    def test_nested_unmapped_file_stays_advisory(self) -> None:
        repo = _nested_tiny()
        try:
            extra = repo / "app" / "src" / "notes.py"
            extra.write_text("note = 1\n", encoding="utf-8")
            _git(repo, "add", "app/src/notes.py")
            _git(repo, "commit", "-m", "note")
            result = subprocess.run(
                [
                    sys.executable,
                    str(GATE),
                    "--repo",
                    str(repo),
                    "--base",
                    "HEAD~1",
                    "--spec-root",
                    str(repo / "app" / "specs"),
                    "--apply-diff",
                ],
                cwd=repo,
                text=True,
                capture_output=True,
            )
        finally:
            shutil.rmtree(repo)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("src/notes.py", result.stdout)
        self.assertIn("coverage: pass", result.stdout)


def _check_sync(repo: Path, config_dir: Path, spec_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(ROOT / "cli.py"),
            "check_sync",
            "--repo",
            str(repo),
            "--config-dir",
            str(config_dir),
            "--spec-root",
            str(spec_root),
        ],
        cwd=repo,
        text=True,
        capture_output=True,
    )


def _nested_tiny() -> Path:
    tiny = REPO / "examples" / "tiny-saas"
    tmp = Path(tempfile.mkdtemp(prefix="specplane-nested-"))
    app = tmp / "app"
    shutil.copytree(tiny / "specs", app / "specs")
    shutil.copytree(tiny / "src", app / "src")
    shutil.copy(tiny / "specplane.config.json", app / "specplane.config.json")
    _git(tmp, "init")
    _git(tmp, "add", "app")
    _git(tmp, "commit", "-m", "base")
    return tmp


if __name__ == "__main__":
    unittest.main()
