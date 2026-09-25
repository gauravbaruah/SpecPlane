#!/usr/bin/env python3
"""Viewer projects kernel payloads. It does not restyle inferred as live."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from kernel import list_gaps, load_kernel  # noqa: E402
from view import build_payload, write_site  # noqa: E402

BILLING = ROOT / "testdata" / "impact_billing" / "specs"
INFERRED = ROOT / "testdata" / "inferred" / "specs"
ASSETS = ROOT / "viewer"
FORBIDDEN = (
    "no security impact",
    "no QA required",
    "No compliance impact",
    "No owner required",
)


class ViewerModelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.kernel = load_kernel(BILLING)
        self.payload = build_payload(self.kernel)

    def test_inferred_is_not_live(self) -> None:
        payload = build_payload(load_kernel(INFERRED))
        rec = payload["records"]["capability.billing_checkout"]
        self.assertEqual(rec["bit"], "inferred")
        self.assertFalse(rec["live_slice"])
        self.assertFalse(rec["inferred_as_live"])
        self.assertNotIn("sequence", rec["projections"])

    def test_affected_path_comes_from_impact(self) -> None:
        graph = self.payload["impacts"]["capability.billing"]
        others = [node for node in graph["affected"] if node["id"] != "capability.billing"]
        self.assertTrue(others)
        for node in others:
            self.assertTrue(node["path"], node["id"])
            for step in node["path"]:
                self.assertIn("from", step)
                self.assertIn("relationship", step)
                self.assertIn("to", step)
                self.assertTrue(step["to"])

    def test_gaps_match_list_gaps(self) -> None:
        self.assertEqual(self.payload["gaps"], list_gaps(self.kernel))

    def test_no_negative_security_claim(self) -> None:
        blob = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (
                ASSETS / "app.js",
                ASSETS / "app.css",
                ASSETS / "index.html",
                ROOT / "view.py",
            )
        )
        for phrase in FORBIDDEN:
            self.assertNotIn(phrase, blob)

    def test_projection_switcher(self) -> None:
        rec = self.payload["records"]["capability.billing"]
        self.assertEqual(
            [name for name in rec["projections"] if name in {"sequence", "diagrams", "data"}],
            [],
        )
        self.assertIn("map", rec["projections"])
        self.assertIn("blast", rec["projections"])
        self.assertIn("layers", rec["projections"])
        self.assertIn("journey", rec["projections"])
        self.assertNotIn("sequence", rec["projections"])

    def test_design_time_change(self) -> None:
        change = next(item for item in self.payload["changes"] if item["id"] == "billing_retry")
        self.assertIn("capability.billing", change["promise_ids"])
        self.assertTrue(change["why"])
        self.assertEqual(change["delta"], {})
        self.assertIn("blast", change["projections"])
        graph = self.payload["impacts"]["change:billing_retry"]
        promised = next(node for node in graph["affected"] if node["id"] == "capability.billing")
        self.assertTrue(promised["path"])

    def test_site_is_local(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            write_site(self.payload, out)
            html = (out / "index.html").read_text(encoding="utf-8")
            script = (out / "app.js").read_text(encoding="utf-8")
            self.assertNotIn("cdn.", html + script)
            self.assertNotIn("http://", html)
            self.assertNotIn("https://", html)
            self.assertTrue((out / "vendor" / "mermaid.min.js").is_file())
            self.assertTrue((out / "payload.js").read_text(encoding="utf-8").startswith("window.SPECPLANE_VIEW"))
        server = (ROOT / "view.py").read_text(encoding="utf-8")
        self.assertIn('("127.0.0.1", 0)', server)
        self.assertNotIn("0.0.0.0", server)


if __name__ == "__main__":
    unittest.main()
