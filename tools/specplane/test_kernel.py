#!/usr/bin/env python3
"""Tests for retrieve / blast / check_sync (simple kernel CLI)."""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from cli import git_changed_files, main as cli_main  # noqa: E402
from kernel import (  # noqa: E402
    SENSOR_TIMEOUT_S,
    blast,
    check_sync,
    format_check_sync,
    format_list_gaps,
    format_promote,
    format_retrieve,
    format_run,
    list_gaps,
    load_kernel,
    RECONCILE_NOTE,
    default_changed_ids,
    format_reconcile,
    map_changed_files,
    promote_ids,
    reconcile,
    retrieve,
    run_sensors,
)
from validate import validate  # noqa: E402

GOLDEN = ROOT / "testdata" / "golden" / "messy_auth" / "specs"
SCOPED = ROOT / "testdata" / "golden" / "scoped_coverage" / "specs"
REPO = ROOT.parents[1]


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
        text = format_retrieve(payload)
        self.assertIn("review_state: unreviewed", text)
        self.assertIn("status: launched", text)
        self.assertIn("bit: live", text)

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


class ScopedCoverageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.kernel = load_kernel(SCOPED)

    def test_other_change_does_not_cover_when_scoped(self) -> None:
        payload = check_sync(
            self.kernel,
            ["capability.alpha", "component.widget"],
            change_slug="select_output_folder",
        )
        self.assertFalse(payload["ok"], payload)
        self.assertEqual(payload["coverage"], "fail")
        self.assertIn("capability.alpha", payload["uncovered"])
        self.assertIn("component.widget", payload["uncovered"])
        self.assertEqual(payload["behavior"], "unverified")
        text = format_check_sync(payload)
        self.assertIn("coverage: fail", text)
        self.assertIn("behavior: unverified", text)
        self.assertIn("not covered by change select_output_folder", text)
        self.assertIn("SpecPlane checked declared coverage. It did not verify behavior.", text)
        self.assertNotIn("result: pass", text)
        self.assertNotIn("sensors: executed", text)

    def test_same_ids_pass_on_listing_change(self) -> None:
        payload = check_sync(
            self.kernel,
            ["capability.alpha", "component.widget"],
            change_slug="baseline_review",
        )
        self.assertTrue(payload["ok"], payload)
        self.assertEqual(payload["coverage"], "pass")
        self.assertEqual(payload["sensors"], "declared")
        self.assertEqual(payload["behavior"], "unverified")
        text = format_check_sync(payload)
        self.assertIn("sensors: declared", text)
        self.assertIn("not_executed", text)
        self.assertIn("behavior: unverified", text)
        self.assertNotIn("result: pass", text)

    def test_unknown_change_slug_fails(self) -> None:
        from io import StringIO
        from unittest.mock import patch

        buf = StringIO()
        err = StringIO()
        with patch("sys.stdout", buf), patch("sys.stderr", err):
            code = cli_main(
                [
                    "check_sync",
                    "--spec-root",
                    str(SCOPED),
                    "--change",
                    "does_not_exist",
                    "--changed-ids",
                    "capability.alpha",
                ]
            )
        self.assertEqual(code, 1)
        self.assertIn("unknown change: does_not_exist", err.getvalue())
        self.assertIn("unknown_change: does_not_exist", buf.getvalue())
        self.assertIn("coverage: fail", buf.getvalue())

    def test_phase1_advisory_does_not_fail_when_scoped(self) -> None:
        payload = check_sync(
            self.kernel,
            ["capability.thin"],
            change_slug="select_output_folder",
        )
        self.assertTrue(payload["ok"], payload)
        self.assertIn("capability.thin", payload["phase1_advisory"])
        self.assertNotIn("capability.thin", payload["uncovered"])
        self.assertFalse(payload["decision_required"])

    def test_default_any_open_change_still_covers(self) -> None:
        payload = check_sync(self.kernel, ["capability.alpha", "component.widget"])
        self.assertTrue(payload["ok"], payload)


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
        self.assertIn("coverage: pass", buf.getvalue())
        self.assertIn("behavior: unverified", buf.getvalue())
        self.assertNotIn("result: pass", buf.getvalue())
        self.assertNotIn("sensors: executed", buf.getvalue())


class ListGapsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.kernel = load_kernel(GOLDEN)

    def test_kernel_generic_queue(self) -> None:
        from kernel import list_gaps

        payload = list_gaps(self.kernel)
        self.assertTrue(payload["advisory"])
        self.assertIn("capability.orphan", payload["phase1_no_join"])
        self.assertNotIn("capability.authentication", payload["phase1_no_join"])
        self.assertIn("add_passkeys", payload["open_changes"])
        self.assertIn("no_sensor", payload["open_changes"])
        self.assertIn("capability.auth_v1", payload["replaced"])
        self.assertIn("no_sensor", payload["missing_success_sensor"])
        self.assertNotIn("add_passkeys", payload["missing_success_sensor"])
        self.assertEqual(
            [key for key in payload if key != "advisory"],
            [
                "phase1_no_join",
                "open_changes",
                "replaced",
                "missing_success_sensor",
                "inferred_unpromoted",
            ],
        )
        self.assertNotIn("missing_runnable", payload)

    def test_cli_exits_zero(self) -> None:
        from io import StringIO
        from unittest.mock import patch

        buf = StringIO()
        with patch("sys.stdout", buf):
            code = cli_main(["list_gaps", "--spec-root", str(GOLDEN)])
        self.assertEqual(code, 0)
        text = buf.getvalue()
        self.assertIn("phase1_no_join", text)
        self.assertIn("capability.orphan", text)
        self.assertIn("no_sensor", text)
        self.assertIn("inferred_unpromoted", text)
        self.assertIn("advisory: true", text)

    def test_archive_folder_is_not_an_open_change(self) -> None:
        from kernel import list_gaps

        archive = GOLDEN / "changes" / "_archive" / "old_one"
        archive.mkdir(parents=True)
        try:
            (archive / "proposal.yaml").write_text(
                "id: old_one\nkind: evolve\nstatus: in-flight\npromise_ids: []\n",
                encoding="utf-8",
            )
            payload = list_gaps(load_kernel(GOLDEN))
            self.assertNotIn("_archive", payload["open_changes"])
            self.assertNotIn("old_one", payload["open_changes"])
        finally:
            (archive / "proposal.yaml").unlink(missing_ok=True)
            archive.rmdir()
            (GOLDEN / "changes" / "_archive").rmdir()


def _write_change(spec_root: Path, slug: str, sensors: list, *, archive: bool = False) -> None:
    folder = spec_root / "changes" / "_archive" / slug if archive else spec_root / "changes" / slug
    folder.mkdir(parents=True)
    (folder / "proposal.yaml").write_text(
        f'change_id: "{slug}"\nkind: "evolve"\nstatus: "in-flight"\npromise_ids: []\n',
        encoding="utf-8",
    )
    (folder / "success.yaml").write_text(
        yaml.safe_dump({"sensors": sensors}, sort_keys=False),
        encoding="utf-8",
    )


def _cli_run(spec_root: Path, slug: str, repo: Path) -> tuple[int, str, str]:
    from io import StringIO
    from unittest.mock import patch

    buf, err = StringIO(), StringIO()
    with patch("sys.stdout", buf), patch("sys.stderr", err):
        code = cli_main(
            ["run", "--spec-root", str(spec_root), "--change", slug, "--repo", str(repo)]
        )
    return code, buf.getvalue(), err.getvalue()


def _no_bare_result(text: str) -> None:
    for line in text.splitlines():
        if line.startswith("result:"):
            raise AssertionError(f"bare result line: {line}")


class TestRun(unittest.TestCase):
    def test_bound_unittest_target(self) -> None:
        """Leaf check a fixture may bind. Does not call run."""
        self.assertTrue(True)

    def test_executes_bound_unittest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "specs"
            _write_change(
                root,
                "bound_ok",
                [
                    {
                        "id": "bound",
                        "must": "leaf check exits 0",
                        "run": {
                            "unittest": (
                                "tools.specplane.test_kernel.TestRun.test_bound_unittest_target"
                            )
                        },
                    }
                ],
            )
            code, text, err = _cli_run(root, "bound_ok", REPO)
        self.assertEqual(code, 0, text + err)
        self.assertIn("result: pass", text)
        self.assertIn("behavior: evidence", text)
        self.assertIn(
            "SpecPlane invoked bound checks. It did not certify the implementation satisfies the spec.",
            text,
        )
        self.assertNotIn("verified satisfies the spec", text)
        _no_bare_result(text)

    def test_test_key_is_unittest_alias(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "specs"
            _write_change(
                root,
                "alias",
                [
                    {
                        "id": "alias",
                        "must": "test: is a unittest id",
                        "test": "tools.specplane.test_kernel.TestRun.test_bound_unittest_target",
                    }
                ],
            )
            code, text, err = _cli_run(root, "alias", REPO)
        self.assertEqual(code, 0, text + err)
        self.assertIn("result: pass", text)

    def test_english_must_not_executed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            marker = tmp_path / "from_must"
            root = tmp_path / "specs"
            _write_change(
                root,
                "words",
                [{"id": "words", "must": f"touch {marker}"}],
            )
            code, text, err = _cli_run(root, "words", tmp_path)
        self.assertEqual(code, 0, text + err)
        self.assertIn("result: not_run", text)
        self.assertIn("behavior: evidence", text)
        self.assertIn("SpecPlane did not invoke a check.", text)
        self.assertFalse(marker.exists())
        self.assertNotIn("verified satisfies the spec", text)
        _no_bare_result(text)

    def test_evaluator_attach_not_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            marker = tmp_path / "from_evaluator"
            root = tmp_path / "specs"
            _write_change(
                root,
                "ev",
                [
                    {
                        "id": "ev",
                        "must": "evaluator without run is not_run",
                        "evaluator": f"touch {marker}",
                    }
                ],
            )
            code, text, err = _cli_run(root, "ev", tmp_path)
        self.assertEqual(code, 0, text + err)
        self.assertIn("result: not_run", text)
        self.assertFalse(marker.exists())
        self.assertNotIn("verified satisfies the spec", text)

    def test_argv_invoked_without_shell(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            marker = tmp_path / "argv_ran"
            shell_marker = tmp_path / "shelled"
            root = tmp_path / "specs"
            script = (
                "import sys; from pathlib import Path; Path(sys.argv[1]).write_text(sys.argv[2])"
            )
            _write_change(
                root,
                "argv_ok",
                [
                    {
                        "id": "argv_ok",
                        "must": "argv list runs without a shell",
                        "evaluator": f"touch {shell_marker}",
                        "run": {
                            "argv": [sys.executable, "-c", script, str(marker), "ok && not-split"]
                        },
                    }
                ],
            )
            code, text, err = _cli_run(root, "argv_ok", tmp_path)
            self.assertEqual(code, 0, text + err)
            self.assertIn("result: pass", text)
            self.assertEqual(marker.read_text(encoding="utf-8"), "ok && not-split")
            self.assertFalse(shell_marker.exists())

            _write_change(
                root,
                "argv_string",
                [
                    {
                        "id": "argv_string",
                        "must": "a string is not a shell command",
                        "run": {"argv": f"touch {shell_marker}"},
                    }
                ],
            )
            code, text, err = _cli_run(root, "argv_string", tmp_path)
        self.assertEqual(code, 1, text + err)
        self.assertIn("result: error", text)
        self.assertFalse(shell_marker.exists())
        _no_bare_result(text)

    def test_unknown_and_archived_change(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            marker = tmp_path / "archived_ran"
            root = tmp_path / "specs"
            _write_change(root, "live_one", [{"id": "idle", "must": "nothing to run"}])
            script = "import sys; from pathlib import Path; Path(sys.argv[1]).write_text('x')"
            _write_change(
                root,
                "old_run",
                [
                    {
                        "id": "old",
                        "must": "archived",
                        "run": {"argv": [sys.executable, "-c", script, str(marker)]},
                    }
                ],
                archive=True,
            )
            code, text, err = _cli_run(root, "does_not_exist", tmp_path)
            self.assertEqual(code, 1)
            self.assertIn("unknown change: does_not_exist", err)
            self.assertIn("unknown_change: does_not_exist", text)
            code, text, err = _cli_run(root, "old_run", tmp_path)
        self.assertEqual(code, 1, text + err)
        self.assertIn("unknown change: old_run", err)
        self.assertFalse(marker.exists())

    def test_sensor_fail_exits_nonzero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = tmp_path / "specs"
            _write_change(
                root,
                "fails",
                [
                    {
                        "id": "fails",
                        "must": "non-zero bind is fail",
                        "run": {"argv": [sys.executable, "-c", "raise SystemExit(3)"]},
                    }
                ],
            )
            code, text, err = _cli_run(root, "fails", tmp_path)
        self.assertEqual(code, 1, text + err)
        self.assertIn("result: fail", text)
        self.assertIn("exit 3", text)
        self.assertNotIn("verified satisfies the spec", text)
        _no_bare_result(text)

    def test_either_bind_failing_fails_sensor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "specs"
            _write_change(
                root,
                "both",
                [
                    {
                        "id": "both",
                        "must": "both binds must pass",
                        "run": {
                            "unittest": (
                                "tools.specplane.test_kernel.TestRun.test_bound_unittest_target"
                            ),
                            "argv": [sys.executable, "-c", "raise SystemExit(1)"],
                        },
                    }
                ],
            )
            payload = run_sensors(load_kernel(root), "both", repo=REPO)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["sensors"][0]["result"], "fail")

    def test_check_sync_still_not_executed(self) -> None:
        from io import StringIO
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            marker = tmp_path / "should_not_run"
            root = tmp_path / "specs"
            script = "import sys; from pathlib import Path; Path(sys.argv[1]).write_text('x')"
            _write_change(
                root,
                "scoped",
                [
                    {
                        "id": "bound",
                        "must": "claim only",
                        "run": {"argv": [sys.executable, "-c", script, str(marker)]},
                    }
                ],
            )
            buf = StringIO()
            with patch("sys.stdout", buf):
                code = cli_main(
                    ["check_sync", "--spec-root", str(root), "--change", "scoped"]
                )
            text = buf.getvalue()
        self.assertEqual(code, 0, text)
        self.assertIn("sensors: declared", text)
        self.assertIn("not_executed", text)
        self.assertIn("behavior: unverified", text)
        self.assertNotIn("sensors: executed", text)
        self.assertNotIn("result: pass", text)
        self.assertFalse(marker.exists())

    def test_timeout_is_error(self) -> None:
        self.assertEqual(SENSOR_TIMEOUT_S, 120)
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = tmp_path / "specs"
            _write_change(
                root,
                "slow",
                [
                    {
                        "id": "slow",
                        "must": "timeout is error",
                        "run": {
                            "argv": [sys.executable, "-c", "import time; time.sleep(30)"]
                        },
                    }
                ],
            )
            payload = run_sensors(load_kernel(root), "slow", repo=tmp_path, timeout=0.4)
            text = format_run(payload)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["sensors"][0]["result"], "error")
        self.assertIn("timed out", payload["sensors"][0]["detail"])
        self.assertIn("result: error", text)
        self.assertNotIn("verified satisfies the spec", text)


INFERRED = ROOT / "testdata" / "inferred"


def _copy_inferred_product(tmp: Path) -> Path:
    dest = tmp / "product"
    shutil.copytree(INFERRED, dest)
    return dest


class TestPromote(unittest.TestCase):
    def test_retrieve_inferred_not_live(self) -> None:
        spec_root = INFERRED / "specs"
        report = validate(spec_root)
        self.assertEqual([f.format() for f in report.errors], [])
        payload = retrieve(load_kernel(spec_root), "capability.billing_checkout")
        assert payload is not None
        self.assertEqual(payload["bit"], "inferred")
        self.assertIsNone(payload["live"])
        self.assertFalse(payload["inferred_as_live"])
        text = format_retrieve(payload)
        self.assertIn("bit: inferred", text)
        self.assertNotIn("\nlive:", text)

        from io import StringIO
        from unittest.mock import patch

        out, err = StringIO(), StringIO()
        with patch("sys.stdout", out), patch("sys.stderr", err):
            code = cli_main(
                ["retrieve", "capability.billing_checkout", "--spec-root", str(spec_root)]
            )
        self.assertEqual(code, 0)
        self.assertIn("inferred (not live): capability.billing_checkout", err.getvalue())
        self.assertIn("bit: inferred", out.getvalue())
        self.assertNotIn("bit: live", out.getvalue())

    def test_promote_named_ids_become_live(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            product = _copy_inferred_product(Path(tmp))
            spec_root = product / "specs"
            before = (spec_root / "capabilities" / "capability.billing_checkout.yaml").read_text(
                encoding="utf-8"
            )
            payload = promote_ids(
                load_kernel(spec_root),
                ["capability.billing_checkout"],
                today="2026-09-24",
            )
            self.assertTrue(payload["ok"], payload)
            self.assertEqual(payload["promoted"], ["capability.billing_checkout"])
            text = format_promote(payload)
            self.assertIn("capability.billing_checkout", text)
            path = spec_root / "capabilities" / "capability.billing_checkout.yaml"
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            tags = [str(tag).lower() for tag in data["meta"]["tags"]]
            self.assertNotIn("inferred", tags)
            self.assertIn("billing", tags)
            self.assertEqual(data["meta"]["version"], "1.0.1")
            self.assertEqual(data["changelog"][0]["date"], "2026-09-24")
            self.assertEqual(data["changelog"][0]["summary"], "Promoted from inferred to live")
            self.assertIn("cite_checkout", before)
            self.assertEqual(
                data["refs"][0]["path"],
                "src/billing/checkout.py",
            )
            again = retrieve(load_kernel(spec_root), "capability.billing_checkout")
            assert again is not None
            self.assertEqual(again["bit"], "live")
            self.assertIsNotNone(again["live"])
            second = promote_ids(
                load_kernel(spec_root),
                ["capability.billing_checkout"],
                today="2026-09-24",
            )
            self.assertFalse(second["ok"])
            self.assertEqual(second["problems"], ["not inferred: capability.billing_checkout"])
            self.assertEqual(
                yaml.safe_load(path.read_text(encoding="utf-8"))["meta"]["version"],
                "1.0.1",
            )

    def test_unknown_or_already_live_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            product = _copy_inferred_product(Path(tmp))
            spec_root = product / "specs"
            path = spec_root / "capabilities" / "capability.billing_checkout.yaml"
            original = path.read_bytes()
            live = spec_root / "capabilities" / "capability.already.yaml"
            live_doc = yaml.safe_load(path.read_text(encoding="utf-8"))
            live_doc["meta"]["id"] = "capability.already"
            live_doc["meta"]["tags"] = ["billing"]
            live.write_text(
                yaml.safe_dump(live_doc, sort_keys=False),
                encoding="utf-8",
            )
            live_before = live.read_bytes()
            missing = promote_ids(
                load_kernel(spec_root),
                ["capability.billing_checkout", "capability.missing"],
            )
            self.assertFalse(missing["ok"])
            self.assertEqual(missing["promoted"], [])
            self.assertIn("not found: capability.missing", missing["problems"])
            self.assertEqual(path.read_bytes(), original)
            already = promote_ids(load_kernel(spec_root), ["capability.already"])
            self.assertFalse(already["ok"])
            self.assertEqual(already["problems"], ["not inferred: capability.already"])
            self.assertEqual(live.read_bytes(), live_before)
            self.assertEqual(path.read_bytes(), original)

    def test_refuse_without_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            product = _copy_inferred_product(Path(tmp))
            spec_root = product / "specs"
            path = spec_root / "capabilities" / "capability.billing_checkout.yaml"
            original = path.read_bytes()
            payload = promote_ids(load_kernel(spec_root), [])
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["problems"], ["promote requires named ids"])
            self.assertEqual(path.read_bytes(), original)

            from io import StringIO
            from unittest.mock import patch

            err = StringIO()
            with patch("sys.stderr", err):
                code = cli_main(["promote", "--spec-root", str(spec_root)])
            self.assertEqual(code, 1)
            self.assertIn("promote requires named ids", err.getvalue())
            self.assertEqual(path.read_bytes(), original)

    def test_does_not_read_source_to_invent_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            product = _copy_inferred_product(Path(tmp))
            spec_root = product / "specs"
            source = (product / "src" / "checkout.py").read_text(encoding="utf-8")
            self.assertIn("capability.parsed_from_checkout", source)
            payload = list_gaps(load_kernel(spec_root))
            self.assertEqual(payload["inferred_unpromoted"], ["capability.billing_checkout"])
            self.assertNotIn("capability.parsed_from_checkout", payload["inferred_unpromoted"])
            self.assertTrue(payload["advisory"])
            invented = promote_ids(
                load_kernel(spec_root),
                ["capability.parsed_from_checkout"],
            )
            self.assertFalse(invented["ok"])
            self.assertEqual(
                invented["problems"],
                ["not found: capability.parsed_from_checkout"],
            )
            self.assertFalse(
                (spec_root / "capabilities" / "capability.parsed_from_checkout.yaml").exists()
            )
            text = format_list_gaps(payload)
            self.assertIn("inferred_unpromoted:", text)
            self.assertIn("capability.billing_checkout", text)

            from io import StringIO
            from unittest.mock import patch

            out = StringIO()
            with patch("sys.stdout", out):
                code = cli_main(["list_gaps", "--spec-root", str(spec_root)])
            self.assertEqual(code, 0)
            self.assertIn("inferred_unpromoted:", out.getvalue())
            self.assertIn("advisory: true", out.getvalue())

    def test_promote_cli_then_retrieve_is_live(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            product = _copy_inferred_product(Path(tmp))
            spec_root = product / "specs"
            from io import StringIO
            from unittest.mock import patch

            out, err = StringIO(), StringIO()
            with patch("sys.stdout", out), patch("sys.stderr", err):
                code = cli_main(
                    [
                        "promote",
                        "--ids",
                        "capability.billing_checkout",
                        "--spec-root",
                        str(spec_root),
                    ]
                )
            self.assertEqual(code, 0, err.getvalue())
            self.assertIn("capability.billing_checkout", out.getvalue())
            self.assertEqual(err.getvalue(), "")
            out2, err2 = StringIO(), StringIO()
            with patch("sys.stdout", out2), patch("sys.stderr", err2):
                code = cli_main(
                    [
                        "retrieve",
                        "capability.billing_checkout",
                        "--spec-root",
                        str(spec_root),
                    ]
                )
            self.assertEqual(code, 0)
            self.assertIn("bit: live", out2.getvalue())
            self.assertNotIn("inferred (not live)", err2.getvalue())
            promoted = yaml.safe_load(
                (spec_root / "capabilities" / "capability.billing_checkout.yaml").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(promoted["changelog"][0]["date"], date.today().isoformat())


class TestReconcile(unittest.TestCase):
    def _repo(self) -> tuple[Path, Path]:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo = Path(tmp.name)
        spec = repo / "specs"
        (spec / "capabilities").mkdir(parents=True)
        (spec / "components").mkdir()
        (spec / "changes" / "demo").mkdir(parents=True)
        (spec / "capabilities" / "capability.alpha.yaml").write_text(
            "\n".join(
                [
                    "meta:",
                    "  id: capability.alpha",
                    "  level: capability",
                    "realized_by:",
                    "  components:",
                    "    - component.widget",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (spec / "components" / "component.widget.yaml").write_text(
            "\n".join(
                [
                    "meta:",
                    "  id: component.widget",
                    "  level: component",
                    "implements:",
                    "  - capability.alpha",
                    "implementation:",
                    "  realization:",
                    "    paths:",
                    "      - src/widget.py",
                    "      - src/pkg/",
                    "      - src/gone.py",
                    "      - src/missing_dir/",
                    "      - /etc/passwd",
                    "      - ../etc/passwd",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (spec / "changes" / "demo" / "proposal.yaml").write_text(
            "\n".join(
                [
                    "change_id: demo",
                    "kind: evolve",
                    "promise_ids:",
                    "  - capability.alpha",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (repo / "src" / "pkg").mkdir(parents=True)
        (repo / "src" / "pkg2").mkdir()
        (repo / "src" / "widget.py").write_text("RESET_TTL = 60\n", encoding="utf-8")
        (repo / "src" / "pkg" / "a.py").write_text("x = 1\n", encoding="utf-8")
        (repo / "src" / "other.py").write_text("y = 2\n", encoding="utf-8")
        (repo / "src" / "pkg2" / "nope.py").write_text("z = 3\n", encoding="utf-8")
        (repo / "README.md").write_text("readme\n", encoding="utf-8")
        return repo, spec

    def _changed(self) -> list[str]:
        return [
            "src/widget.py",
            "src/pkg/a.py",
            "src/other.py",
            "src/pkg2/nope.py",
            "README.md",
            "specs/capabilities/capability.alpha.yaml",
        ]

    def test_missing_prefix_and_exact(self) -> None:
        repo, spec = self._repo()
        before = (spec / "components" / "component.widget.yaml").read_bytes()
        payload = reconcile(load_kernel(spec), self._changed(), repo=repo)
        text = format_reconcile(payload)
        missing = {(row["id"], row["path"]) for row in payload["missing"]}
        self.assertIn(("component.widget", "src/gone.py"), missing)
        self.assertIn(("component.widget", "src/missing_dir/"), missing)
        self.assertIn(("component.widget", "/etc/passwd"), missing)
        self.assertIn(("component.widget", "../etc/passwd"), missing)
        self.assertNotIn(("component.widget", "src/widget.py"), missing)
        self.assertNotIn(("component.widget", "src/pkg/"), missing)
        mapped = {(row["path"], row["id"]) for row in payload["mapped_changed"]}
        self.assertIn(("src/widget.py", "component.widget"), mapped)
        self.assertIn(("src/pkg/a.py", "component.widget"), mapped)
        self.assertNotIn(("src/pkg2/nope.py", "component.widget"), mapped)
        self.assertIn("id: component.widget", text)
        self.assertIn("path: src/gone.py", text)
        self.assertIn("path: src/widget.py", text)
        self.assertIn(RECONCILE_NOTE, text)
        self.assertNotIn("verified", text)
        self.assertNotIn("RESET_TTL", text)
        self.assertEqual((spec / "components" / "component.widget.yaml").read_bytes(), before)

    def test_unmapped_changed_app_file(self) -> None:
        repo, spec = self._repo()
        payload = reconcile(load_kernel(spec), self._changed(), repo=repo)
        self.assertEqual(payload["unmapped_changed"], ["src/other.py", "src/pkg2/nope.py"])
        self.assertNotIn("README.md", payload["unmapped_changed"])
        self.assertNotIn(
            "specs/capabilities/capability.alpha.yaml", payload["unmapped_changed"]
        )
        text = format_reconcile(payload)
        self.assertIn("unmapped_changed:", text)
        self.assertIn("- src/other.py", text)
        self.assertFalse(payload["ok"])

    def test_does_not_parse_or_rewrite(self) -> None:
        repo, spec = self._repo()
        spec_path = spec / "components" / "component.widget.yaml"
        before = spec_path.read_text(encoding="utf-8")
        body = (repo / "src" / "widget.py").read_text(encoding="utf-8")
        payload = reconcile(load_kernel(spec), ["src/widget.py"], repo=repo)
        text = format_reconcile(payload)
        self.assertIn("RESET_TTL", body)
        self.assertNotIn("RESET_TTL", text)
        self.assertEqual(spec_path.read_text(encoding="utf-8"), before)
        self.assertIn("src/gone.py", before)

    def _git_repo(self) -> tuple[Path, Path]:
        import os
        import subprocess

        repo, spec = self._repo()
        env = os.environ.copy()
        env.update(
            {
                "GIT_AUTHOR_NAME": "specplane-test",
                "GIT_AUTHOR_EMAIL": "specplane-test@example.com",
                "GIT_COMMITTER_NAME": "specplane-test",
                "GIT_COMMITTER_EMAIL": "specplane-test@example.com",
            }
        )
        subprocess.check_call(["git", "init"], cwd=repo, env=env, stdout=subprocess.DEVNULL)
        subprocess.check_call(["git", "add", "specs"], cwd=repo, env=env)
        subprocess.check_call(["git", "commit", "-m", "specs"], cwd=repo, env=env, stdout=subprocess.DEVNULL)
        return repo, spec

    def test_check_sync_default_includes_mapped_id(self) -> None:
        from io import StringIO
        from unittest.mock import patch

        repo, spec = self._git_repo()
        buf = StringIO()
        err = StringIO()
        with patch("sys.stdout", buf), patch("sys.stderr", err):
            code = cli_main(
                ["check_sync", "--spec-root", str(spec), "--repo", str(repo)]
            )
        text = buf.getvalue()
        self.assertEqual(code, 0, text + err.getvalue())
        self.assertIn("component.widget", text)
        self.assertIn("unmapped_changed:", text)
        self.assertIn("src/other.py", text)
        self.assertIn("advisory: unmapped app file; not a coverage failure", text)
        self.assertIn("coverage: pass", text)
        self.assertIn("behavior: unverified", text)
        self.assertNotIn("behavior: verified", text)
        self.assertNotIn("RESET_TTL", text)

    def test_changed_ids_override(self) -> None:
        from io import StringIO
        from unittest.mock import patch

        repo, spec = self._git_repo()
        buf = StringIO()
        with patch("sys.stdout", buf):
            code = cli_main(
                [
                    "check_sync",
                    "--spec-root",
                    str(spec),
                    "--repo",
                    str(repo),
                    "--changed-ids",
                    "capability.alpha",
                ]
            )
        text = buf.getvalue()
        self.assertEqual(code, 0, text)
        self.assertIn("- capability.alpha", text)
        self.assertNotIn("component.widget", text)
        self.assertNotIn("unmapped_changed", text)
        self.assertNotIn("src/other.py", text)

    def test_reconcile_cli_stdout(self) -> None:
        from io import StringIO
        from unittest.mock import patch

        repo, spec = self._git_repo()
        buf = StringIO()
        with patch("sys.stdout", buf):
            code = cli_main(
                ["reconcile", "--spec-root", str(spec), "--repo", str(repo)]
            )
        text = buf.getvalue()
        self.assertEqual(code, 0, text)
        self.assertTrue(text.startswith("reconcile\n"))
        self.assertIn("path: src/gone.py", text)
        self.assertIn("path: src/pkg/a.py", text)
        self.assertIn("note: " + RECONCILE_NOTE, text)
        self.assertNotIn("RESET_TTL", text)

    def test_docs_greenfield_without_infer(self) -> None:
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        self.assertIn("Greenfield can declare maps without infer", readme)

    def test_default_changed_ids_union(self) -> None:
        repo, spec = self._repo()
        kernel = load_kernel(spec)
        ids, unmapped = default_changed_ids(
            kernel, ["src/widget.py", "specs/capabilities/capability.alpha.yaml"], repo
        )
        self.assertIn("component.widget", ids)
        self.assertIn("capability.alpha", ids)
        self.assertEqual(unmapped, [])


if __name__ == "__main__":
    unittest.main()
