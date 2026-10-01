"""Change-aware retrieval, readiness, evidence states, and task context."""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("SPECPLANE_TELEMETRY", "0")

from cli import main as cli_main  # noqa: E402


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _tree(root: Path) -> None:
    _write(
        root / "capabilities" / "capability.capture.yaml",
        """meta:
  id: capability.capture
  level: capability
  purpose: "Live promise stays on the live slice."
  status: active
  version: "0.1.0"
responsibilities:
  - "Record a moment."
diagrams:
  - type: flow
    title: ignore
    mermaid: "flowchart TD\\n  SECRET_DIAGRAM-->B"
""",
    )
    _write(
        root / "capabilities" / "capability.widget_cap.yaml",
        """meta:
  id: capability.widget_cap
  level: capability
  purpose: "Show a widget."
  status: active
  version: "0.1.0"
realized_by:
  components:
    - component.widget
""",
    )
    _write(
        root / "components" / "component.widget.yaml",
        """meta:
  id: component.widget
  level: component
  purpose: "Draws the widget."
  status: active
  version: "0.1.0"
implements:
  - capability.widget_cap
implementation:
  realization:
    paths:
      - src/widget.py
      - src/pkg/
""",
    )
    _write(
        root / "changes" / "phone_follow" / "proposal.yaml",
        """id: phone_follow
kind: learn
status: in-flight
promise_ids:
  - capability.capture
""",
    )
    _write(
        root / "changes" / "phone_follow" / "delta.yaml",
        """MODIFIED:
  - id: capability.capture
    summary: "The phone keeps the household label."
ADDED: []
REMOVED: []
""",
    )
    _write(
        root / "changes" / "phone_follow" / "success.yaml",
        """sensors:
  - id: english-only
    promise: capability.capture
    must: "The household label is kept."
""",
    )
    _write(
        root / "changes" / "widget_follow" / "proposal.yaml",
        """id: widget_follow
kind: learn
status: in-flight
promise_ids:
  - capability.widget_cap
""",
    )
    _write(
        root / "changes" / "widget_follow" / "delta.yaml",
        """MODIFIED:
  - id: capability.widget_cap
    summary: "The widget keeps its declared component."
ADDED: []
REMOVED: []
""",
    )


def _cli(argv: list[str]) -> tuple[int, str, str]:
    out = StringIO()
    err = StringIO()
    with patch("sys.stdout", out), patch("sys.stderr", err):
        code = cli_main(argv)
    return code, out.getvalue(), err.getvalue()


class EffectiveContextTests(unittest.TestCase):
    def test_retrieve_labels_live_and_change(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "specs"
            _tree(root)
            code, text, err = _cli(["retrieve", "capability.capture", "--spec-root", str(root)])
        self.assertEqual(code, 0, text + err)
        live, _, change = text.partition("active change:")
        self.assertIn("Live promise stays on the live slice.", live)
        self.assertNotIn("household label", live)
        self.assertIn("MODIFIED capability.capture: The phone keeps the household label.", change)
        self.assertIn("implementation context: phone_follow", text)
        self.assertIn("canonical synchronization: pending", text)
        self.assertIn("readiness: warning", text)
        self.assertIn(
            "SpecPlane · retrieve — implementation context is phone_follow. "
            "Canonical synchronization is pending. "
            "Readiness warning: no implementation relationships are declared.",
            text,
        )

    def test_related_capability_has_no_readiness_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "specs"
            _tree(root)
            code, text, err = _cli(
                ["retrieve", "capability.widget_cap", "--spec-root", str(root)]
            )
        self.assertEqual(code, 0, text + err)
        self.assertIn("implementation context: widget_follow", text)
        self.assertNotIn("readiness: warning", text)
        self.assertNotIn("Readiness warning", text)

    def test_retrieve_without_a_change_is_silent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "specs"
            _tree(root)
            shutil.rmtree(root / "changes" / "phone_follow")
            code, text, err = _cli(["retrieve", "capability.capture", "--spec-root", str(root)])
        self.assertEqual(code, 0, text + err)
        self.assertIn("in-flight: (none)", text)
        self.assertNotIn("SpecPlane · retrieve", text)
        self.assertNotIn("implementation context:", text)

    def test_english_sensor_is_unverified(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "specs"
            _tree(root)
            code, text, err = _cli(
                [
                    "check_sync",
                    "--spec-root",
                    str(root),
                    "--change",
                    "phone_follow",
                    "--changed-ids",
                    "capability.capture",
                ]
            )
        self.assertEqual(code, 0, text + err)
        self.assertIn("evidence: none", text)
        self.assertIn("status: UNVERIFIED", text)
        self.assertNotIn("status: VERIFIED", text)

    def test_unbound_run_stays_unverified(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "specs"
            _tree(root)
            code, text, err = _cli(
                ["run", "--spec-root", str(root), "--change", "phone_follow", "--repo", tmp]
            )
        self.assertEqual(code, 0, text + err)
        self.assertIn("evidence: none", text)
        self.assertIn("status: UNVERIFIED", text)
        self.assertIn("result: not_run", text)
        self.assertIn(
            "SpecPlane · run — no bound check was executed. "
            "Add run.unittest or run.argv on sensor english-only.",
            text,
        )

    def test_bound_run_is_verified(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "specs"
            _tree(root)
            _write(
                root / "changes" / "phone_follow" / "success.yaml",
                f"""sensors:
  - id: bound
    promise: capability.capture
    must: "A bound command exits 0."
    run:
      argv: [{sys.executable!r}, "-c", "raise SystemExit(0)"]
""",
            )
            code, text, err = _cli(
                ["run", "--spec-root", str(root), "--change", "phone_follow", "--repo", tmp]
            )
        self.assertEqual(code, 0, text + err)
        self.assertIn("status: VERIFIED", text)
        self.assertIn("result: pass", text)
        self.assertIn(sys.executable, text)
        self.assertIn(
            "SpecPlane · run — bound checks passed. "
            "This does not certify the implementation satisfies the spec.",
            text,
        )

    def test_unmapped_file_stays_unmapped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "specs"
            _tree(root)
            secret = Path(tmp) / "src" / "nobody.py"
            _write(secret, "SECRET_BODY = 'do not invent a component'\n")
            code, text, err = _cli(["context", "src/nobody.py", "--spec-root", str(root)])
        self.assertEqual(code, 0, text + err)
        self.assertIn("unmapped: true", text)
        self.assertIn(
            "SpecPlane · context — this file is unmapped. No component declares it.",
            text,
        )
        self.assertNotIn("component.widget", text)
        self.assertNotIn("SECRET_BODY", text)
        self.assertNotIn("capability.capture", text)

    def test_mapped_file_names_the_component(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "specs"
            _tree(root)
            _write(Path(tmp) / "src" / "widget.py", "SECRET_BODY = 'widget source'\n")
            _write(Path(tmp) / "src" / "pkg" / "a.py", "SECRET_BODY = 'pkg source'\n")
            code, text, err = _cli(["context", "src/pkg/a.py", "--spec-root", str(root)])
        self.assertEqual(code, 0, text + err)
        self.assertIn("mapped:", text)
        self.assertIn("component.widget", text)
        self.assertNotIn("unmapped: true", text)
        self.assertNotIn("SECRET_BODY", text)
        self.assertIn("specification:", text)
        self.assertIn("implementation:", text)
        self.assertIn("src/pkg/", text)

    def test_context_keeps_spec_change_and_evidence_apart(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "specs"
            _tree(root)
            code, text, err = _cli(
                ["context", "capability.capture", "--spec-root", str(root), "--change", "phone_follow"]
            )
        self.assertEqual(code, 0, text + err)
        self.assertIn("specification:", text)
        self.assertIn("purpose: Live promise stays on the live slice.", text)
        self.assertIn("change:", text)
        self.assertIn("The phone keeps the household label.", text)
        self.assertIn("implementation:", text)
        self.assertIn("(none declared)", text)
        self.assertIn("evidence:", text)
        self.assertIn("evidence: none", text)
        self.assertIn("status: UNVERIFIED", text)
        self.assertIn("readiness: warning", text)
        self.assertNotIn("SECRET_DIAGRAM", text)

    def test_unknown_id_is_not_unmapped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "specs"
            _tree(root)
            code, text, err = _cli(["context", "capability.missing", "--spec-root", str(root)])
        self.assertEqual(code, 1, text + err)
        self.assertIn("unknown: true", text)
        self.assertNotIn("unmapped: true", text)
        self.assertIn("not found: capability.missing", err)


if __name__ == "__main__":
    unittest.main()
