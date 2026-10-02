"""Local command events. On unless a human disables them. Nothing is uploaded.

The CLI records that a command ran. It does not record spec text, ids, paths,
filenames, prompts, diffs, or environment values.
"""

from __future__ import annotations

import calendar
import json
import os
import re
import time
import uuid
from pathlib import Path

VERSION = "0.1.0a1"

_CALLERS = frozenset(
    {
        "cursor_skill",
        "claude_skill",
        "codex_skill",
        "cursor_rule",
        "human_cli",
        "github_action",
        "pre_commit_hook",
        "mcp",
    }
)
_TOKEN = re.compile(r"^[A-Za-z0-9_.:-]{1,64}$")
_COMMANDS = frozenset(
    {
        "validate",
        "retrieve",
        "context",
        "blast",
        "impact",
        "check_sync",
        "reconcile",
        "list_gaps",
        "run",
        "promote",
        "init",
        "uninstall",
        "view",
        "mcp",
        "telemetry",
        "telemetry_status",
        "telemetry_show",
        "telemetry_enable",
        "telemetry_disable",
        "usage",
    }
)
_WINDOW_S = 30 * 24 * 60 * 60
_DAY_S = 24 * 60 * 60
_STAR_AFTER_S = 2 * _DAY_S
_REMIND_AFTER_S = 7 * _DAY_S
STAR_URL = "https://github.com/gauravbaruah/SpecPlane"
ISSUE_URL = "https://github.com/gauravbaruah/SpecPlane/issues/new"
_ON = frozenset({"1", "on", "true", "yes"})
_OFF = frozenset({"0", "off", "false", "no"})


def project_root(start: Path | None = None) -> Path | None:
    """Directory this command belongs to. Not written into an event."""
    raw = os.environ.get("SPECPLANE_PROJECT_DIR", "").strip()
    if raw:
        path = Path(raw).expanduser()
        try:
            path.mkdir(parents=True, exist_ok=True)
        except OSError:
            return None
        return path
    origin = (start or Path.cwd()).resolve()
    for candidate in (origin, *origin.parents):
        if (candidate / "specplane.config.json").is_file():
            return candidate
    return origin


def project_token(root: Path | None = None) -> str | None:
    """Opaque id for this project. The repository name and path are not stored."""
    home = root if root is not None else project_root()
    if home is None:
        return None
    path = home / ".specplane" / "project_id"
    try:
        if path.is_file():
            existing = path.read_text(encoding="utf-8").strip()
            if _TOKEN.fullmatch(existing):
                return existing
        path.parent.mkdir(parents=True, exist_ok=True)
        fresh = uuid.uuid4().hex
        path.write_text(fresh + "\n", encoding="utf-8")
        return fresh
    except OSError:
        return None


def specplane_home() -> Path:
    raw = os.environ.get("SPECPLANE_HOME", "").strip()
    if raw:
        return Path(raw).expanduser()
    return Path.home() / ".specplane"


def _config_path() -> Path:
    return specplane_home() / "telemetry.json"


def _events_path() -> Path:
    return specplane_home() / "events" / "events.jsonl"


def _env_override() -> str | None:
    raw = os.environ.get("SPECPLANE_TELEMETRY", "").strip().lower()
    if raw in _ON:
        return "on"
    if raw in _OFF:
        return "off"
    return None


def _stored_enabled() -> bool | None:
    path = _config_path()
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict) or "enabled" not in data:
        return None
    return bool(data.get("enabled"))


def enabled() -> bool:
    override = _env_override()
    if override == "on":
        return True
    if override == "off":
        return False
    stored = _stored_enabled()
    if stored is None:
        return True
    return stored


def set_enabled(on: bool) -> None:
    home = specplane_home()
    home.mkdir(parents=True, exist_ok=True)
    _config_path().write_text(json.dumps({"enabled": bool(on)}) + "\n", encoding="utf-8")


def _token(name: str) -> str | None:
    raw = os.environ.get(name, "").strip()
    if raw and _TOKEN.fullmatch(raw):
        return raw
    return None


def _caller() -> str:
    raw = os.environ.get("SPECPLANE_CALLER", "").strip()
    if not raw:
        return "unknown"
    if raw in _CALLERS:
        return raw
    return "unknown"


def _installation_id() -> str:
    path = specplane_home() / "installation_id"
    try:
        if path.is_file():
            existing = path.read_text(encoding="utf-8").strip()
            if _TOKEN.fullmatch(existing):
                return existing
        home = specplane_home()
        home.mkdir(parents=True, exist_ok=True)
        fresh = uuid.uuid4().hex
        path.write_text(fresh + "\n", encoding="utf-8")
        return fresh
    except OSError:
        return "unknown"


def event_count() -> int:
    path = _events_path()
    if not path.is_file():
        return 0
    try:
        return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    except OSError:
        return 0


def read_events() -> str:
    path = _events_path()
    if not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def activity_mtime() -> float:
    """Newest local telemetry file. The viewer refreshes when this moves."""
    latest = 0.0
    for path in (_events_path(), _config_path()):
        try:
            latest = max(latest, path.stat().st_mtime)
        except OSError:
            continue
    return latest


def _event_time(raw: object) -> float | None:
    text = str(raw or "").strip()
    try:
        return float(calendar.timegm(time.strptime(text, "%Y-%m-%dT%H:%M:%SZ")))
    except (TypeError, ValueError):
        return None


def _for_project(item: dict[str, object], project_id: str | None) -> bool:
    if project_id is None:
        return True
    token = str(item.get("project_id") or "")
    return bool(project_id) and token == project_id and bool(_TOKEN.fullmatch(token))


def _asks(oldest: float | None, moment: float, scoped: bool) -> dict[str, object]:
    age = None if oldest is None else moment - oldest
    return {
        "star": bool(scoped and age is not None and age >= _STAR_AFTER_S),
        "remind": bool(scoped and age is not None and age >= _REMIND_AFTER_S),
        "star_url": STAR_URL,
        "issue_url": ISSUE_URL,
    }


def activity_summary(now: float | None = None, *, project_id: str | None = None) -> dict[str, object]:
    """Last-30-day counts. No ids, paths, or a claim that an agent fixed anything.

    Pass project_id to count one project. Events with no matching attribution are omitted.
    """
    scoped = project_id is not None
    if not enabled():
        lines = ["Local command events are off."]
        payload: dict[str, object] = {"enabled": False, "lines": lines, "text": "\n".join(lines)}
        payload.update(_asks(None, 0, False))
        return payload
    moment = time.time() if now is None else now
    cutoff = moment - _WINDOW_S
    commands: dict[str, list[tuple[float, str]]] = {}
    callers: dict[str, int] = {}
    oldest: float | None = None
    for line in read_events().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(item, dict) or not _for_project(item, project_id):
            continue
        when = _event_time(item.get("timestamp"))
        if when is None or when > moment + 60:
            continue
        if oldest is None or when < oldest:
            oldest = when
        if when < cutoff:
            continue
        command = str(item.get("command") or "")
        if command not in _COMMANDS:
            continue
        result = "ok" if str(item.get("result") or "") == "ok" else "nonzero"
        commands.setdefault(command, []).append((when, result))
        caller = str(item.get("invoked_via") or "")
        if caller not in _CALLERS:
            caller = "unknown"
        callers[caller] = callers.get(caller, 0) + 1
    asks = _asks(oldest, moment, scoped)
    if not commands:
        empty = (
            "No local events for this project in the last 30 days."
            if scoped
            else "No local events in the last 30 days."
        )
        lines = [empty]
        payload = {"enabled": True, "lines": lines, "text": "\n".join(lines)}
        payload.update(asks)
        return payload
    lines = [
        "SpecPlane on this project — last 30 days"
        if scoped
        else "SpecPlane on this machine — last 30 days"
    ]
    for name in sorted(commands):
        rows = commands[name]
        ok = sum(1 for _when, result in rows if result == "ok")
        bad = len(rows) - ok
        text = f"{name} {len(rows)} · {ok} ok"
        if bad:
            text += f" · {bad} nonzero"
        lines.append(text)
    if callers:
        parts = [
            f"{'unattributed' if name == 'unknown' else name} {callers[name]}"
            for name in sorted(callers)
        ]
        lines.append("caller · " + " · ".join(parts))
    for name in sorted(commands):
        saw_bad = False
        recoveries = 0
        for _when, result in sorted(commands[name]):
            if result == "nonzero":
                saw_bad = True
            elif saw_bad:
                recoveries += 1
                saw_bad = False
        if recoveries:
            lines.append(f"{name} nonzero, then later ok · {recoveries}")
    payload = {"enabled": True, "lines": lines, "text": "\n".join(lines)}
    payload.update(asks)
    return payload


def status_lines() -> list[str]:
    state = "on" if enabled() else "off"
    lines = [f"telemetry: {state}", "upload: never"]
    if _env_override() is not None:
        lines.append("source: SPECPLANE_TELEMETRY")
    elif _stored_enabled() is not None:
        lines.append("source: telemetry.json")
    else:
        lines.append("source: default")
    lines.append(f"events: {event_count()}")
    return lines


def record_command(command: str, exit_code: int, started: float) -> None:
    """Append one structural event. Never raises. No-op when telemetry is off."""
    try:
        if not enabled():
            return
        if not _TOKEN.fullmatch(command):
            command = "unknown"
        duration_ms = max(0, int((time.perf_counter() - started) * 1000))
        payload: dict[str, object] = {
            "event": "specplane.command.completed",
            "event_id": uuid.uuid4().hex,
            "installation_id": _installation_id(),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "specplane_version": VERSION,
            "command": command,
            "invoked_via": _caller(),
            "duration_ms": duration_ms,
            "exit_code": int(exit_code),
            "result": "ok" if int(exit_code) == 0 else "nonzero",
        }
        session = _token("SPECPLANE_SESSION_ID")
        if session:
            payload["session_id"] = session
        run = _token("SPECPLANE_RUN_ID")
        if run:
            payload["run_id"] = run
        project = project_token()
        if project:
            payload["project_id"] = project
        path = _events_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")
    except Exception:
        return
