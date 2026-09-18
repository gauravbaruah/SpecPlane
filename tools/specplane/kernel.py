"""Kernel graph: live specs + open change folders. Deterministic; no LLM."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from validate import SpecDoc, as_str_list, dig, index_by_id, load_specs, validate


LIVE_STATUSES = {
    "planned",
    "in_progress",
    "launched",
    "draft",
    "active",
    "",
}
REPLACED_STATUSES = {"deprecated", "archived"}
INFERRED_MARKERS = {"inferred"}


@dataclass
class Change:
    change_id: str
    kind: str
    status: str
    promise_ids: list[str]
    path: Path
    data: dict[str, Any] = field(default_factory=dict)

    @property
    def open(self) -> bool:
        return self.status in {"", "in-flight", "in_flight", "open"}


@dataclass
class Kernel:
    spec_root: Path
    docs: list[SpecDoc]
    by_id: dict[str, SpecDoc]
    changes: list[Change]


def load_changes(spec_root: Path) -> list[Change]:
    root = spec_root / "changes"
    if not root.is_dir():
        return []
    out: list[Change] = []
    for folder in sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")):
        proposal = folder / "proposal.yaml"
        data: dict[str, Any] = {}
        if proposal.is_file():
            loaded = yaml.safe_load(proposal.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                data = loaded
        delta_path = folder / "delta.yaml"
        if delta_path.is_file():
            delta = yaml.safe_load(delta_path.read_text(encoding="utf-8"))
            if isinstance(delta, dict):
                data = {**delta, **data}
        change_id = str(data.get("id") or data.get("change_id") or folder.name)
        kind = str(data.get("kind") or "")
        status = str(data.get("status") or "in-flight")
        promise_ids = as_str_list(data.get("promise_ids"))
        out.append(
            Change(
                change_id=change_id,
                kind=kind,
                status=status,
                promise_ids=promise_ids,
                path=folder,
                data=data,
            )
        )
    return out


def load_kernel(spec_root: Path) -> Kernel:
    spec_root = spec_root.resolve()
    docs, _findings = load_specs(spec_root)
    return Kernel(
        spec_root=spec_root,
        docs=docs,
        by_id=index_by_id(docs),
        changes=load_changes(spec_root),
    )


def bit_of(doc: SpecDoc) -> str:
    tags = {str(t).lower() for t in (doc.meta.get("tags") or []) if t}
    if tags & INFERRED_MARKERS:
        return "inferred"
    status = str(doc.meta.get("status") or "")
    if status in REPLACED_STATUSES or doc.meta.get("replaced_by"):
        return "replaced"
    if status in LIVE_STATUSES:
        return "live"
    return "live"


def leftovers_for(kernel: Kernel, spec_id: str) -> list[str]:
    found: list[str] = []
    for doc in kernel.docs:
        if str(doc.meta.get("replaced_by") or "") == spec_id:
            found.append(doc.spec_id)
        elif bit_of(doc) == "replaced" and doc.spec_id != spec_id:
            # Only attach leftovers that point at this id.
            continue
    return found


def open_changes_for(kernel: Kernel, spec_id: str) -> list[Change]:
    return [
        change
        for change in kernel.changes
        if change.open and spec_id in change.promise_ids
    ]


def slice_fields(doc: SpecDoc) -> dict[str, Any]:
    realized = doc.data.get("realized_by") if isinstance(doc.data.get("realized_by"), dict) else {}
    deps = dig(doc.data, "implementation", "dependencies", "internal")
    depended = dig(doc.data, "implementation", "depended_on_by", "components")
    return {
        "id": doc.spec_id,
        "purpose": doc.meta.get("purpose") or "",
        "level": doc.level,
        "bit": bit_of(doc),
        "responsibilities": as_str_list(doc.data.get("responsibilities")),
        "implements": as_str_list(doc.data.get("implements")),
        "uses": as_str_list(doc.data.get("uses")),
        "realized_by_components": as_str_list(realized.get("components")),
        "realized_by_containers": as_str_list(realized.get("containers")),
        "depends_on": as_str_list(deps),
        "depended_on_by": as_str_list(depended),
    }


def retrieve(kernel: Kernel, spec_id: str) -> dict[str, Any] | None:
    doc = kernel.by_id.get(spec_id)
    if not doc:
        return None
    bit = bit_of(doc)
    live_slice = slice_fields(doc) if bit == "live" else None
    replaced_self = spec_id if bit == "replaced" else None
    return {
        "id": spec_id,
        "bit": bit,
        "live": live_slice,
        "replaced": leftovers_for(kernel, spec_id)
        + ([replaced_self] if replaced_self else []),
        "in_flight": [
            {"id": c.change_id, "kind": c.kind, "path": str(c.path)}
            for c in open_changes_for(kernel, spec_id)
        ],
        "inferred_as_live": False,
    }


def _component_edges(doc: SpecDoc) -> tuple[list[str], list[str], list[str]]:
    implements = as_str_list(doc.data.get("implements"))
    uses = as_str_list(doc.data.get("uses"))
    internal = as_str_list(dig(doc.data, "implementation", "dependencies", "internal"))
    reverse = as_str_list(dig(doc.data, "implementation", "depended_on_by", "components"))
    contains = as_str_list(dig(doc.data, "relationships", "contains"))
    return implements, uses, internal + reverse + contains


def blast(kernel: Kernel, spec_id: str) -> dict[str, Any] | None:
    start = kernel.by_id.get(spec_id)
    if not start:
        return None

    capabilities: set[str] = set()
    components: set[str] = set()
    foundations: set[str] = set()
    seen_components: set[str] = set()

    def walk_component(cid: str) -> None:
        if cid in seen_components:
            return
        seen_components.add(cid)
        components.add(cid)
        doc = kernel.by_id.get(cid)
        if not doc:
            return
        implements, uses, neighbors = _component_edges(doc)
        capabilities.update(implements)
        foundations.update(uses)  # terminal: do not follow used_by
        for other in neighbors:
            if other.startswith("foundation."):
                foundations.add(other)
            elif other.startswith("capability."):
                capabilities.add(other)
            elif other.startswith("component."):
                walk_component(other)

    if start.level == "component":
        walk_component(spec_id)
    elif start.level == "capability":
        capabilities.add(spec_id)
        realized = (
            start.data.get("realized_by")
            if isinstance(start.data.get("realized_by"), dict)
            else {}
        )
        for cid in as_str_list(realized.get("components")):
            walk_component(cid)
        foundations.update(as_str_list(start.data.get("uses")))
    elif start.level == "foundation":
        foundations.add(spec_id)
        used = start.data.get("used_by") if isinstance(start.data.get("used_by"), dict) else {}
        # Blast *of* a foundation: one hop to direct users, then stop.
        for cid in as_str_list(used.get("components")):
            components.add(cid)
            doc = kernel.by_id.get(cid)
            if doc:
                capabilities.update(as_str_list(doc.data.get("implements")))
        for cid in as_str_list(used.get("containers")):
            other = kernel.by_id.get(cid)
            if other:
                capabilities.update(as_str_list(other.data.get("implements")))
    elif start.level == "container":
        capabilities.update(as_str_list(start.data.get("implements")))
        foundations.update(as_str_list(start.data.get("uses")))
        for cid in as_str_list(dig(start.data, "relationships", "contains")):
            if cid.startswith("component."):
                walk_component(cid)
    else:
        capabilities.update(as_str_list(dig(start.data, "system_context", "capabilities")))

    others = set(components)
    if start.level == "component":
        others.discard(spec_id)
    extra_caps = set(capabilities)
    if start.level == "capability":
        extra_caps.discard(spec_id)
    extra_foundations = set(foundations)
    if start.level == "foundation":
        extra_foundations.discard(spec_id)
    empty = not others and not extra_caps and not extra_foundations

    named = {spec_id} | capabilities | components | foundations
    open_hits = [
        change.change_id
        for change in kernel.changes
        if change.open and named & set(change.promise_ids)
    ]

    shown_components = set(components)
    if start.level == "component":
        shown_components.add(spec_id)

    return {
        "change": spec_id,
        "affects": {
            "capabilities": sorted(capabilities),
            "components": sorted(shown_components),
            "foundations": sorted(foundations),
        },
        "open_changes": sorted(set(open_hits)),
        "empty": empty,
        "decision_required": False,
    }


def change_covers(kernel: Kernel, change: Change, spec_id: str) -> bool:
    if spec_id in change.promise_ids:
        return True
    doc = kernel.by_id.get(spec_id)
    if not doc:
        return False
    implements = as_str_list(doc.data.get("implements"))
    if any(cap in change.promise_ids for cap in implements):
        return True
    realized = doc.data.get("realized_by") if isinstance(doc.data.get("realized_by"), dict) else {}
    for cid in as_str_list(realized.get("components")) + as_str_list(realized.get("containers")):
        if cid in change.promise_ids:
            return True
    return False


def id_covered(kernel: Kernel, spec_id: str) -> bool:
    return any(change_covers(kernel, change, spec_id) for change in kernel.changes if change.open)


def is_phase1_shaped(doc: SpecDoc) -> bool:
    """No join edges: no realized_by, uses, or component implements (Q116)."""
    realized = doc.data.get("realized_by") if isinstance(doc.data.get("realized_by"), dict) else {}
    if as_str_list(realized.get("components")) or as_str_list(realized.get("containers")):
        return False
    if as_str_list(doc.data.get("uses")):
        return False
    if as_str_list(doc.data.get("implements")):
        return False
    return True


def map_changed_files(kernel: Kernel, files: list[str]) -> list[str]:
    ids: list[str] = []
    spec_root_name = kernel.spec_root.name
    for raw in files:
        path = Path(raw)
        if path.suffix not in {".yaml", ".yml"}:
            continue
        if "changes" in path.parts:
            continue
        if spec_root_name not in path.parts and not str(path).startswith("specs/"):
            # still allow bare filenames from the spec root
            if path.stem in kernel.by_id:
                ids.append(path.stem)
            continue
        stem = path.stem
        if stem in kernel.by_id:
            ids.append(stem)
    return sorted(set(ids))


def check_sync(
    kernel: Kernel,
    changed_ids: list[str],
) -> dict[str, Any]:
    changed_ids = sorted({cid for cid in changed_ids if cid})
    phase1_advisory: list[str] = []
    linked: list[str] = []
    unknown = [cid for cid in changed_ids if cid not in kernel.by_id]
    for cid in changed_ids:
        doc = kernel.by_id.get(cid)
        if not doc:
            continue
        if is_phase1_shaped(doc):
            phase1_advisory.append(cid)
        else:
            linked.append(cid)

    uncovered = [cid for cid in linked if not id_covered(kernel, cid)]
    empty_blasts: list[str] = []
    for cid in linked:
        result = blast(kernel, cid)
        if result and result["empty"]:
            empty_blasts.append(cid)

    fail_uncovered = bool(uncovered)
    fail_empty = bool(empty_blasts)
    decision = fail_uncovered or fail_empty
    ok = not fail_uncovered and not fail_empty and not unknown
    return {
        "changed_ids": changed_ids,
        "uncovered": uncovered,
        "unknown": unknown,
        "empty_blast": empty_blasts,
        "phase1_advisory": phase1_advisory,
        "ok": ok,
        "decision_required": decision,
    }


def format_retrieve(payload: dict[str, Any]) -> str:
    lines = [f"retrieve {payload['id']}", f"bit: {payload['bit']}"]
    live = payload.get("live")
    if live and payload["bit"] != "inferred":
        lines.append("live:")
        lines.append(f"  id: {live['id']}")
        if live.get("purpose"):
            lines.append(f"  purpose: {live['purpose']}")
        for key in (
            "responsibilities",
            "implements",
            "realized_by_components",
            "realized_by_containers",
            "uses",
            "depends_on",
            "depended_on_by",
        ):
            values = live.get(key) or []
            if values:
                lines.append(f"  {key}:")
                for item in values:
                    lines.append(f"    - {item}")
    replaced = payload.get("replaced") or []
    if replaced:
        lines.append("replaced:")
        for item in replaced:
            lines.append(f"  - {item}")
    in_flight = payload.get("in_flight") or []
    if in_flight:
        lines.append("in-flight:")
        for item in in_flight:
            kind = item.get("kind") or ""
            suffix = f" ({kind})" if kind else ""
            lines.append(f"  - {item['id']}{suffix}")
    else:
        lines.append("in-flight: (none)")
    return "\n".join(lines) + "\n"


def format_blast(payload: dict[str, Any]) -> str:
    lines = [f"blast {payload['change']}", "affects:"]
    affects = payload["affects"]
    for bucket in ("capabilities", "components", "foundations"):
        values = affects.get(bucket) or []
        lines.append(f"  {bucket}:")
        if not values:
            lines.append("    (none)")
        for item in values:
            lines.append(f"    - {item}")
    opens = payload.get("open_changes") or []
    lines.append("open_changes:")
    if opens:
        for item in opens:
            lines.append(f"  - {item}")
    else:
        lines.append("  (none)")
    if payload.get("empty"):
        lines.append("empty: true")
    if payload.get("decision_required"):
        lines.append("DECISION REQUIRED")
        lines.append("  SpecPlane does not pick spec vs code.")
    return "\n".join(lines) + "\n"


def format_check_sync(payload: dict[str, Any]) -> str:
    lines = ["check_sync"]
    lines.append("changed_ids:")
    if payload["changed_ids"]:
        for item in payload["changed_ids"]:
            lines.append(f"  - {item}")
    else:
        lines.append("  (none)")
    if payload["ok"]:
        lines.append("result: pass")
        if payload.get("phase1_advisory"):
            lines.append("phase1_advisory:")
            for item in payload["phase1_advisory"]:
                lines.append(f"  - {item}")
            lines.append("  Phase 1 ids have no join edges; uncovered / empty blast do not fail.")
        return "\n".join(lines) + "\n"
    lines.append("result: fail")
    if payload["uncovered"]:
        lines.append("uncovered (no open change covers id):")
        for item in payload["uncovered"]:
            lines.append(f"  - {item}")
    if payload["empty_blast"]:
        lines.append("empty_blast:")
        for item in payload["empty_blast"]:
            lines.append(f"  - {item}")
    if payload.get("phase1_advisory"):
        lines.append("phase1_advisory:")
        for item in payload["phase1_advisory"]:
            lines.append(f"  - {item}")
    if payload["unknown"]:
        lines.append("unknown_ids:")
        for item in payload["unknown"]:
            lines.append(f"  - {item}")
    if payload.get("decision_required"):
        lines.append("DECISION REQUIRED")
        lines.append("  Named behavior moved and live spec / open change did not cover it.")
        lines.append("  SpecPlane does not stamp live.")
    return "\n".join(lines) + "\n"


def structural_validate(spec_root: Path):
    return validate(spec_root)
