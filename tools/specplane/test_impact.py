#!/usr/bin/env python3
"""Impact is one subgraph plus projections. Membership matches blast for spec ids."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

import yaml

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from cli import main as cli_main  # noqa: E402
from impact import (  # noqa: E402
    _GOVERNANCE_GAP,
    _INFERRED_NOTE,
    _OWNERSHIP_GAP,
    format_impact,
    impact,
)
from kernel import blast, load_kernel  # noqa: E402
from mcp_stdio import dispatch  # noqa: E402
from validate import validate  # noqa: E402

FIXTURE = ROOT / "testdata" / "impact_billing" / "specs"
GOLDEN = ROOT / "testdata" / "golden" / "messy_auth" / "specs"

FORBIDDEN = (
    "no security impact",
    "no compliance review",
    "no qa required",
    "no qa ",
    "untested",
    "is safe",
    "are safe",
)


def _node(payload: dict, spec_id: str) -> dict:
    for node in payload["affected"]:
        if node["id"] == spec_id:
            return node
    raise AssertionError(f"{spec_id} not in affected")


def _ids(payload: dict) -> set[str]:
    return {node["id"] for node in payload["affected"]}


def _blast_sets(payload: dict) -> tuple[set[str], set[str], set[str]]:
    caps: set[str] = set()
    comps: set[str] = set()
    founds: set[str] = set()
    for node in payload["affected"]:
        if node["epistemic_state"] == "derived":
            continue
        if node["level"] == "capability":
            caps.add(node["id"])
        elif node["level"] == "component":
            comps.add(node["id"])
        elif node["level"] == "foundation":
            founds.add(node["id"])
    return caps, comps, founds


def _text_values(value: object):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _text_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from _text_values(item)


class ImpactTests(unittest.TestCase):
    def setUp(self) -> None:
        self.kernel = load_kernel(FIXTURE)

    def test_fixture_is_structurally_valid(self) -> None:
        report = validate(FIXTURE)
        self.assertEqual([finding.format() for finding in report.errors], [])

    def test_change_path_explains_worker(self) -> None:
        payload = impact(self.kernel, "billing_retry")
        assert payload is not None
        self.assertEqual(payload["root"], "change.billing_retry")
        self.assertEqual(payload["root_kind"], "change")
        worker = _node(payload, "component.invoice_worker")
        self.assertFalse(worker["direct"])
        self.assertEqual(worker["epistemic_state"], "declared")
        self.assertEqual(worker["source"], "spec")
        self.assertEqual(
            [(step["from"], step["relationship"], step["to"]) for step in worker["path"]],
            [
                ("change.billing_retry", "promises", "capability.billing"),
                ("capability.billing", "realized_by.components", "component.billing_api"),
                ("component.billing_api", "dependencies.internal", "component.invoice_worker"),
            ],
        )
        billing = _node(payload, "capability.billing")
        self.assertTrue(billing["direct"])
        self.assertEqual(billing["relationship"], "promises")

    def test_change_alias_and_no_git(self) -> None:
        def boom(*_args: object, **_kwargs: object) -> None:
            raise AssertionError("impact must not invoke git")

        with mock.patch.object(subprocess, "check_output", boom):
            payload = impact(self.kernel, "change.billing_retry")
        assert payload is not None
        self.assertEqual(payload["root"], "change.billing_retry")
        self.assertIn("component.billing_api", _ids(payload))

    def test_inclusion_and_deliberate_absence(self) -> None:
        payload = impact(self.kernel, "billing_retry")
        assert payload is not None
        ids = _ids(payload)
        for spec_id in (
            "capability.billing",
            "container.billing",
            "component.billing_api",
            "component.invoice_worker",
            "component.payment_store",
            "foundation.privacy_consent",
            "system.payments",
        ):
            self.assertIn(spec_id, ids)
        self.assertNotIn("component.unrelated_mailer", ids)
        self.assertNotIn("capability.identity", ids)
        self.assertNotIn("capability.ledger", ids)
        store = _node(payload, "component.payment_store")
        self.assertEqual(store["epistemic_state"], "inferred")
        self.assertEqual(store["note"], _INFERRED_NOTE)
        self.assertEqual(store["relationship"], "dependencies.internal")
        system = _node(payload, "system.payments")
        self.assertEqual(system["epistemic_state"], "derived")
        self.assertTrue(str(system["source"]).startswith("inverse:"))
        container = _node(payload, "container.billing")
        self.assertEqual(container["epistemic_state"], "declared")
        self.assertEqual(container["relationship"], "realized_by.containers")

    def test_product_uses_declared_fields_only(self) -> None:
        payload = impact(self.kernel, "billing_retry")
        assert payload is not None
        product = payload["perspectives"]["product"]
        details = {item.get("detail") for item in product["items"]}
        self.assertIn("payment_completion", details)
        self.assertIn("patient_payment", details)
        roadmap = [
            item
            for item in product["items"]
            if item.get("kind") == "roadmap_dependency"
        ]
        self.assertEqual(len(roadmap), 1)
        self.assertEqual(roadmap[0]["related_id"], "capability.identity")
        self.assertFalse(roadmap[0]["in_affected_subgraph"])
        refs = [item for item in product["items"] if item.get("kind") == "flow_ref"]
        missing = [item for item in refs if item["detail"] == "missing_flow"]
        self.assertEqual(missing[0]["resolved"], False)
        gap_text = " ".join(gap["statement"] for gap in product["gaps"])
        self.assertIn("missing_flow", gap_text)

    def test_quality_distinguishes_missing_verification(self) -> None:
        payload = impact(self.kernel, "billing_retry")
        assert payload is not None
        quality = payload["perspectives"]["quality"]
        missing = {row["subject"] for row in quality["missing_verification"]}
        self.assertIn("component.invoice_worker", missing)
        self.assertNotIn("component.billing_api", missing)
        strategy_notes = [
            row["note"]
            for row in quality["verification"]
            if row.get("kind") == "test_strategy" and row["subject"] == "component.billing_api"
        ]
        self.assertTrue(strategy_notes)
        self.assertIn("not evidence", strategy_notes[0])
        sensor_notes = [row["note"] for row in quality["sensors"]]
        self.assertTrue(sensor_notes)
        self.assertTrue(all("not evidence" in note for note in sensor_notes))
        journeys = quality["journeys"]
        self.assertEqual(journeys[0]["flow_id"], "patient_payment")
        self.assertIn("card_declined", journeys[0]["exceptions"])
        self.assertIn("retry_with_new_card", journeys[0]["recovery"])
        criteria = {row["detail"] for row in quality["criteria"]}
        self.assertIn("A declined charge can be retried once", criteria)
        self.assertIn("payment_completion", criteria)

    def test_stages_outcomes_and_data_models(self) -> None:
        payload = impact(self.kernel, "capability.billing")
        assert payload is not None
        product = payload["perspectives"]["product"]
        flow = next(item for item in product["items"] if item.get("flow_id") == "patient_payment")
        self.assertEqual(flow["stages"], ["charge", "decline", "retry", "completed"])
        self.assertEqual(flow["outcomes"]["success"], ["payment completed"])
        self.assertEqual(flow["outcomes"]["abandonment"], ["patient leaves"])
        quality = payload["perspectives"]["quality"]
        models = [row for row in quality["contracts"] if row.get("kind") == "data_models"]
        self.assertEqual(len(models), 1)
        self.assertEqual(models[0]["subject"], "component.billing_api")
        self.assertEqual(models[0]["epistemic_state"], "declared")
        self.assertEqual(models[0]["source"], "contracts.data_models")
        self.assertEqual(
            models[0]["models"]["RetryRequest"]["fields"],
            ["invoice_id", "instrument_id"],
        )

    def test_governance_is_declared_and_foundations_stay_unclassified(self) -> None:
        payload = impact(self.kernel, "billing_retry")
        assert payload is not None
        governance = payload["perspectives"]["governance"]
        concerns = {(row["subject"], row["concern"]) for row in governance["concerns"]}
        self.assertIn(("capability.billing", "legal"), concerns)
        self.assertIn(("capability.billing", "security"), concerns)
        self.assertIn(("capability.billing", "data_classification"), concerns)
        self.assertIn(("component.billing_api", "compliance"), concerns)
        self.assertNotIn("privacy", {row["concern"] for row in governance["concerns"]})
        foundations = {row["id"] for row in governance["unclassified_foundations"]}
        self.assertEqual(foundations, {"foundation.privacy_consent"})
        self.assertNotIn("capability.identity", {row["subject"] for row in governance["concerns"]})
        joined = " ".join(row["statement"] for row in governance["unclassified_foundations"])
        self.assertIn("does not identify a governance relationship", joined)

    def test_absence_is_not_a_negative_claim(self) -> None:
        payload = impact(self.kernel, "billing_retry")
        assert payload is not None
        blob = "\n".join(_text_values(payload)).lower()
        for phrase in FORBIDDEN:
            self.assertNotIn(phrase, blob)
        ownership = payload["perspectives"]["ownership"]
        gaps = {(row["subject"], row["statement"]) for row in ownership["gaps"]}
        self.assertIn(("component.invoice_worker", _OWNERSHIP_GAP), gaps)
        owners = {
            (row["subject"], row["source"], row["owner"])
            for row in ownership["associations"]
        }
        self.assertIn(("component.billing_api", "meta.owner", "Payments Platform"), owners)
        self.assertIn(("component.billing_api", "CODEOWNERS", "@payments-codeowners"), owners)
        self.assertIn(("capability.billing", "meta.owner", "Product / Billing"), owners)
        mail = [row for row in ownership["associations"] if row["owner"] == "Mail Team"]
        self.assertEqual(mail, [])

        ledger = impact(self.kernel, "capability.ledger")
        assert ledger is not None
        ledger_blob = "\n".join(_text_values(ledger)).lower()
        for phrase in FORBIDDEN:
            self.assertNotIn(phrase, ledger_blob)
        gov_gaps = [row["statement"] for row in ledger["perspectives"]["governance"]["gaps"]]
        self.assertIn(_GOVERNANCE_GAP, gov_gaps)
        self.assertIn(
            ("capability.ledger", _OWNERSHIP_GAP),
            {(row["subject"], row["statement"]) for row in ledger["perspectives"]["ownership"]["gaps"]},
        )

    def test_system_perspective_does_not_copy_paths(self) -> None:
        payload = impact(self.kernel, "billing_retry")
        assert payload is not None
        system = payload["perspectives"]["system"]
        self.assertEqual(set(system), {"question", "by_level", "note"})
        self.assertIn("component.invoice_worker", system["by_level"]["component"])
        self.assertNotIn("component.unrelated_mailer", system["by_level"]["component"])

    def test_spec_id_root_shares_the_walker(self) -> None:
        payload = impact(self.kernel, "component.billing_api")
        assert payload is not None
        self.assertEqual(payload["root"], "component.billing_api")
        worker = _node(payload, "component.invoice_worker")
        self.assertTrue(worker["direct"])
        self.assertEqual(worker["relationship"], "dependencies.internal")
        self.assertNotIn("component.unrelated_mailer", _ids(payload))

    def test_unknown_root_is_none(self) -> None:
        self.assertIsNone(impact(self.kernel, "capability.missing"))

    def test_cli_prints_yaml(self) -> None:
        from io import StringIO
        from contextlib import redirect_stderr, redirect_stdout

        out = StringIO()
        err = StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = cli_main(["impact", "billing_retry", "--spec-root", str(FIXTURE)])
        self.assertEqual(code, 0, err.getvalue())
        loaded = yaml.safe_load(out.getvalue())
        self.assertEqual(loaded["impact"]["root"], "change.billing_retry")
        missing = StringIO()
        with redirect_stdout(StringIO()), redirect_stderr(missing):
            code = cli_main(["impact", "capability.missing", "--spec-root", str(FIXTURE)])
        self.assertEqual(code, 1)
        self.assertIn("not found", missing.getvalue())

    def test_mcp_dispatch_matches_format(self) -> None:
        payload = impact(self.kernel, "billing_retry")
        assert payload is not None
        text = dispatch("impact", {"id": "billing_retry", "spec_root": str(FIXTURE)})
        self.assertEqual(text, format_impact(payload))

    def test_golden_membership_matches_blast(self) -> None:
        golden = load_kernel(GOLDEN)
        for spec_id in sorted(golden.by_id):
            expected = blast(golden, spec_id)
            projected = impact(golden, spec_id)
            assert expected is not None and projected is not None
            caps, comps, founds = _blast_sets(projected)
            self.assertEqual(caps, set(expected["affects"]["capabilities"]), spec_id)
            self.assertEqual(comps, set(expected["affects"]["components"]), spec_id)
            self.assertEqual(founds, set(expected["affects"]["foundations"]), spec_id)
            self.assertEqual(projected["open_changes"], expected["open_changes"], spec_id)


if __name__ == "__main__":
    unittest.main()
