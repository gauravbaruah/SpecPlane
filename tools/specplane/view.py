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
from kernel import check_sync, list_gaps, load_kernel, retrieve  # noqa: E402
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
        records[doc.spec_id] = _record(row)

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


def _record(row: dict[str, Any]) -> dict[str, Any]:
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
    return {
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


def _delta(data: dict[str, Any]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for key in DELTA_KEYS:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            out[key] = [value.strip()]
        elif isinstance(value, list):
            lines = [str(item) for item in value if str(item).strip()]
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
