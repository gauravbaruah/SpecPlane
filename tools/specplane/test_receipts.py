"""A SpecPlane · line is printed only when the command established something consequential."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kernel import (  # noqa: E402
    format_blast,
    format_check_sync,
    format_run,
    receipt_validate,
)


class ReceiptTests(unittest.TestCase):
    def test_empty_blast_names_the_gap(self) -> None:
        text = format_blast(
            {
                "change": "capability.orphan",
                "affects": {"capabilities": [], "components": [], "foundations": []},
                "open_changes": [],
                "empty": True,
            }
        )
        self.assertIn(
            "SpecPlane · blast — no declared impact. This does not mean the code is unaffected.",
            text,
        )

    def test_nonempty_blast_has_no_receipt(self) -> None:
        text = format_blast(
            {
                "change": "capability.authentication",
                "affects": {
                    "capabilities": ["capability.authentication"],
                    "components": ["component.login_api"],
                    "foundations": [],
                },
                "open_changes": [],
                "empty": False,
            }
        )
        self.assertNotIn("SpecPlane ·", text)

    def test_sync_failure_is_a_receipt(self) -> None:
        text = format_check_sync(
            {
                "ok": False,
                "change": "household-keep",
                "changed_ids": ["capability.live_capture"],
                "coverage": "fail",
                "uncovered": ["capability.live_capture"],
                "unknown": [],
                "unknown_change": "",
                "empty_blast": [],
                "phase1_advisory": [],
                "sensors": "missing",
                "sensor_rows": [],
            }
        )
        self.assertIn(
            "SpecPlane · sync check — 1 uncovered: capability.live_capture. "
            "Name them on an open change, then check_sync again.",
            text,
        )
        self.assertNotIn("caught", text.lower())

    def test_phase1_pass_admits_no_impact(self) -> None:
        text = format_check_sync(
            {
                "ok": True,
                "change": "",
                "changed_ids": ["capability.orphan"],
                "coverage": "pass",
                "uncovered": [],
                "unknown": [],
                "unknown_change": "",
                "empty_blast": [],
                "phase1_advisory": ["capability.orphan"],
                "sensors": "missing",
                "sensor_rows": [],
            }
        )
        self.assertIn("passed as Phase 1 advisory", text)
        self.assertIn("no declared impact", text)
        self.assertIn("Phase 1 is valid. No component is linked yet, so an empty impact list is a warning.", text)

    def test_declared_sensors_are_not_called_executed(self) -> None:
        text = format_check_sync(
            {
                "ok": True,
                "change": "local_command_events",
                "changed_ids": ["foundation.observability_standards"],
                "coverage": "pass",
                "uncovered": [],
                "unknown": [],
                "unknown_change": "",
                "empty_blast": [],
                "phase1_advisory": [],
                "sensors": "declared",
                "sensor_rows": [{"change": "local_command_events", "must": "A sensor."}],
            }
        )
        self.assertIn("Declared sensors were not executed.", text)
        self.assertIn("Run them with: specplane run --change local_command_events.", text)

    def test_run_pass_does_not_certify(self) -> None:
        text = format_run(
            {
                "change": "local_command_events",
                "sensors": [{"id": "on-by-default", "must": "writes", "result": "pass"}],
                "invoked": True,
            }
        )
        self.assertIn(
            "SpecPlane · run — bound checks passed. "
            "This does not certify the implementation satisfies the spec. "
            "The next human step is to say ship it, or keep editing.",
            text,
        )

    def test_run_not_executed(self) -> None:
        text = format_run(
            {
                "change": "learn",
                "sensors": [{"id": "english", "must": "Dictation continues.", "result": "not_run"}],
                "invoked": False,
            }
        )
        self.assertIn("SpecPlane · run — no bound check was executed.", text)

    def test_validate_receipt_only_on_errors(self) -> None:
        self.assertEqual(
            receipt_validate(2),
            "SpecPlane · validate — 2 error(s). Fix the errors and validate again.",
        )
        self.assertEqual(receipt_validate(0), "")


if __name__ == "__main__":
    unittest.main()
