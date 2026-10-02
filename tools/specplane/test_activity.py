"""Activity is last-30-day counts from the local log. It does not upload."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from telemetry import activity_summary  # noqa: E402


def _stamp(offset_s: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + offset_s))


class ActivityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)
        self._old_home = os.environ.get("SPECPLANE_HOME")
        self._old_tel = os.environ.get("SPECPLANE_TELEMETRY")
        os.environ["SPECPLANE_HOME"] = str(self.home)
        os.environ["SPECPLANE_TELEMETRY"] = "1"

    def tearDown(self) -> None:
        if self._old_home is None:
            os.environ.pop("SPECPLANE_HOME", None)
        else:
            os.environ["SPECPLANE_HOME"] = self._old_home
        if self._old_tel is None:
            os.environ.pop("SPECPLANE_TELEMETRY", None)
        else:
            os.environ["SPECPLANE_TELEMETRY"] = self._old_tel
        self.tmp.cleanup()

    def _write(self, rows: list[dict[str, object]]) -> None:
        path = self.home / "events" / "events.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        body = "".join(json.dumps(row) + "\n" for row in rows)
        path.write_text(body, encoding="utf-8")

    def test_counts_only(self) -> None:
        self._write(
            [
                {
                    "command": "retrieve",
                    "result": "ok",
                    "invoked_via": "cursor_skill",
                    "timestamp": _stamp(-10),
                    "spec_id": "capability.secret_id",
                    "path": "src/secret.py",
                },
                {
                    "command": "validate",
                    "result": "ok",
                    "invoked_via": "not-a-label",
                    "timestamp": _stamp(-8),
                },
                {
                    "command": "capability.secret_id",
                    "result": "ok",
                    "invoked_via": "cursor_skill",
                    "timestamp": _stamp(-5),
                    "path": "src/secret.py",
                },
            ]
        )
        text = str(activity_summary()["text"])
        self.assertIn("retrieve 1 · 1 ok", text)
        self.assertIn("caller · cursor_skill 1 · unattributed 1", text)
        self.assertNotIn("not-a-label", text)
        self.assertNotIn("unknown", text)
        self.assertNotIn("capability.secret_id", text)
        self.assertNotIn("src/secret.py", text)
        self.assertNotIn("prompt", text)

    def test_copy_does_not_post(self) -> None:
        script = (ROOT / "viewer" / "app.js").read_text(encoding="utf-8")
        server = (ROOT / "view.py").read_text(encoding="utf-8")
        self.assertIn("navigator.clipboard.writeText", script)
        self.assertIn("activity.text", script)
        self.assertIn("What it does", script)
        self.assertIn("What ok means", script)
        self.assertIn("What a nonzero exit means", script)
        self.assertIn("That is the order of the exits.", script)
        self.assertIn("Returns the live promise for one id", script)
        self.assertIn("Runs checks already bound on one change", script)
        self.assertIn("A changed id had no open change covering it", script)
        self.assertIn("unattributed means that variable was not set", script)
        self.assertIn("It is not a failed check.", script)
        self.assertNotIn("allowlisted", script)
        self.assertNotIn("caught", script)
        self.assertNotIn("corrected", script)
        for needle in ("fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "urllib"):
            self.assertNotIn(needle, script)
            self.assertNotIn(needle, server)

    def test_sequence_is_not_a_catch(self) -> None:
        self._write(
            [
                {
                    "command": "check_sync",
                    "result": "nonzero",
                    "invoked_via": "cursor_skill",
                    "timestamp": _stamp(-30),
                },
                {
                    "command": "check_sync",
                    "result": "ok",
                    "invoked_via": "cursor_skill",
                    "timestamp": _stamp(-10),
                },
            ]
        )
        text = str(activity_summary()["text"])
        self.assertIn("check_sync nonzero, then later ok · 1", text)
        lowered = text.lower()
        for word in ("caught", "corrected", "constraint", "override", "fixed"):
            self.assertNotIn(word, lowered)

    def test_empty_and_off(self) -> None:
        self.assertEqual(
            activity_summary()["text"],
            "No local events in the last 30 days.",
        )
        self._write(
            [
                {
                    "command": "run",
                    "result": "ok",
                    "invoked_via": "human_cli",
                    "timestamp": _stamp(-10),
                }
            ]
        )
        os.environ["SPECPLANE_TELEMETRY"] = "0"
        self.assertEqual(activity_summary()["text"], "Local command events are off.")
        self.assertFalse(activity_summary(project_id="abc")["star"])
        self.assertFalse(activity_summary(project_id="abc")["remind"])

    def _row(self, command: str, project: str | None, age_s: float) -> dict[str, object]:
        row: dict[str, object] = {
            "command": command,
            "result": "ok",
            "invoked_via": "human_cli",
            "timestamp": _stamp(-age_s),
        }
        if project is not None:
            row["project_id"] = project
        return row

    def test_project_counts_omit_other_projects(self) -> None:
        self._write(
            [
                self._row("retrieve", "proj-a", 10),
                self._row("blast", "proj-b", 10),
                self._row("validate", None, 10),
                self._row("run", "src/secret.py", 10),
            ]
        )
        text = str(activity_summary(project_id="proj-a")["text"])
        self.assertIn("SpecPlane on this project — last 30 days", text)
        self.assertIn("retrieve 1 · 1 ok", text)
        self.assertNotIn("blast", text)
        self.assertNotIn("validate", text)
        self.assertNotIn("run", text)
        self.assertNotIn("src/secret.py", text)
        self.assertNotIn("proj-a", text)

    def test_star_after_two_days(self) -> None:
        self._write([self._row("retrieve", "proj-a", 3 * 24 * 60 * 60)])
        summary = activity_summary(project_id="proj-a")
        self.assertTrue(summary["star"])
        self.assertFalse(summary["remind"])
        self.assertEqual(summary["star_url"], "https://github.com/gauravbaruah/SpecPlane")

    def test_reminder_after_seven_days(self) -> None:
        self._write([self._row("retrieve", "proj-a", 8 * 24 * 60 * 60)])
        summary = activity_summary(project_id="proj-a")
        self.assertTrue(summary["star"])
        self.assertTrue(summary["remind"])
        self.assertEqual(
            summary["issue_url"],
            "https://github.com/gauravbaruah/SpecPlane/issues/new",
        )
        self.assertNotIn("proj-a", str(summary["text"]))

    def test_quiet_before_two_days(self) -> None:
        self._write([self._row("retrieve", "proj-a", 60 * 60)])
        summary = activity_summary(project_id="proj-a")
        self.assertFalse(summary["star"])
        self.assertFalse(summary["remind"])
        script = (ROOT / "viewer" / "app.js").read_text(encoding="utf-8")
        self.assertIn("https://github.com/gauravbaruah/SpecPlane", script)
        self.assertIn("https://github.com/gauravbaruah/SpecPlane/issues/new", script)
        self.assertIn("This project on this machine", script)
        self.assertNotIn("mailto:", script)
        lowered = script.lower()
        self.assertNotIn("email", lowered)


if __name__ == "__main__":
    unittest.main()
