"""Kernel graph: live specs + open change folders. Deterministic; no LLM."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import date
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
# Capability Phase 1 lists. data_classification is a label, not a promise sentence.
CONSTRAINT_LIST_KEYS = ("legal", "security", "ux")


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
        if folder.name == "_archive":
            continue
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


def change_statements_for(change: Change, spec_id: str) -> list[str]:
    """Delta sentences for this id. The live slice is not rewritten."""

    def rows_for(only_id: str | None) -> list[str]:
        found: list[str] = []
        for key in ("ADDED", "MODIFIED", "REMOVED"):
            rows = change.data.get(key) or []
            if not isinstance(rows, list):
                continue
            for item in rows:
                if not isinstance(item, dict):
                    continue
                row_id = str(item.get("id") or "").strip()
                summary = " ".join(str(item.get("summary") or "").split())
                if only_id and row_id != only_id:
                    continue
                if not row_id and not summary:
                    continue
                found.append(f"{key} {row_id}: {summary}".strip())
        return found

    matched = rows_for(spec_id)
    return matched or rows_for(None)


def _relative_spec_path(spec_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(spec_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _declared_diagrams(doc: SpecDoc) -> list[dict[str, str]]:
    raw = doc.data.get("diagrams")
    if not isinstance(raw, list):
        return []
    diagrams: list[dict[str, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        row: dict[str, str] = {}
        for key in ("type", "title", "description", "mermaid"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                row[key] = value.strip()
        if row.get("type") or row.get("mermaid"):
            diagrams.append(row)
    return diagrams


def authored_constraint_lists(doc: SpecDoc) -> dict[str, list[str]]:
    """Legal, security, and ux sentences as authored. Omits empty lists and scalars."""
    raw = doc.data.get("constraints")
    if not isinstance(raw, dict):
        return {}
    lists: dict[str, list[str]] = {}
    for key in CONSTRAINT_LIST_KEYS:
        value = raw.get(key)
        if not isinstance(value, list):
            continue
        texts = as_str_list(value)
        if texts:
            lists[key] = texts
    return lists


def slice_fields(doc: SpecDoc, spec_root: Path | None = None) -> dict[str, Any]:
    realized = doc.data.get("realized_by") if isinstance(doc.data.get("realized_by"), dict) else {}
    deps = dig(doc.data, "implementation", "dependencies", "internal")
    depended = dig(doc.data, "implementation", "depended_on_by", "components")
    fields: dict[str, Any] = {
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
    constraints = authored_constraint_lists(doc)
    if constraints:
        fields["constraints"] = constraints
    if spec_root is not None:
        fields["path"] = _relative_spec_path(spec_root, doc.path)
    diagrams = _declared_diagrams(doc)
    if diagrams:
        fields["diagrams"] = diagrams
    return fields


def retrieve(kernel: Kernel, spec_id: str) -> dict[str, Any] | None:
    doc = kernel.by_id.get(spec_id)
    if not doc:
        return None
    bit = bit_of(doc)
    fields = slice_fields(doc, kernel.spec_root)
    live_slice = fields if bit == "live" else None
    declared = fields if bit == "inferred" else None
    replaced_self = spec_id if bit == "replaced" else None
    payload: dict[str, Any] = {
        "id": spec_id,
        "bit": bit,
        "review_state": str(doc.meta.get("review_state") or ""),
        "status": str(doc.meta.get("status") or ""),
        "live": live_slice,
        "replaced": leftovers_for(kernel, spec_id)
        + ([replaced_self] if replaced_self else []),
        "in_flight": [
            {
                "id": c.change_id,
                "kind": c.kind,
                "path": str(c.path),
                "statements": change_statements_for(c, spec_id),
            }
            for c in open_changes_for(kernel, spec_id)
        ],
        "inferred_as_live": False,
    }
    if declared is not None:
        payload["declared"] = declared
    if bit == "live" and payload["in_flight"] and is_phase1_shaped(doc):
        payload["readiness"] = (
            "Implementation is underway and no implementation relationships are declared."
        )
    return payload


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


def id_covered(
    kernel: Kernel, spec_id: str, only: Change | None = None
) -> bool:
    if only is not None:
        return change_covers(kernel, only, spec_id)
    return any(change_covers(kernel, change, spec_id) for change in kernel.changes if change.open)


def resolve_open_change(kernel: Kernel, slug: str) -> Change | None:
    for change in kernel.changes:
        if change.open and change.path.name == slug:
            return change
    return None


def success_sensors(change: Change) -> list[dict[str, str]]:
    path = change.path / "success.yaml"
    if not path.is_file():
        return []
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        return []
    sensors = loaded.get("sensors") or []
    if not isinstance(sensors, list):
        return []
    out: list[dict[str, str]] = []
    for row in sensors:
        if not isinstance(row, dict):
            continue
        must = str(row.get("must") or "").strip()
        if not must:
            continue
        item = {
            "must": must,
            "promise": str(row.get("promise") or "").strip(),
            "evidence": evidence_label(row),
        }
        sensor_id = str(row.get("id") or "").strip()
        if sensor_id:
            item["id"] = sensor_id
        out.append(item)
    return out


def evidence_label(row: dict[str, Any]) -> str:
    """The bound command, or none. Does not run it."""
    parts: list[str] = []
    run = row.get("run")
    if isinstance(run, dict):
        for key in ("unittest", "test"):
            text = str(run.get(key) or "").strip()
            if text:
                parts.append(text)
        argv = run.get("argv")
        if isinstance(argv, list) and argv and all(isinstance(part, str) for part in argv):
            parts.append(" ".join(argv))
    test = row.get("test")
    if isinstance(test, str) and test.strip():
        parts.append(test.strip())
    return " | ".join(parts) if parts else "none"


def status_for_result(result: str) -> str:
    if result == "pass":
        return "VERIFIED"
    if result in {"fail", "error"}:
        return "FAILED"
    return "UNVERIFIED"


def success_must_lines(change: Change) -> list[str]:
    return [row["must"] for row in success_sensors(change)]


def covering_changes(
    kernel: Kernel, changed_ids: list[str], scoped: Change | None
) -> list[Change]:
    if scoped is not None:
        return [scoped]
    found: list[Change] = []
    seen: set[str] = set()
    for cid in changed_ids:
        for change in kernel.changes:
            if not change.open or change.path.name in seen:
                continue
            if change_covers(kernel, change, cid):
                seen.add(change.path.name)
                found.append(change)
    return found


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


_NON_APP_DIR_PREFIXES = (
    "specs/",
    "docs/",
    "design-docs/",
    "legacy/",
    ".github/",
    ".cursor/",
    ".agents/",
)
_NON_APP_SUFFIXES = (".md", ".png", ".gif", ".svg", ".jpg", ".jpeg", ".webp", ".ico")

RECONCILE_NOTE = (
    "SpecPlane compared declared paths to the tree. "
    "It did not parse source or pick spec vs code."
)


def _norm_rel(path: str) -> str:
    text = str(path).strip().replace("\\", "/")
    while text.startswith("./"):
        text = text[2:]
    return text


def _escapes_repo(path: str) -> bool:
    if not path or path.startswith("/") or path.startswith("~"):
        return True
    return any(part == ".." for part in path.split("/"))


def _is_app_file(path: str) -> bool:
    rel = _norm_rel(path)
    if not rel or rel.endswith("/"):
        return False
    first = rel.split("/", 1)[0]
    if first.startswith("."):
        return False
    if any(rel.startswith(prefix) for prefix in _NON_APP_DIR_PREFIXES):
        return False
    return not rel.endswith(_NON_APP_SUFFIXES)


def _declared_matches(declared: str, changed: str) -> bool:
    dec = _norm_rel(declared)
    ch = _norm_rel(changed)
    if not dec or not ch or _escapes_repo(dec) or _escapes_repo(ch):
        return False
    if dec.endswith("/"):
        return ch.startswith(dec)
    return ch == dec


def _declared_present(repo: Path, declared: str) -> bool:
    dec = _norm_rel(declared)
    if not dec or _escapes_repo(dec):
        return False
    rel = dec[:-1] if dec.endswith("/") else dec
    target = repo.joinpath(*[part for part in rel.split("/") if part])
    try:
        target.resolve().relative_to(repo.resolve())
    except ValueError:
        return False
    if dec.endswith("/"):
        return target.is_dir()
    return target.is_file()


def component_realization_paths(kernel: Kernel) -> list[tuple[str, str]]:
    """(component id, declared path) from implementation.realization.paths.

    Components only. Replaced specs are skipped. Paths are not rewritten.
    """
    rows: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for doc in kernel.docs:
        if doc.level != "component" or bit_of(doc) == "replaced":
            continue
        raw = dig(doc.data, "implementation", "realization", "paths")
        for path in as_str_list(raw):
            key = (doc.spec_id, path)
            if key in seen:
                continue
            seen.add(key)
            rows.append(key)
    return rows


def reconcile(
    kernel: Kernel,
    changed_files: list[str],
    *,
    repo: Path,
) -> dict[str, Any]:
    """Compare declared paths to the tree and to changed paths.

    Does not read file bodies and does not write.
    """
    repo = repo.resolve()
    declared = component_realization_paths(kernel)
    changed = []
    seen_changed: set[str] = set()
    for raw in changed_files:
        rel = _norm_rel(raw)
        if not rel or rel in seen_changed:
            continue
        seen_changed.add(rel)
        changed.append(rel)

    missing: list[dict[str, str]] = []
    for spec_id, path in declared:
        if not _declared_present(repo, path):
            missing.append({"id": spec_id, "path": _norm_rel(path) or path})
    missing.sort(key=lambda row: (row["id"], row["path"]))

    mapped: list[dict[str, str]] = []
    mapped_paths: set[str] = set()
    for rel in changed:
        for spec_id, path in declared:
            if _declared_matches(path, rel):
                mapped.append({"path": rel, "id": spec_id})
                mapped_paths.add(rel)
    mapped.sort(key=lambda row: (row["path"], row["id"]))

    unmapped = sorted(
        rel for rel in changed if rel not in mapped_paths and _is_app_file(rel)
    )
    return {
        "missing": missing,
        "unmapped_changed": unmapped,
        "mapped_changed": mapped,
        "ok": not missing and not unmapped,
    }


def default_changed_ids(
    kernel: Kernel, files: list[str], repo: Path
) -> tuple[list[str], list[str]]:
    """Spec-YAML ids plus component ids for declared path hits.

    The second list is unmapped changed app files (advisory).
    """
    report = reconcile(kernel, files, repo=repo)
    ids = set(map_changed_files(kernel, files))
    for row in report["mapped_changed"]:
        ids.add(row["id"])
    return sorted(ids), list(report["unmapped_changed"])


def format_reconcile(payload: dict[str, Any]) -> str:
    lines = ["reconcile", "missing:"]
    missing = payload.get("missing") or []
    if not missing:
        lines.append("  (none)")
    for row in missing:
        lines.append(f"  - id: {row.get('id')}")
        lines.append(f"    path: {row.get('path')}")
    lines.append("unmapped_changed:")
    unmapped = payload.get("unmapped_changed") or []
    if not unmapped:
        lines.append("  (none)")
    for item in unmapped:
        lines.append(f"  - {item}")
    lines.append("mapped_changed:")
    mapped = payload.get("mapped_changed") or []
    if not mapped:
        lines.append("  (none)")
    for row in mapped:
        lines.append(f"  - path: {row.get('path')}")
        lines.append(f"    id: {row.get('id')}")
    lines.append(f"ok: {'true' if payload.get('ok') else 'false'}")
    lines.append(f"note: {RECONCILE_NOTE}")
    return "\n".join(lines) + "\n"


def _is_spec_id(text: str) -> bool:
    return text.startswith(("capability.", "component.", "container.", "foundation.", "system.")) and " " not in text


def change_known_ids(change: Change) -> set[str]:
    """Ids this open change names, including ones not on disk yet."""
    ids = {item for item in change.promise_ids if item}
    path = change.path / "delta.yaml"
    if not path.is_file():
        return ids
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        return ids
    added = loaded.get("ADDED") or []
    if not isinstance(added, list):
        return ids
    for item in added:
        if isinstance(item, str) and _is_spec_id(item.strip()):
            ids.add(item.strip())
        elif isinstance(item, dict):
            raw = str(item.get("id") or "").strip()
            if _is_spec_id(raw):
                ids.add(raw)
    return ids


def check_sync(
    kernel: Kernel,
    changed_ids: list[str],
    change_slug: str | None = None,
) -> dict[str, Any]:
    changed_ids = sorted({cid for cid in changed_ids if cid})
    scoped: Change | None = None
    unknown_change = ""
    if change_slug:
        scoped = resolve_open_change(kernel, change_slug)
        if scoped is None:
            unknown_change = change_slug

    phase1_advisory: list[str] = []
    linked: list[str] = []
    known = change_known_ids(scoped) if scoped is not None else set()
    unknown = [
        cid
        for cid in changed_ids
        if cid not in kernel.by_id and cid not in known
    ]
    for cid in changed_ids:
        doc = kernel.by_id.get(cid)
        if not doc:
            continue
        if is_phase1_shaped(doc):
            phase1_advisory.append(cid)
        else:
            linked.append(cid)

    uncovered: list[str] = []
    empty_blasts: list[str] = []
    if not unknown_change:
        uncovered = [cid for cid in linked if not id_covered(kernel, cid, only=scoped)]
        if scoped is not None:
            for cid in changed_ids:
                if cid in kernel.by_id or cid not in known:
                    continue
                if cid not in scoped.promise_ids and cid not in uncovered:
                    uncovered.append(cid)
        for cid in linked:
            result = blast(kernel, cid)
            if result and result["empty"]:
                empty_blasts.append(cid)

    fail_uncovered = bool(uncovered)
    fail_empty = bool(empty_blasts)
    decision = fail_uncovered or fail_empty
    ok = not fail_uncovered and not fail_empty and not unknown and not unknown_change

    contributors = covering_changes(kernel, changed_ids, scoped) if not unknown_change else []
    sensor_rows: list[dict[str, str]] = []
    missing_slugs: list[str] = []
    for change in contributors:
        musts = success_must_lines(change)
        if not musts:
            missing_slugs.append(change.path.name)
        for row in success_sensors(change):
            sensor_rows.append(
                {
                    "change": change.path.name,
                    "must": row["must"],
                    "id": row.get("id") or "",
                    "evidence": row.get("evidence") or "none",
                    "status": "UNVERIFIED",
                }
            )
    if unknown_change or not contributors or missing_slugs:
        sensors = "missing"
    else:
        sensors = "declared"

    return {
        "changed_ids": changed_ids,
        "change": change_slug or "",
        "unknown_change": unknown_change,
        "uncovered": uncovered,
        "unknown": unknown,
        "empty_blast": empty_blasts,
        "phase1_advisory": phase1_advisory,
        "ok": ok,
        "coverage": "pass" if ok else "fail",
        "sensors": sensors,
        "sensor_rows": sensor_rows,
        "missing_sensor_changes": missing_slugs,
        "behavior": "unverified",
        "decision_required": decision,
    }


def change_has_success_sensor(change: Change) -> bool:
    path = change.path / "success.yaml"
    if not path.is_file():
        return False
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        return False
    sensors = loaded.get("sensors") or []
    if not isinstance(sensors, list):
        return False
    return any(isinstance(row, dict) and str(row.get("must") or "").strip() for row in sensors)


def list_gaps(kernel: Kernel) -> dict[str, Any]:
    """Kernel-generic gap queue (Q108). Advisory only (Q109)."""
    phase1_no_join = sorted(
        doc.spec_id
        for doc in kernel.docs
        if doc.level == "capability" and bit_of(doc) == "live" and is_phase1_shaped(doc)
    )
    open_changes = sorted(change.change_id for change in kernel.changes if change.open)
    replaced = sorted(doc.spec_id for doc in kernel.docs if bit_of(doc) == "replaced")
    missing_success_sensor = sorted(
        change.change_id
        for change in kernel.changes
        if change.open and not change_has_success_sensor(change)
    )
    inferred_unpromoted = sorted(
        doc.spec_id for doc in kernel.docs if bit_of(doc) == "inferred"
    )
    return {
        "phase1_no_join": phase1_no_join,
        "open_changes": open_changes,
        "replaced": replaced,
        "missing_success_sensor": missing_success_sensor,
        "inferred_unpromoted": inferred_unpromoted,
        "advisory": True,
    }


def format_list_gaps(payload: dict[str, Any]) -> str:
    lines = ["list_gaps"]
    for key in (
        "phase1_no_join",
        "open_changes",
        "replaced",
        "missing_success_sensor",
        "inferred_unpromoted",
    ):
        lines.append(f"{key}:")
        values = payload.get(key) or []
        if not values:
            lines.append("  (none)")
        for item in values:
            lines.append(f"  - {item}")
    lines.append("advisory: true")
    return "\n".join(lines) + "\n"


def _bump_patch(version: str) -> str:
    parts = version.strip().split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        return version.strip() or "1.0.0"
    return f"{parts[0]}.{parts[1]}.{int(parts[2]) + 1}"


def _document_without_inferred(data: dict[str, Any], today: str) -> dict[str, Any]:
    meta = data.get("meta")
    if not isinstance(meta, dict):
        meta = {}
        data["meta"] = meta
    tags = meta.get("tags") or []
    if isinstance(tags, str):
        tags = [tags]
    if not isinstance(tags, list):
        tags = []
    meta["tags"] = [tag for tag in tags if str(tag).lower() != "inferred"]
    meta["last_updated"] = today
    meta["version"] = _bump_patch(str(meta.get("version") or "1.0.0"))
    changelog = data.get("changelog")
    if not isinstance(changelog, list):
        changelog = []
    data["changelog"] = [
        {
            "date": today,
            "author": "promote",
            "summary": "Promoted from inferred to live",
            "breaking": False,
        },
        *changelog,
    ]
    return data


def promote_ids(
    kernel: Kernel,
    spec_ids: list[str],
    *,
    today: str | None = None,
) -> dict[str, Any]:
    """Drop ``inferred`` on named ids only. Never scans application source."""
    named = []
    seen: set[str] = set()
    for raw in spec_ids:
        spec_id = str(raw).strip()
        if not spec_id or spec_id in seen:
            continue
        seen.add(spec_id)
        named.append(spec_id)
    if not named:
        return {
            "ok": False,
            "promoted": [],
            "problems": ["promote requires named ids"],
        }

    problems: list[str] = []
    docs: list[SpecDoc] = []
    for spec_id in named:
        doc = kernel.by_id.get(spec_id)
        if doc is None:
            problems.append(f"not found: {spec_id}")
            continue
        if bit_of(doc) != "inferred":
            problems.append(f"not inferred: {spec_id}")
            continue
        docs.append(doc)
    if problems:
        return {"ok": False, "promoted": [], "problems": problems}

    stamp = today or date.today().isoformat()
    pending: list[tuple[SpecDoc, str]] = []
    for doc in docs:
        loaded = yaml.safe_load(doc.path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            return {
                "ok": False,
                "promoted": [],
                "problems": [f"not a mapping: {doc.spec_id}"],
            }
        text = yaml.safe_dump(
            _document_without_inferred(loaded, stamp),
            sort_keys=False,
            allow_unicode=True,
        )
        if not text.endswith("\n"):
            text += "\n"
        pending.append((doc, text))
    for doc, text in pending:
        doc.path.write_text(text, encoding="utf-8")
    return {
        "ok": True,
        "promoted": [doc.spec_id for doc, _text in pending],
        "problems": [],
    }


def format_promote(payload: dict[str, Any]) -> str:
    lines = ["promote", "promoted:"]
    promoted = payload.get("promoted") or []
    if not promoted:
        lines.append("  (none)")
    for item in promoted:
        lines.append(f"  - {item}")
    return "\n".join(lines) + "\n"


def _format_slice(lines: list[str], label: str, fields: dict[str, Any]) -> None:
    lines.append(f"{label}:")
    lines.append(f"  id: {fields['id']}")
    if fields.get("path"):
        lines.append(f"  path: {fields['path']}")
    if fields.get("purpose"):
        lines.append(f"  purpose: {fields['purpose']}")
    for key in (
        "responsibilities",
        "implements",
        "realized_by_components",
        "realized_by_containers",
        "uses",
        "depends_on",
        "depended_on_by",
    ):
        values = fields.get(key) or []
        if values:
            lines.append(f"  {key}:")
            for item in values:
                lines.append(f"    - {item}")
    constraints = fields.get("constraints") or {}
    if constraints:
        lines.append("  constraints:")
        for key in CONSTRAINT_LIST_KEYS:
            values = constraints.get(key) or []
            if not values:
                continue
            lines.append(f"    {key}:")
            for item in values:
                lines.append(f"      - {item}")
    diagrams = fields.get("diagrams") or []
    if diagrams:
        lines.append("  diagrams:")
        for diagram in diagrams:
            dtype = str(diagram.get("type") or "").strip() or "diagram"
            title = str(diagram.get("title") or "").strip()
            head = f"{dtype} — {title}" if title else dtype
            lines.append(f"    - {head}")
            mermaid = str(diagram.get("mermaid") or "")
            if mermaid:
                lines.append("      mermaid: |")
                for line in mermaid.splitlines():
                    lines.append(f"        {line}")


def format_retrieve(payload: dict[str, Any]) -> str:
    lines = [f"retrieve {payload['id']}", f"bit: {payload['bit']}"]
    review_state = str(payload.get("review_state") or "")
    if review_state:
        lines.append(f"review_state: {review_state}")
    status = str(payload.get("status") or "")
    if status:
        lines.append(f"status: {status}")
    live = payload.get("live")
    if live and payload["bit"] != "inferred":
        _format_slice(lines, "live", live)
    declared = payload.get("declared")
    if declared and payload["bit"] == "inferred":
        _format_slice(lines, "declared", declared)
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
        names = ", ".join(str(item.get("id") or "") for item in in_flight if item.get("id"))
        lines.append(f"implementation context: {names}")
        lines.append("canonical synchronization: pending")
        lines.append("active change:")
        for item in in_flight:
            kind = item.get("kind") or ""
            lines.append(f"  - {item['id']} ({kind})".rstrip())
            statements = item.get("statements") or []
            if not statements:
                lines.append("    (no delta summary)")
            for statement in statements:
                lines.append(f"    {statement}")
        readiness = str(payload.get("readiness") or "")
        if readiness:
            lines.append("readiness: warning")
            lines.append(f"  {readiness}")
        receipt = f"SpecPlane · retrieve — implementation context is {names}. Canonical synchronization is pending."
        if readiness:
            receipt += " Readiness warning: no implementation relationships are declared."
        lines.append(receipt)
    else:
        lines.append("in-flight: (none)")
    return "\n".join(lines) + "\n"


_SPEC_ID_PREFIXES = ("capability.", "foundation.", "system.", "container.", "component.")


def looks_like_spec_id(text: str) -> bool:
    if "/" in text or "\\" in text:
        return False
    return text.startswith(_SPEC_ID_PREFIXES)


def _context_sensors(spec_id: str, changes: list[Change]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for change in changes:
        for sensor in success_sensors(change):
            promise = str(sensor.get("promise") or "").strip()
            if promise and promise != spec_id:
                continue
            rows.append(
                {
                    "change": change.change_id,
                    "id": str(sensor.get("id") or ""),
                    "must": str(sensor.get("must") or ""),
                    "evidence": str(sensor.get("evidence") or "none"),
                    "status": "UNVERIFIED",
                }
            )
    return rows


def _context_body(kernel: Kernel, spec_id: str, change_slug: str | None) -> dict[str, Any] | None:
    payload = retrieve(kernel, spec_id)
    if payload is None:
        return None
    doc = kernel.by_id[spec_id]
    in_flight = list(payload.get("in_flight") or [])
    missing = ""
    if change_slug:
        known = any(change.change_id == change_slug for change in kernel.changes)
        if not known:
            missing = change_slug
            in_flight = []
        else:
            in_flight = [item for item in in_flight if item.get("id") == change_slug]
    covering = [
        change
        for change in open_changes_for(kernel, spec_id)
        if not change_slug or change.change_id == change_slug
    ]
    live = payload.get("live") or payload.get("declared") or {}
    readiness = ""
    if payload.get("bit") == "live" and in_flight and is_phase1_shaped(doc):
        readiness = str(payload.get("readiness") or "")
    return {
        "id": spec_id,
        "bit": payload["bit"],
        "purpose": str(live.get("purpose") or ""),
        "responsibilities": list(live.get("responsibilities") or []),
        "constraints": live.get("constraints") or {},
        "implements": list(live.get("implements") or []),
        "realized_by_components": list(live.get("realized_by_components") or []),
        "in_flight": in_flight,
        "readiness": readiness,
        "sensors": _context_sensors(spec_id, covering),
        "named_change_missing": missing,
    }


def _implementation_lines(kernel: Kernel, body: dict[str, Any]) -> list[str]:
    if str(body.get("id") or "").startswith("component."):
        wanted = {str(body["id"])}
    else:
        wanted = set(body.get("realized_by_components") or [])
    lines: list[str] = []
    for spec_id, path in component_realization_paths(kernel):
        if spec_id in wanted:
            lines.append(f"{spec_id}: {path}")
    return lines


def build_context(kernel: Kernel, target: str, change_slug: str | None = None) -> dict[str, Any]:
    """Task slice. A path with no realization.paths match stays unmapped."""
    text = target.strip()
    if looks_like_spec_id(text):
        body = _context_body(kernel, text, change_slug)
        if body is None:
            return {"target": text, "unknown": True, "unmapped": False, "bodies": []}
        return {"target": text, "unknown": False, "unmapped": False, "bodies": [body]}
    rel = _norm_rel(text)
    matched = [
        spec_id
        for spec_id, declared in component_realization_paths(kernel)
        if _declared_matches(declared, rel)
    ]
    components = sorted(set(matched))
    if not components:
        return {"target": rel or text, "unknown": False, "unmapped": True, "bodies": []}
    bodies = [
        body
        for spec_id in components
        if (body := _context_body(kernel, spec_id, change_slug)) is not None
    ]
    return {
        "target": rel or text,
        "unknown": False,
        "unmapped": False,
        "components": components,
        "bodies": bodies,
    }


def _format_context_body(lines: list[str], kernel: Kernel, body: dict[str, Any]) -> None:
    lines.append("specification:")
    lines.append(f"  id: {body.get('id') or ''}")
    lines.append(f"  bit: {body.get('bit') or ''}")
    purpose = str(body.get("purpose") or "")
    if purpose:
        lines.append(f"  purpose: {purpose}")
    for item in body.get("responsibilities") or []:
        lines.append(f"  - {item}")
    constraints = body.get("constraints") or {}
    for key in CONSTRAINT_LIST_KEYS:
        for item in constraints.get(key) or []:
            lines.append(f"  constraint.{key}: {item}")
    for item in body.get("implements") or []:
        lines.append(f"  implements: {item}")
    for item in body.get("realized_by_components") or []:
        lines.append(f"  realized_by: {item}")
    lines.append("change:")
    missing = str(body.get("named_change_missing") or "")
    in_flight = body.get("in_flight") or []
    if missing:
        lines.append(f"  unknown_change: {missing}")
    elif not in_flight:
        lines.append("  (none)")
    else:
        names = ", ".join(str(item.get("id") or "") for item in in_flight if item.get("id"))
        lines.append(f"  implementation context: {names}")
        lines.append("  canonical synchronization: pending")
        for item in in_flight:
            kind = item.get("kind") or ""
            lines.append(f"  - {item.get('id') or ''} ({kind})".rstrip())
            statements = item.get("statements") or []
            if not statements:
                lines.append("    (no delta summary)")
            for statement in statements:
                lines.append(f"    {statement}")
    readiness = str(body.get("readiness") or "")
    if readiness:
        lines.append("  readiness: warning")
        lines.append(f"    {readiness}")
    lines.append("implementation:")
    paths = _implementation_lines(kernel, body)
    if paths:
        for path in paths:
            lines.append(f"  - {path}")
    else:
        lines.append("  (none declared)")
    lines.append("evidence:")
    sensors = body.get("sensors") or []
    if not sensors:
        lines.append("  (none)")
    for sensor in sensors:
        label = sensor.get("id") or sensor.get("must") or ""
        lines.append(f"  - {label}")
        if sensor.get("must") and sensor.get("id"):
            lines.append(f"    must: {sensor.get('must')}")
        lines.append(f"    evidence: {sensor.get('evidence') or 'none'}")
        lines.append(f"    status: {sensor.get('status') or 'UNVERIFIED'}")


def format_context(kernel: Kernel, payload: dict[str, Any]) -> str:
    lines = [f"context {payload.get('target') or ''}"]
    if payload.get("unknown"):
        lines.append("unknown: true")
        return "\n".join(lines) + "\n"
    if payload.get("unmapped"):
        lines.append("unmapped: true")
        lines.append("SpecPlane · context — this file is unmapped. No component declares it.")
        return "\n".join(lines) + "\n"
    components = payload.get("components") or []
    if components:
        lines.append("mapped:")
        for spec_id in components:
            lines.append(f"  - {spec_id}")
    for body in payload.get("bodies") or []:
        _format_context_body(lines, kernel, body)
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
    receipt = receipt_blast(payload)
    if receipt:
        lines.append(receipt)
    return "\n".join(lines) + "\n"


def receipt_blast(payload: dict[str, Any]) -> str:
    if payload.get("empty"):
        return (
            "SpecPlane · blast — no declared impact. "
            "This does not mean the code is unaffected."
        )
    if payload.get("decision_required"):
        return (
            "SpecPlane · blast — decision required. "
            "SpecPlane does not pick spec vs code."
        )
    return ""


COVERAGE_NOTE = (
    "SpecPlane checked declared coverage. It did not verify behavior."
)


def _uncovered_recipe(payload: dict[str, Any]) -> list[str]:
    """Next steps when coverage failed on known ids. Not for unknown ids or an unknown change."""
    if payload.get("unknown_change") or payload.get("unknown"):
        return []
    uncovered = [str(item) for item in (payload.get("uncovered") or []) if item]
    if not uncovered:
        return []
    slug = str(payload.get("change") or "").strip()
    ids = ",".join(uncovered)
    lines = ["  uncovered:"]
    for item in uncovered:
        lines.append(f"    - {item}")
    lines.append("  To resolve:")
    if len(uncovered) == 1:
        lines.append(f"    1. retrieve {uncovered[0]}")
    else:
        lines.append("    1. retrieve each uncovered id:")
        for item in uncovered:
            lines.append(f"       - {item}")
    if slug:
        lines.append(
            f"    2. Open or extend specs/changes/{slug}/ "
            "(proposal.yaml, delta.yaml, success.yaml) so those ids are in promise_ids."
        )
        lines.append(f"    3. check_sync --change {slug} --changed-ids {ids}")
    else:
        lines.append(
            "    2. Open a change folder (proposal.yaml, delta.yaml, success.yaml) "
            "so those ids are in promise_ids."
        )
        lines.append(f"    3. check_sync --changed-ids {ids}")
    return lines


def format_check_sync(payload: dict[str, Any]) -> str:
    lines = ["check_sync"]
    if payload.get("change"):
        lines.append(f"change: {payload['change']}")
    lines.append("changed_ids:")
    if payload["changed_ids"]:
        for item in payload["changed_ids"]:
            lines.append(f"  - {item}")
    else:
        lines.append("  (none)")
    lines.append(f"coverage: {payload.get('coverage') or ('pass' if payload.get('ok') else 'fail')}")
    if payload.get("unknown_change"):
        lines.append(f"unknown_change: {payload['unknown_change']}")
    if payload.get("uncovered"):
        slug = payload.get("change") or ""
        if slug:
            lines.append(f"uncovered (not covered by change {slug}):")
        else:
            lines.append("uncovered (no open change covers id):")
        for item in payload["uncovered"]:
            lines.append(f"  - {item}")
    if payload.get("empty_blast"):
        lines.append("empty_blast:")
        for item in payload["empty_blast"]:
            lines.append(f"  - {item}")
    if payload.get("phase1_advisory"):
        lines.append("phase1_advisory:")
        for item in payload["phase1_advisory"]:
            lines.append(f"  - {item}")
        lines.append("  Phase 1 ids have no join edges; uncovered / empty blast do not fail.")
    if payload.get("unknown"):
        lines.append("unknown_ids:")
        for item in payload["unknown"]:
            lines.append(f"  - {item}")
    sensors = payload.get("sensors") or "missing"
    lines.append(f"sensors: {sensors}")
    if sensors == "declared":
        for row in payload.get("sensor_rows") or []:
            must = str(row.get("must") or "")
            if not must:
                continue
            lines.append(f"  - change: {row.get('change')}")
            if row.get("id"):
                lines.append(f"    id: {row.get('id')}")
            lines.append(f"    must: {must}")
            lines.append(f"    evidence: {row.get('evidence') or 'none'}")
            lines.append(f"    status: {row.get('status') or 'UNVERIFIED'}")
    elif payload.get("missing_sensor_changes"):
        for slug in payload["missing_sensor_changes"]:
            lines.append(f"  - change: {slug}")
    lines.append("behavior: unverified")
    if payload.get("decision_required"):
        lines.append("DECISION REQUIRED")
        lines.append("  Named behavior moved and live spec / open change did not cover it.")
        lines.append("  SpecPlane does not stamp live.")
        lines.extend(_uncovered_recipe(payload))
    unmapped = payload.get("unmapped_changed") or []
    if unmapped:
        lines.append("unmapped_changed:")
        for item in unmapped:
            lines.append(f"  - {item}")
        lines.append("  advisory: unmapped app file; not a coverage failure")
    lines.append(f"note: {COVERAGE_NOTE}")
    lines.append(receipt_check_sync(payload))
    return "\n".join(lines) + "\n"


def receipt_check_sync(payload: dict[str, Any]) -> str:
    if not payload.get("ok"):
        parts: list[str] = []
        if payload.get("unknown_change"):
            parts.append("unknown change")
        uncovered = len(payload.get("uncovered") or [])
        empty = len(payload.get("empty_blast") or [])
        unknown = len(payload.get("unknown") or [])
        if uncovered:
            parts.append(f"{uncovered} uncovered")
        if empty:
            parts.append(f"{empty} empty blast")
        if unknown:
            parts.append(f"{unknown} unknown")
        detail = ", ".join(parts) if parts else "coverage failed"
        return f"SpecPlane · sync check — {detail}. Behavior was not verified."
    advisory = payload.get("phase1_advisory") or []
    if advisory:
        return (
            "SpecPlane · sync check — passed as Phase 1 advisory "
            f"({len(advisory)} with no declared impact). Behavior was not verified."
        )
    if payload.get("sensors") == "declared":
        return (
            "SpecPlane · sync check — coverage passed. "
            "Declared sensors were not executed. Behavior was not verified."
        )
    return (
        "SpecPlane · sync check — coverage passed. "
        "No sensors were executed. Behavior was not verified."
    )


# Per sensor, shared across that sensor's binds. Not a product timeout knob.
SENSOR_TIMEOUT_S = 120

RUN_INVOKED_NOTE = (
    "SpecPlane invoked bound checks. It did not certify the implementation satisfies the spec."
)
RUN_IDLE_NOTE = (
    "SpecPlane did not invoke a check. It did not certify the implementation satisfies the spec."
)

_RESULT_RANK = {"pass": 0, "not_run": 0, "fail": 1, "error": 2}


def _read_success_sensors(change: Change) -> tuple[list[dict[str, Any]], str]:
    path = change.path / "success.yaml"
    if not path.is_file():
        return [], ""
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [], f"success.yaml: {exc}"
    if loaded is None:
        return [], ""
    if not isinstance(loaded, dict):
        return [], "success.yaml: document must be a mapping"
    sensors = loaded.get("sensors") or []
    if not isinstance(sensors, list):
        return [], "success.yaml: sensors must be a list"
    rows: list[dict[str, Any]] = []
    for row in sensors:
        if not isinstance(row, dict):
            return [], "success.yaml: each sensor must be a mapping"
        rows.append(row)
    return rows, ""


def _unittest_id(value: Any) -> tuple[str | None, str | None]:
    if value is None:
        return None, None
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None, None
        return text, None
    return None, "must be a string"


def _plan_binds(row: dict[str, Any]) -> tuple[list[list[str]], str, str]:
    """Argvs to invoke. early result is not_run or error when nothing should run.

    English ``must:`` is never turned into a command. ``evaluator:`` is not a harness.
    """
    errors: list[str] = []
    unittest_ids: list[str] = []
    argvs: list[list[str]] = []

    if "test" in row:
        uid, err = _unittest_id(row.get("test"))
        if err:
            errors.append(f"test: {err}")
        elif uid:
            unittest_ids.append(uid)

    if "run" in row:
        run = row.get("run")
        if run is None:
            pass
        elif not isinstance(run, dict):
            errors.append("run: must be a mapping with argv and/or unittest")
        else:
            if "argv" in run:
                argv = run.get("argv")
                if (
                    isinstance(argv, list)
                    and len(argv) > 0
                    and all(isinstance(part, str) for part in argv)
                ):
                    argvs.append(list(argv))
                else:
                    errors.append("run.argv must be a list of strings (no shell)")
            for key in ("unittest", "test"):
                if key not in run:
                    continue
                uid, err = _unittest_id(run.get(key))
                if err:
                    errors.append(f"run.{key} {err}")
                elif uid:
                    unittest_ids.append(uid)

    if errors:
        return [], "error", "; ".join(errors)

    seen: set[str] = set()
    for uid in unittest_ids:
        if uid in seen:
            continue
        seen.add(uid)
        argvs.append([sys.executable, "-m", "unittest", uid])
    if not argvs:
        return [], "not_run", ""
    return argvs, "", ""


def _worst_result(outcomes: list[tuple[str, str]]) -> tuple[str, str]:
    worst = max(_RESULT_RANK[status] for status, _detail in outcomes)
    details = [
        detail
        for status, detail in outcomes
        if _RESULT_RANK[status] == worst and detail
    ]
    name = next(key for key, rank in _RESULT_RANK.items() if rank == worst and key != "not_run")
    return name, "; ".join(details)


def _invoke_argv(argv: list[str], repo: Path, timeout: float) -> tuple[str, str]:
    if timeout <= 0:
        return "error", f"timed out after {timeout:g}s"
    try:
        proc = subprocess.run(
            argv,
            cwd=repo,
            env=os.environ.copy(),
            shell=False,
            timeout=timeout,
            capture_output=True,
            text=True,
        )
    except subprocess.TimeoutExpired:
        return "error", f"timed out after {timeout:g}s"
    except OSError as exc:
        return "error", str(exc)
    if proc.returncode == 0:
        return "pass", ""
    return "fail", f"exit {proc.returncode}"


def _execute_binds(
    argvs: list[list[str]], repo: Path, timeout: float
) -> tuple[str, str]:
    deadline = time.monotonic() + timeout
    outcomes: list[tuple[str, str]] = []
    for argv in argvs:
        remaining = deadline - time.monotonic()
        outcomes.append(_invoke_argv(argv, repo, remaining))
    return _worst_result(outcomes)


def run_sensors(
    kernel: Kernel,
    change_slug: str,
    *,
    repo: Path,
    timeout: float = SENSOR_TIMEOUT_S,
) -> dict[str, Any]:
    """Invoke bound checks on one open change. Does not execute ``must:`` text."""
    slug = (change_slug or "").strip()
    repo = repo.resolve()
    change = resolve_open_change(kernel, slug) if slug else None
    if change is None:
        return {
            "change": slug,
            "unknown_change": slug,
            "sensors": [],
            "invoked": False,
            "ok": False,
            "behavior": "evidence",
        }

    rows, parse_error = _read_success_sensors(change)
    sensor_rows: list[dict[str, str]] = []
    invoked = False
    worst = "pass"
    if parse_error:
        sensor_rows.append({"id": "", "must": "", "result": "error", "detail": parse_error})
        worst = "error"
    else:
        for row in rows:
            argvs, early, detail = _plan_binds(row)
            if early:
                result = early
            else:
                result, detail = _execute_binds(argvs, repo, timeout)
                invoked = True
            if _RESULT_RANK[result] > _RESULT_RANK[worst]:
                worst = result
            sensor_rows.append(
                {
                    "id": str(row.get("id") or "").strip(),
                    "must": str(row.get("must") or "").strip(),
                    "result": result,
                    "detail": detail,
                    "evidence": evidence_label(row),
                    "status": status_for_result(result),
                }
            )

    return {
        "change": slug,
        "unknown_change": "",
        "sensors": sensor_rows,
        "invoked": invoked,
        "ok": _RESULT_RANK[worst] < _RESULT_RANK["fail"],
        "behavior": "evidence",
    }


def format_run(payload: dict[str, Any]) -> str:
    lines = ["run", f"change: {payload.get('change') or ''}"]
    if payload.get("unknown_change"):
        lines.append(f"unknown_change: {payload['unknown_change']}")
    lines.append("sensors:")
    rows = payload.get("sensors") or []
    if not rows:
        lines.append("  (none)")
    for row in rows:
        lines.append(f"  - id: {row.get('id') or ''}")
        must = str(row.get("must") or "")
        if must:
            lines.append(f"    must: {must}")
        lines.append(f"    evidence: {row.get('evidence') or 'none'}")
        lines.append(f"    status: {row.get('status') or status_for_result(str(row.get('result') or ''))}")
        lines.append(f"    result: {row.get('result') or ''}")
        detail = str(row.get("detail") or "")
        if detail and row.get("result") in {"fail", "error"}:
            lines.append(f"    detail: {detail}")
    lines.append("behavior: evidence")
    note = RUN_INVOKED_NOTE if payload.get("invoked") else RUN_IDLE_NOTE
    lines.append(f"note: {note}")
    lines.append(receipt_run(payload))
    return "\n".join(lines) + "\n"


def receipt_run(payload: dict[str, Any]) -> str:
    rows = payload.get("sensors") or []
    results = [str(row.get("result") or "") for row in rows]
    failed = [item for item in results if item in {"fail", "error"}]
    if failed:
        return (
            f"SpecPlane · run — {len(failed)} bound check(s) failed. "
            "This does not certify the spec."
        )
    if not payload.get("invoked") or not results or all(item == "not_run" for item in results):
        unbound = [
            str(row.get("id") or "").strip()
            for row in rows
            if str(row.get("evidence") or "none") == "none" and str(row.get("id") or "").strip()
        ]
        base = "SpecPlane · run — no bound check was executed."
        if unbound:
            return base + " Add run.unittest or run.argv on sensor " + ", ".join(unbound) + "."
        return base
    if any(item == "not_run" for item in results):
        return (
            "SpecPlane · run — some sensors were not executed. "
            "This does not certify the spec."
        )
    return (
        "SpecPlane · run — bound checks passed. "
        "This does not certify the implementation satisfies the spec."
    )


def receipt_validate(error_count: int) -> str:
    if error_count:
        return f"SpecPlane · validate — {error_count} error(s)."
    return ""


def structural_validate(spec_root: Path):
    return validate(spec_root)
