#!/usr/bin/env python3
"""Tests for retrieve / blast / check_sync (simple kernel CLI)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from cli import git_changed_files, main as cli_main  # noqa: E402
from kernel import blast, check_sync, load_kernel, map_changed_files, retrieve  # noqa: E402
from validate import validate  # noqa: E402

GOLDEN = ROOT / "testdata" / "golden" / "messy_auth" / "specs"


class GoldenValidate(unittest.TestCase):
    def test_golden_tree_is_structurally_valid(self) -> None:
        report = validate(GOLDEN)
        self.assertEqual([f.format() for f in report.errors], [])


class RetrieveTests(unittest.TestCase):
    def setUp(self) -> None:
        self.kernel = load_kernel(GOLDEN)

    def test_one_live_graph_leftover_and_open_delta(self) -> None:
        payload = retrieve(self.kernel, "capability.authentication")
        assert payload is not None
        self.assertEqual(payload["bit"], "live")
        assert payload["live"] is not None
        self.assertEqual(payload["live"]["id"], "capability.authentication")
        self.assertIn("component.session_manager", payload["live"]["realized_by_components"])
        self.assertEqual(payload["replaced"], ["capability.auth_v1"])
        self.assertEqual(payload["in_flight"][0]["id"], "add_passkeys")
        self.assertFalse(payload["inferred_as_live"])

    def test_unknown_id_is_none(self) -> None:
        self.assertIsNone(retrieve(self.kernel, "capability.does_not_exist"))

    def test_replaced_id_is_not_default_live(self) -> None:
        payload = retrieve(self.kernel, "capability.auth_v1")
        assert payload is not None
        self.assertEqual(payload["bit"], "replaced")
        self.assertIsNone(payload["live"])


class BlastTests(unittest.TestCase):
    def setUp(self) -> None:
        self.kernel = load_kernel(GOLDEN)

    def test_session_manager_does_not_explode_through_foundation(self) -> None:
        payload = blast(self.kernel, "component.session_manager")
        assert payload is not None
        comps = payload["affects"]["components"]
        caps = payload["affects"]["capabilities"]
        self.assertIn("component.login_api", comps)
        self.assertIn("component.token_store", comps)
        self.assertIn("component.session_manager", comps)
        self.assertNotIn("component.banner", comps)
        self.assertIn("capability.authentication", caps)
        self.assertNotIn("capability.marketing", caps)
        self.assertIn("foundation.security_baseline", payload["affects"]["foundations"])
        self.assertFalse(payload["empty"])
        self.assertIn("add_passkeys", payload["open_changes"])

    def test_orphan_is_empty_blast(self) -> None:
        payload = blast(self.kernel, "capability.orphan")
        assert payload is not None
        self.assertTrue(payload["empty"])


class CheckSyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.kernel = load_kernel(GOLDEN)

    def test_pass_when_open_change_covers_component_via_capability(self) -> None:
        payload = check_sync(self.kernel, ["component.session_manager"])
        self.assertTrue(payload["ok"], payload)
        self.assertFalse(payload["decision_required"])

    def test_fail_when_unrelated_id_has_no_open_change(self) -> None:
        payload = check_sync(self.kernel, ["component.banner"])
        self.assertFalse(payload["ok"])
        self.assertIn("component.banner", payload["uncovered"])
        self.assertTrue(payload["decision_required"])

    def test_phase1_orphan_is_advisory_not_fail(self) -> None:
        payload = check_sync(self.kernel, ["capability.orphan"])
        self.assertTrue(payload["ok"], payload)
        self.assertIn("capability.orphan", payload["phase1_advisory"])
        self.assertNotIn("capability.orphan", payload["empty_blast"])
        self.assertFalse(payload["decision_required"])

    def test_linked_and_phase1_still_fails_on_linked(self) -> None:
        payload = check_sync(self.kernel, ["component.banner", "capability.orphan"])
        self.assertFalse(payload["ok"])
        self.assertIn("component.banner", payload["uncovered"])
        self.assertIn("capability.orphan", payload["phase1_advisory"])
        self.assertNotIn("capability.orphan", payload["uncovered"])

    def test_untracked_spec_yaml_maps_to_ids(self) -> None:
        import subprocess
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.check_call(["git", "init"], cwd=repo, stdout=subprocess.DEVNULL)
            spec = repo / "specs" / "capabilities" / "capability.orphan.yaml"
            spec.parent.mkdir(parents=True)
            spec.write_text("meta: {id: capability.orphan}\n", encoding="utf-8")
            files = git_changed_files(repo)
            self.assertTrue(any(Path(f).name == "capability.orphan.yaml" for f in files), files)
            ids = map_changed_files(self.kernel, files)
            self.assertIn("capability.orphan", ids)
            change_file = (
                repo / "specs" / "changes" / "demo" / "proposal.yaml"
            )
            change_file.parent.mkdir(parents=True)
            change_file.write_text("id: demo\n", encoding="utf-8")
            files2 = git_changed_files(repo)
            ids2 = map_changed_files(self.kernel, files2)
            self.assertNotIn("demo", ids2)


class CliSmoke(unittest.TestCase):
    def test_retrieve_stdout(self) -> None:
        from io import StringIO
        from unittest.mock import patch

        buf = StringIO()
        with patch("sys.stdout", buf):
            code = cli_main(
                ["retrieve", "capability.authentication", "--spec-root", str(GOLDEN)]
            )
        self.assertEqual(code, 0)
        self.assertIn("capability.authentication", buf.getvalue())
        self.assertIn("capability.auth_v1", buf.getvalue())
        self.assertIn("add_passkeys", buf.getvalue())

    def test_retrieve_missing(self) -> None:
        from io import StringIO
        from unittest.mock import patch

        err = StringIO()
        with patch("sys.stderr", err):
            code = cli_main(["retrieve", "capability.nope", "--spec-root", str(GOLDEN)])
        self.assertEqual(code, 1)
        self.assertIn("not found", err.getvalue())

    def test_check_sync_fail_exit(self) -> None:
        from io import StringIO
        from unittest.mock import patch

        buf = StringIO()
        with patch("sys.stdout", buf):
            code = cli_main(
                [
                    "check_sync",
                    "--spec-root",
                    str(GOLDEN),
                    "--changed-ids",
                    "component.banner",
                ]
            )
        self.assertEqual(code, 1)
        self.assertIn("DECISION REQUIRED", buf.getvalue())

    def test_check_sync_phase1_exit_zero(self) -> None:
        from io import StringIO
        from unittest.mock import patch

        buf = StringIO()
        with patch("sys.stdout", buf):
            code = cli_main(
                [
                    "check_sync",
                    "--spec-root",
                    str(GOLDEN),
                    "--changed-ids",
                    "capability.orphan",
                ]
            )
        self.assertEqual(code, 0)
        self.assertIn("phase1_advisory", buf.getvalue())
        self.assertIn("result: pass", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
