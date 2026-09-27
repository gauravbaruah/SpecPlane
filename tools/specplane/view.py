#!/usr/bin/env python3
"""Local viewer: a read of retrieve, impact, list_gaps, and check_sync.

Generates a static site and serves it on 127.0.0.1. Does not walk the spec
tree itself, reimplement impact, or call a model.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import threading
import webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from impact import impact  # noqa: E402
from kernel import check_sync, list_gaps, load_kernel, retrieve, success_sensors  # noqa: E402
from validate import dig  # noqa: E402
from validate import resolve_spec_root  # noqa: E402

def assets_dir() -> Path:
    """Checkout keeps viewer/ beside this file. A wheel keeps it inside the bundled kit."""
    local = ROOT / "viewer"
    if (local / "app.js").is_file():
        return local
    bundled = ROOT / "_specplane_kit" / "tools" / "specplane" / "viewer"
    if (bundled / "app.js").is_file():
        return bundled
    raise FileNotFoundError("viewer assets not found next to view.py")
MERMAID_VERSION = "10.9.3"
LEVELS = ("system", "capability", "container", "component", "foundation", "change")
DELTA_KEYS = ("ADDED", "MODIFIED", "REMOVED")

PAYLOAD_GAPS: list[dict[str, str]] = []


def _branch(spec_root: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(spec_root), "rev-parse", "--abbrev-ref", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""
    return "" if out in ("", "HEAD") else out


def _opened(value: Any) -> str:
    text = value.isoformat() if hasattr(value, "isoformat") else str(value or "").strip()
    if len(text) >= 10 and text[4:5] == "-" and text[7:8] == "-":
        return text[:10]
    return ""


def build_payload(kernel: Any) -> dict[str, Any]:
    records: dict[str, Any] = {}
    for doc in sorted(kernel.docs, key=lambda item: item.spec_id):
        row = retrieve(kernel, doc.spec_id)
        if row is None:
            continue
        records[doc.spec_id] = _record(row, doc, kernel)

    changes: list[dict[str, Any]] = []
    for change in kernel.changes:
        if not change.open:
            continue
        slug = change.path.name
        sync = check_sync(kernel, list(change.promise_ids), slug)
        public = {
            "id": slug,
            "kind": change.kind,
            "why": str(change.data.get("why") or "").strip(),
            "promise_ids": list(change.promise_ids),
            "opened": _opened(change.data.get("opened")),
            "delta": _delta(change.data),
            "check_sync": {
                "coverage": sync.get("coverage"),
                "sensors": sync.get("sensors"),
                "behavior": sync.get("behavior"),
                "sensor_rows": sync.get("sensor_rows") or [],
                "ok": bool(sync.get("ok")),
            },
        }
        changes.append(public)

    impacts: dict[str, Any] = {}
    for spec_id in records:
        payload = impact(kernel, spec_id)
        if payload is not None:
            impacts[spec_id] = payload
    for change in changes:
        payload = impact(kernel, change["id"])
        if payload is not None:
            impacts["change:" + change["id"]] = payload

    for spec_id, record in records.items():
        record["projections"] = projections_for(record, impacts.get(spec_id))
    for change in changes:
        change["projections"] = change_projections(impacts.get("change:" + change["id"]))

    return {
        "records": records,
        "changes": changes,
        "gaps": list_gaps(kernel),
        "impacts": impacts,
        "payload_gaps": PAYLOAD_GAPS,
        "mermaid": MERMAID_VERSION,
        "context": {
            "spec_root": kernel.spec_root.name,
            "branch": _branch(kernel.spec_root),
        },
    }


def projections_for(record: dict[str, Any], graph: dict[str, Any] | None) -> list[str]:
    """One slot. Empty projections are omitted. Sequence is not its own tab."""
    names = ["map"]
    if _others(graph, record["id"]):
        names.append("blast")
    if record.get("links"):
        names.append("layers")
    if _journey(graph, record["id"]):
        names.append("journey")
    if record.get("diagrams"):
        names.append("diagrams")
    if _data(graph, record["id"]):
        names.append("data")
    return names


def change_projections(graph: dict[str, Any] | None) -> list[str]:
    if graph and graph.get("affected"):
        return ["blast"]
    return []


def _filled(value: Any) -> str:
    return str(value or "").strip()


def _history(doc: Any) -> dict[str, Any]:
    meta = doc.meta or {}
    history: dict[str, Any] = {}
    for key in ("version", "introduced_in", "last_updated", "owner"):
        text = _filled(meta.get(key))
        if text:
            history[key] = text
    changelog: list[dict[str, Any]] = []
    raw_log = doc.data.get("changelog")
    if isinstance(raw_log, list):
        for entry in raw_log:
            if not isinstance(entry, dict):
                continue
            date = _filled(entry.get("date"))
            summary = _filled(entry.get("summary"))
            if not date and not summary:
                continue
            item: dict[str, Any] = {"date": date, "summary": summary}
            author = _filled(entry.get("author"))
            if author:
                item["author"] = author
            if entry.get("breaking") is True:
                item["breaking"] = True
            changelog.append(item)
    if changelog:
        history["changelog"] = changelog
    refs: list[dict[str, str]] = []
    raw_refs = doc.data.get("refs")
    if isinstance(raw_refs, list):
        for ref in raw_refs:
            if not isinstance(ref, dict):
                continue
            item = {
                key: _filled(ref.get(key))
                for key in ("id", "title", "type", "path", "url")
                if _filled(ref.get(key))
            }
            if item:
                refs.append(item)
    if refs:
        history["refs"] = refs
    realization = dig(doc.data, "implementation", "realization")
    paths = realization.get("paths") if isinstance(realization, dict) else None
    if isinstance(paths, list):
        cleaned = [_filled(path) for path in paths if _filled(path)]
        if cleaned:
            history["realization_paths"] = cleaned
    return history


def _validation_checks(doc: Any) -> dict[str, Any]:
    validation = dig(doc.data, "implementation", "validation") if doc is not None else None
    if not isinstance(validation, dict):
        return {"declared": False}
    criteria = validation.get("acceptance_criteria")
    count = len([item for item in criteria if _filled(item)]) if isinstance(criteria, list) else 0
    strategy = validation.get("test_strategy")
    names = [str(name) for name, value in strategy.items() if _filled(value)] if isinstance(strategy, dict) else []
    checks: dict[str, Any] = {"declared": bool(count or names)}
    if count:
        checks["acceptance"] = count
    if names:
        checks["strategies"] = names
    return checks


def _trace(kernel: Any, doc: Any) -> dict[str, Any]:
    metrics = doc.data.get("success_metrics")
    targets = metrics.get("targets") if isinstance(metrics, dict) and isinstance(metrics.get("targets"), dict) else {}
    derived = metrics.get("derived_from") if isinstance(metrics, dict) and isinstance(metrics.get("derived_from"), dict) else {}
    emitters: dict[str, str] = {}
    raw_events = doc.data.get("analytics_events")
    if isinstance(raw_events, list):
        for event in raw_events:
            if not isinstance(event, dict):
                continue
            name = _filled(event.get("name"))
            if name:
                emitters[name] = _filled(event.get("emitted_by"))
    rows: list[dict[str, Any]] = []
    for name, value in targets.items():
        label = _filled(name)
        text = _filled(value)
        if not label or not text:
            continue
        sources = derived.get(name)
        if isinstance(sources, str):
            sources = [sources]
        measured: list[dict[str, Any]] = []
        if isinstance(sources, list):
            for source in sources:
                event = _filled(source)
                if not event:
                    continue
                emitted = emitters.get(event, "")
                item: dict[str, Any] = {"name": event}
                if emitted:
                    item["emitted_by"] = emitted
                    target = kernel.by_id.get(emitted)
                    item["checks"] = _validation_checks(target) if target is not None else {"missing": True}
                measured.append(item)
        row: dict[str, Any] = {"name": label, "value": text}
        if measured:
            row["measured_by"] = measured
        rows.append(row)
    sensors: list[dict[str, str]] = []
    for change in kernel.changes:
        if not change.open:
            continue
        for sensor in success_sensors(change):
            if sensor.get("promise") == doc.spec_id:
                sensors.append({"change": change.path.name, "must": sensor["must"]})
    trace: dict[str, Any] = {}
    if rows:
        trace["targets"] = rows
    if sensors:
        trace["sensors"] = sensors
    return trace


def _record(row: dict[str, Any], doc: Any, kernel: Any) -> dict[str, Any]:
    live = row.get("live") if isinstance(row.get("live"), dict) else None
    declared = row.get("declared") if isinstance(row.get("declared"), dict) else None
    shown = live if live is not None else declared
    links: list[dict[str, str]] = []
    if shown:
        for spec_id in shown.get("realized_by_components") or []:
            links.append({"rel": "realized_by", "id": spec_id})
        for spec_id in shown.get("realized_by_containers") or []:
            links.append({"rel": "realized_by", "id": spec_id})
        for spec_id in shown.get("implements") or []:
            links.append({"rel": "implements", "id": spec_id})
        for spec_id in shown.get("uses") or []:
            links.append({"rel": "uses", "id": spec_id})
        for spec_id in shown.get("depends_on") or []:
            links.append({"rel": "depends_on", "id": spec_id})
        for spec_id in shown.get("depended_on_by") or []:
            links.append({"rel": "depended_on_by", "id": spec_id})
    public: dict[str, Any] = {
        "id": row["id"],
        "bit": row.get("bit") or "",
        "review_state": row.get("review_state") or "",
        "status": row.get("status") or "",
        "purpose": (shown or {}).get("purpose") or "",
        "level": (shown or {}).get("level") or _level_name(row["id"]),
        "responsibilities": list((shown or {}).get("responsibilities") or []),
        "links": links,
        "diagrams": list((shown or {}).get("diagrams") or []),
        "path": (shown or {}).get("path") or "",
        "in_flight": [
            {"id": item.get("id"), "kind": item.get("kind") or ""}
            for item in (row.get("in_flight") or [])
        ],
        "live_slice": live is not None,
        "inferred_as_live": bool(row.get("inferred_as_live")),
    }
    replaced_by = _filled((doc.meta or {}).get("replaced_by"))
    if replaced_by:
        public["replaced_by"] = replaced_by
    history = _history(doc)
    if history:
        public["history"] = history
    trace = _trace(kernel, doc)
    if trace:
        public["trace"] = trace
    return public


def _delta_line(item: Any) -> dict[str, str] | None:
    if isinstance(item, str):
        text = item.strip()
        return {"text": text} if text else None
    if not isinstance(item, dict):
        return None
    spec_id = str(item.get("id") or "").strip()
    text = str(item.get("summary") or item.get("text") or "").strip()
    line: dict[str, str] = {}
    if spec_id:
        line["id"] = spec_id
    if text:
        line["text"] = text
    return line or None


def _delta(data: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = {}
    for key in DELTA_KEYS:
        value = data.get(key)
        lines: list[dict[str, str]] = []
        if isinstance(value, str):
            line = _delta_line(value)
            if line:
                lines.append(line)
        elif isinstance(value, list):
            for item in value:
                line = _delta_line(item)
                if line:
                    lines.append(line)
        elif isinstance(value, dict):
            for group, items in value.items():
                group_name = str(group).strip()
                seq = items if isinstance(items, list) else [items]
                for item in seq:
                    line = _delta_line(item)
                    if not line:
                        continue
                    if group_name:
                        line = {**line, "group": group_name}
                    lines.append(line)
        if lines:
            out[key] = lines
    return out


def _others(graph: dict[str, Any] | None, spec_id: str) -> bool:
    if not graph:
        return False
    return any(str(node.get("id")) != spec_id for node in graph.get("affected") or [])


def _data(graph: dict[str, Any] | None, spec_id: str) -> bool:
    if not graph:
        return False
    contracts = ((graph.get("perspectives") or {}).get("quality") or {}).get("contracts") or []
    return any(
        item.get("subject") == spec_id and item.get("kind") == "data_models" and item.get("models")
        for item in contracts
    )


def _journey(graph: dict[str, Any] | None, spec_id: str) -> bool:
    if not graph:
        return False
    perspectives = graph.get("perspectives") or {}
    product = (perspectives.get("product") or {}).get("items") or []
    if any(item.get("subject") == spec_id and item.get("kind") == "flow" for item in product):
        return True
    journeys = (perspectives.get("quality") or {}).get("journeys") or []
    return any(item.get("subject") == spec_id for item in journeys)


def _level_name(spec_id: str) -> str:
    for name in LEVELS:
        if spec_id.startswith(name + "."):
            return name
    return ""


def write_payload(payload: dict[str, Any], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "payload.js").write_text(
        "window.SPECPLANE_VIEW = " + json.dumps(payload, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )


def write_site(payload: dict[str, Any], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for name in ("index.html", "app.js", "app.css", "logo.png"):
        shutil.copy2(assets_dir() / name, out / name)
    for folder in ("vendor", "fonts"):
        src = assets_dir() / folder
        if not src.is_dir():
            continue
        dest = out / folder
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
    write_payload(payload, out)


def _spec_mtime(spec_root: Path) -> float:
    latest = spec_root.stat().st_mtime if spec_root.exists() else 0.0
    if not spec_root.is_dir():
        return latest
    for path in spec_root.rglob("*"):
        try:
            latest = max(latest, path.stat().st_mtime)
        except OSError:
            continue
    return latest


_refresh_lock = threading.Lock()


def refresh_payload(spec_root: Path, out: Path) -> bool:
    """Rewrite payload.js when the spec root is newer than the generated file."""
    payload_path = out / "payload.js"
    if payload_path.is_file() and _spec_mtime(spec_root) <= payload_path.stat().st_mtime:
        return False
    with _refresh_lock:
        if payload_path.is_file() and _spec_mtime(spec_root) <= payload_path.stat().st_mtime:
            return False
        write_payload(build_payload(load_kernel(spec_root)), out)
        return True


def serve(out: Path, open_browser: bool, spec_root: Path | None = None) -> int:
    out = out.resolve()

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, directory=str(out), **kwargs)

        def do_GET(self) -> None:
            if spec_root is not None:
                refresh_payload(spec_root, out)
            super().do_GET()

        def end_headers(self) -> None:
            path = self.path.split("?", 1)[0]
            if path in ("/", "/index.html", "/payload.js"):
                self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def log_message(self, fmt: str, *args: Any) -> None:
            return

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    host, port = httpd.server_address
    url = f"http://{host}:{port}/"
    sys.stdout.write(url + "\n")
    sys.stdout.flush()
    if open_browser:
        webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        return 0
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Human readout of retrieve. Local and read-only.")
    parser.add_argument("--spec-root", type=Path, default=None)
    parser.add_argument("--config-dir", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, default=None, help="Output directory (default: .specplane/view)")
    parser.add_argument("--open", action="store_true", dest="open_browser", help="Also launch the browser")
    args = parser.parse_args(argv)

    spec_root = resolve_spec_root(args.spec_root, args.config_dir)
    if not spec_root.is_dir():
        sys.stderr.write(f"spec root does not exist: {spec_root} (pass --spec-root)\n")
        return 1
    out = args.out if args.out is not None else args.config_dir / ".specplane" / "view"
    kernel = load_kernel(spec_root)
    write_site(build_payload(kernel), out)
    return serve(out, args.open_browser, spec_root)


if __name__ == "__main__":
    sys.exit(main())
