"""Local command events: on by default, structural, and unable to change an exit code."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cli import main as cli_main  # noqa: E402


class TelemetryTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name)
        self._env = patch.dict(
            os.environ,
            {
                "SPECPLANE_HOME": str(self.home),
                "SPECPLANE_PROJECT_DIR": str(self.home / "repo-secret-path"),
                "SPECPLANE_TELEMETRY": "",
                "SPECPLANE_CALLER": "",
                "SPECPLANE_RUN_ID": "",
                "SPECPLANE_SESSION_ID": "",
            },
            clear=False,
        )
        self._env.start()

    def tearDown(self) -> None:
        self._env.stop()
        self._tmp.cleanup()

    def test_default_writes_an_event(self) -> None:
        from io import StringIO

        buf = StringIO()
        with patch("sys.stdout", buf):
            code = cli_main(["telemetry", "status"])
        self.assertEqual(code, 0)
        self.assertIn("telemetry: on", buf.getvalue())
        self.assertIn("source: default", buf.getvalue())
        self.assertIn("upload: never", buf.getvalue())
        raw = (self.home / "events" / "events.jsonl").read_text(encoding="utf-8")
        event = json.loads(raw.splitlines()[-1])
        self.assertEqual(event["command"], "telemetry_status")
        self.assertEqual(event["result"], "ok")
        self.assertNotIn("repo-secret-path", raw)
        self.assertNotIn("path", event)
        self.assertRegex(event["project_id"], r"^[a-f0-9]{32}$")

    def test_disabled_writes_nothing(self) -> None:
        os.environ["SPECPLANE_TELEMETRY"] = "0"
        code = cli_main(["telemetry", "status"])
        self.assertEqual(code, 0)
        self.assertFalse((self.home / "events" / "events.jsonl").exists())

    def test_enabled_event_omits_spec_id(self) -> None:
        os.environ["SPECPLANE_TELEMETRY"] = "1"
        os.environ["SPECPLANE_CALLER"] = "cursor_skill"
        os.environ["SPECPLANE_RUN_ID"] = "run_1"
        spec_id = "capability.not_in_the_event"
        code = cli_main(["retrieve", spec_id, "--spec-root", str(ROOT / "testdata" / "golden" / "messy_auth" / "specs")])
        self.assertIn(code, (0, 1))
        raw = (self.home / "events" / "events.jsonl").read_text(encoding="utf-8")
        self.assertNotIn(spec_id, raw)
        self.assertNotIn("messy_auth", raw)
        event = json.loads(raw.splitlines()[-1])
        self.assertEqual(event["command"], "retrieve")
        self.assertEqual(event["invoked_via"], "cursor_skill")
        self.assertEqual(event["run_id"], "run_1")
        self.assertEqual(event["event"], "specplane.command.completed")
        self.assertNotIn("path", event)
        self.assertIn(event["result"], ("ok", "nonzero"))

    def test_bad_caller_is_unknown(self) -> None:
        os.environ["SPECPLANE_TELEMETRY"] = "1"
        os.environ["SPECPLANE_CALLER"] = "sk-live-secret"
        os.environ["SPECPLANE_SESSION_ID"] = "../secrets"
        cli_main(["telemetry", "status"])
        raw = (self.home / "events" / "events.jsonl").read_text(encoding="utf-8")
        self.assertNotIn("sk-live-secret", raw)
        self.assertNotIn("secrets", raw)
        event = json.loads(raw.splitlines()[-1])
        self.assertEqual(event["invoked_via"], "unknown")
        self.assertNotIn("session_id", event)
        self.assertEqual(event["command"], "telemetry_status")

    def test_emit_failure_keeps_exit_code(self) -> None:
        os.environ["SPECPLANE_TELEMETRY"] = "1"
        real_open = Path.open

        def guarded(self: Path, *args, **kwargs):
            mode = args[0] if args else kwargs.get("mode", "")
            if self.name == "events.jsonl" and "a" in str(mode):
                raise OSError("disk")
            return real_open(self, *args, **kwargs)

        with patch.object(Path, "open", guarded):
            code = cli_main(["telemetry", "status"])
        self.assertEqual(code, 0)

    def test_enable_then_disable(self) -> None:
        self.assertEqual(cli_main(["telemetry", "enable"]), 0)
        self.assertIn('"enabled": true', (self.home / "telemetry.json").read_text(encoding="utf-8"))
        os.environ["SPECPLANE_TELEMETRY"] = ""
        from io import StringIO

        buf = StringIO()
        with patch("sys.stdout", buf):
            self.assertEqual(cli_main(["telemetry", "status"]), 0)
        self.assertIn("telemetry: on", buf.getvalue())
        self.assertIn("upload: never", buf.getvalue())
        self.assertEqual(cli_main(["telemetry", "disable"]), 0)
        buf = StringIO()
        with patch("sys.stdout", buf):
            self.assertEqual(cli_main(["telemetry", "status"]), 0)
        self.assertIn("telemetry: off", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
