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
        self.assertEqual(rec["purpose"], "Customer completes paid checkout")
        self.assertIn("Accept payment and record the order", rec["responsibilities"])
        self.assertEqual(rec["path"], "capabilities/capability.billing_checkout.yaml")
        self.assertNotIn("sequence", rec["projections"])

    def test_affected_hops_are_distances(self) -> None:
        graph = self.payload["impacts"]["capability.billing"]
        root = [node for node in graph["affected"] if node["id"] == "capability.billing"][0]
        self.assertEqual(root["distance"], 0)
        self.assertTrue(root["direct"])
        worker = [node for node in graph["affected"] if node["id"] == "component.invoice_worker"][0]
        self.assertGreaterEqual(worker["distance"], 2)
        self.assertFalse(worker["direct"])
        self.assertTrue(worker["path"])

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

    def test_diagrams_scroll_in_the_column(self) -> None:
        src = (ASSETS / "app.js").read_text(encoding="utf-8")
        css = (ASSETS / "app.css").read_text(encoding="utf-8")
        self.assertIn("diagram-frame", src)
        self.assertNotIn("viewportCanvas(flowStage", src)
        self.assertNotIn("viewportCanvas(sequenceStage", src)
        frame = css.split(".diagram-frame {", 1)[1].split("}", 1)[0]
        self.assertIn("overflow-x: auto", frame)
        self.assertIn("max-width: 100%", frame)
        self.assertNotIn("viewportCanvas", src)
        self.assertNotIn("touch-action: none", css)

    def test_blast_hop_copy_is_in_the_viewer(self) -> None:
        src = (ASSETS / "app.js").read_text(encoding="utf-8")
        self.assertIn("1 hop · direct", src)
        self.assertIn("Further", src)
        self.assertIn("select to expand", src)
        self.assertIn("+ hops", src)
        self.assertIn("terminal · not expanding", src)

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
        self.assertIn("map", rec["projections"])
        self.assertIn("blast", rec["projections"])
        self.assertIn("layers", rec["projections"])
        self.assertIn("journey", rec["projections"])
        self.assertIn("diagrams", rec["projections"])
        self.assertNotIn("sequence", rec["projections"])
        self.assertNotIn("data", rec["projections"])
        self.assertEqual(rec["diagrams"][0]["type"], "sequence")
        self.assertEqual(rec["path"], "capabilities/capability.billing.yaml")
        graph = self.payload["impacts"]["capability.billing"]
        flow = next(
            item
            for item in graph["perspectives"]["product"]["items"]
            if item.get("flow_id") == "patient_payment"
        )
        self.assertEqual(flow["stages"], ["charge", "decline", "retry", "completed"])
        api = self.payload["records"]["component.billing_api"]
        self.assertIn("data", api["projections"])
        self.assertNotIn("diagrams", api["projections"])
        identity = self.payload["records"]["capability.identity"]
        self.assertNotIn("diagrams", identity["projections"])
        self.assertNotIn("data", identity["projections"])
        self.assertNotIn("sequence", identity["projections"])

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
            self.assertTrue((out / "fonts" / "schibsted-grotesk-400.woff2").is_file())
            self.assertTrue((out / "fonts" / "jetbrains-mono-500.woff2").is_file())
            self.assertTrue((out / "payload.js").read_text(encoding="utf-8").startswith("window.SPECPLANE_VIEW"))
            self.assertTrue((out / "logo.png").is_file())
            self.assertIn("logo.png", script)
        server = (ROOT / "view.py").read_text(encoding="utf-8")
        self.assertIn('("127.0.0.1", 0)', server)
        self.assertNotIn("0.0.0.0", server)

    def test_navbar_names_the_system_and_branch(self) -> None:
        systems = [rid for rid, rec in self.payload["records"].items() if rec.get("level") == "system"]
        self.assertEqual(systems, ["system.payments"])
        self.assertEqual(self.payload["context"]["spec_root"], "specs")
        self.assertIsInstance(self.payload["context"]["branch"], str)
        src = (ASSETS / "app.js").read_text(encoding="utf-8")
        self.assertIn(" · read-only", src)
        self.assertIn('label: next === "dark" ? "Dark" : "Light"', src)
        self.assertIn("theme-btn", (ASSETS / "app.css").read_text(encoding="utf-8"))
        self.assertIn("In flight is not a filter: an id is in flight when an open change names it.", src)
        self.assertIn("Inferred ids were recovered from code. They are explorable and stay marked until promoted.", src)
        self.assertIn("Replaced ids stay so history resolves. They are not part of the live model.", src)

    def test_design_system_tokens_are_local(self) -> None:
        css = (ASSETS / "app.css").read_text(encoding="utf-8")
        self.assertIn("Schibsted Grotesk", css)
        self.assertIn("JetBrains Mono", css)
        self.assertIn("--bg-surface: #fbfaf7", css)
        self.assertIn("--bg-surface: #18191c", css)
        self.assertIn("--warning: #9a5b00", css)
        self.assertIn("prefers-color-scheme: dark", css)
        self.assertIn(':root[data-theme="dark"]', css)
        self.assertIn(':root:not([data-theme="light"])', css)
        script = (ASSETS / "app.js").read_text(encoding="utf-8")
        self.assertIn("specplane-view-theme", script)
        self.assertIn('"light"', script)
        self.assertIn('"dark"', script)
        self.assertNotIn("fonts.googleapis.com", css)
        self.assertNotIn("cdn.", css)
        self.assertIn("1440px", css)
        self.assertIn("clamp(24px, 4vw, 64px)", css)
        self.assertIn("minmax(420px, 5fr) minmax(0, 7fr)", css)
        self.assertIn("72ch", css)
        self.assertIn("overflow-wrap: anywhere", css)
        self.assertIn("minmax(0, 1fr)", css)
        self.assertIn("1100px", css)
        id_rule = css.split(".node .id {", 1)[1].split("}", 1)[0]
        self.assertNotIn("ellipsis", id_rule)
        self.assertIn(".node .line", css)
        self.assertNotIn("break-all", css)
        self.assertIn("[._/]", script)
        self.assertIn("Open ↓", script)
        self.assertIn("Close ↑", script)
        self.assertIn("← Live", script)
        self.assertIn("Why this is here", script)
        self.assertIn("declared here", script)
        self.assertIn("parseFlow", script)
        self.assertIn("parseSequence", script)
        self.assertIn("not represented", script)
        self.assertIn("background: var(--bg-canvas)", css)
        self.assertIn("720px", css)
        self.assertIn("--bg-hover", css)
        self.assertTrue((ASSETS / "fonts" / "schibsted-grotesk-600.woff2").is_file())
        self.assertTrue((ASSETS / "fonts" / "jetbrains-mono-500.woff2").is_file())


if __name__ == "__main__":
    unittest.main()
