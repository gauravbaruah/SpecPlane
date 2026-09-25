#!/usr/bin/env python3
"""Local viewer: a read of retrieve, impact, list_gaps, and check_sync.

Generates a static site and serves it on 127.0.0.1. Does not walk the spec
tree itself, reimplement impact, or call a model.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
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

PAYLOAD_GAPS = [
    {
        "desired": "Diagrams projection, including sequence diagrams the record holds",
        "missing": "retrieve and impact do not return declared diagram source (Mermaid text, type, or flow_ref on a diagram)",
        "smallest": "Add declared diagrams to the retrieve or impact payload for the selected id",
    },
    {
        "desired": "Data projection of entity and schema relationships",
        "missing": "impact quality contracts do not include data_models",
        "smallest": "Project implementation.contracts.data_models on the quality or a dedicated impact field",
    },
    {
        "desired": "Journey with branches, loops, and endings taken from a declared flowchart",
        "missing": "impact flow items carry id, goal, and kinds; quality journeys carry exceptions and recovery text, not stages or a graph",
        "smallest": "Return flow stages and any declared flowchart on the product projection",
    },
    {
        "desired": "Source fold naming the spec file",
        "missing": "retrieve does not include the file path",
        "smallest": "Add the spec path to retrieve",
    },
    {
        "desired": "Purpose and responsibilities on an inferred id",
        "missing": "retrieve returns no live slice when bit is inferred",
        "smallest": "Return a non-live slice for inferred ids, still marked inferred",
    },
]


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
    return names


def change_projections(graph: dict[str, Any] | None) -> list[str]:
    if graph and graph.get("affected"):
        return ["blast"]
    return []


def _record(row: dict[str, Any]) -> dict[str, Any]:
    live = row.get("live") if isinstance(row.get("live"), dict) else None
    links: list[dict[str, str]] = []
    if live:
        for spec_id in live.get("realized_by_components") or []:
            links.append({"rel": "realized_by", "id": spec_id})
        for spec_id in live.get("realized_by_containers") or []:
            links.append({"rel": "realized_by", "id": spec_id})
        for spec_id in live.get("implements") or []:
            links.append({"rel": "implements", "id": spec_id})
        for spec_id in live.get("uses") or []:
            links.append({"rel": "uses", "id": spec_id})
        for spec_id in live.get("depends_on") or []:
            links.append({"rel": "depends_on", "id": spec_id})
        for spec_id in live.get("depended_on_by") or []:
            links.append({"rel": "depended_on_by", "id": spec_id})
    return {
        "id": row["id"],
        "bit": row.get("bit") or "",
        "review_state": row.get("review_state") or "",
        "status": row.get("status") or "",
        "purpose": (live or {}).get("purpose") or "",
        "level": (live or {}).get("level") or _level_name(row["id"]),
        "responsibilities": list((live or {}).get("responsibilities") or []),
        "links": links,
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


def write_site(payload: dict[str, Any], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for name in ("index.html", "app.js", "app.css"):
        shutil.copy2(assets_dir() / name, out / name)
    vendor_src = assets_dir() / "vendor"
    if vendor_src.is_dir():
        dest = out / "vendor"
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(vendor_src, dest)
    (out / "payload.js").write_text(
        "window.SPECPLANE_VIEW = " + json.dumps(payload, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )


def serve(out: Path, open_browser: bool) -> int:
    out = out.resolve()

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, directory=str(out), **kwargs)

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
    return serve(out, args.open_browser)


if __name__ == "__main__":
    sys.exit(main())
