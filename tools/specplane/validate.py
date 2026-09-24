#!/usr/bin/env python3
"""Validate SpecPlane YAML against v9.1.0 structural rules (applicable section 08)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write("PyYAML is required: pip install pyyaml\n")
    sys.exit(2)

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
REF_INTERPOLATION_RE = re.compile(r"\{\{refs\.([a-zA-Z0-9_]+)\.")
CAMEL_RE = re.compile(r"[a-z][A-Z]")

AI_NATIVE_TYPES = {
    "agent",
    "tool",
    "workflow",
    "tool_registry",
    "state_store",
    "evaluator",
}
COMPONENT_TYPES = {
    "component",
    "widget",
    "service",
    *AI_NATIVE_TYPES,
}
CLASSIFICATION_RANK = {
    "public": 0,
    "internal": 1,
    "confidential": 2,
    "regulated": 3,
}


@dataclass
class Finding:
    severity: str  # error | warning
    rule: str
    path: Path | None
    message: str

    def format(self) -> str:
        loc = str(self.path) if self.path else "."
        return f"{self.severity.upper()} [{self.rule}] {loc}: {self.message}"


@dataclass
class SpecDoc:
    path: Path
    data: dict[str, Any]
    meta: dict[str, Any]
    spec_id: str
    level: str
    spec_type: str | None


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    file_count: int = 0

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "error"]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "warning"]


def load_config(start: Path) -> dict[str, Any]:
    for candidate in (start, *start.parents):
        path = candidate / "specplane.config.json"
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            data["_config_dir"] = str(path.parent)
            return data
    return {"specRoot": "specs", "_config_dir": str(start)}


def as_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            if isinstance(item, str) and item:
                out.append(item)
            elif isinstance(item, dict):
                ident = item.get("id") or item.get("name")
                if isinstance(ident, str) and ident:
                    out.append(ident)
        return out
    return []


def dig(data: dict[str, Any], *keys: str) -> Any:
    cur: Any = data
    for key in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def expected_parent(spec_root: Path, level: str) -> Path | None:
    if level == "capability":
        return spec_root / "capabilities"
    if level == "foundation":
        return spec_root / "foundations"
    if level == "container":
        return spec_root / "containers"
    if level == "component":
        return spec_root / "components"
    if level == "system":
        return spec_root
    return None


def load_specs(spec_root: Path) -> tuple[list[SpecDoc], list[Finding]]:
    findings: list[Finding] = []
    docs: list[SpecDoc] = []
    if not spec_root.is_dir():
        findings.append(
            Finding("error", "layout", spec_root, "spec root does not exist")
        )
        return docs, findings

    for path in sorted(spec_root.rglob("*.yaml")):
        if path.name.startswith("."):
            continue
        try:
            rel = path.resolve().relative_to(spec_root.resolve())
        except ValueError:
            rel = path
        if "changes" in rel.parts:
            # Change-folder YAML is convention, not a 5C spec (capability.specplane_change_folders).
            continue
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            findings.append(Finding("error", "yaml", path, f"parse error: {exc}"))
            continue
        if not isinstance(data, dict):
            findings.append(Finding("error", "yaml", path, "document must be a mapping"))
            continue
        meta = data.get("meta") if isinstance(data.get("meta"), dict) else {}
        spec_id = str(meta.get("id") or "")
        level = str(meta.get("level") or "")
        spec_type = meta.get("type")
        spec_type = str(spec_type) if spec_type is not None else None
        docs.append(
            SpecDoc(
                path=path,
                data=data,
                meta=meta,
                spec_id=spec_id,
                level=level,
                spec_type=spec_type,
            )
        )
    return docs, findings


def index_by_id(docs: list[SpecDoc]) -> dict[str, SpecDoc]:
    return {doc.spec_id: doc for doc in docs if doc.spec_id}


def check_meta_and_layout(doc: SpecDoc, spec_root: Path, report: Report) -> None:
    if not doc.spec_id:
        report.findings.append(Finding("error", "1", doc.path, "meta.id is required"))
        return
    if doc.spec_id != doc.path.stem:
        report.findings.append(
            Finding(
                "error",
                "1",
                doc.path,
                f"meta.id '{doc.spec_id}' does not match filename '{doc.path.stem}'",
            )
        )
    if doc.level not in {"capability", "foundation", "system", "container", "component"}:
        report.findings.append(
            Finding("error", "7", doc.path, f"invalid meta.level '{doc.level}'")
        )
        return

    parent = expected_parent(spec_root, doc.level)
    if parent is not None:
        try:
            doc.path.resolve().relative_to(parent.resolve())
        except ValueError:
            report.findings.append(
                Finding(
                    "error",
                    "2",
                    doc.path,
                    f"{doc.level} spec must live under {parent}",
                )
            )

    version = str(doc.meta.get("version") or "")
    if not SEMVER_RE.match(version):
        report.findings.append(
            Finding("error", "9", doc.path, f"meta.version must be semver, got '{version}'")
        )

    changelog = doc.data.get("changelog")
    if not isinstance(changelog, list) or len(changelog) == 0:
        report.findings.append(
            Finding("error", "10", doc.path, "changelog must be a non-empty list")
        )

    introduced = str(doc.meta.get("introduced_in") or "")
    if not SEMVER_RE.match(introduced):
        report.findings.append(
            Finding("error", "12", doc.path, "meta.introduced_in is required semver")
        )

    status = str(doc.meta.get("status") or "")
    if status == "deprecated":
        if not SEMVER_RE.match(str(doc.meta.get("deprecated_in") or "")):
            report.findings.append(
                Finding(
                    "error",
                    "12",
                    doc.path,
                    "deprecated specs require meta.deprecated_in semver",
                )
            )
        replaced = str(doc.meta.get("replaced_by") or "")
        if not replaced:
            report.findings.append(
                Finding("error", "13", doc.path, "deprecated specs require meta.replaced_by")
            )

    if doc.level in {"capability", "foundation"} and doc.spec_type:
        report.findings.append(
            Finding("error", "7", doc.path, f"{doc.level} specs must not set meta.type")
        )
    if doc.level == "system" and doc.spec_type not in (None, "system"):
        report.findings.append(
            Finding("error", "7", doc.path, "system specs must use type: system or omit type")
        )
    if doc.level == "container" and doc.spec_type not in (None, "container"):
        report.findings.append(
            Finding("error", "7", doc.path, "container specs must use type: container")
        )
    if doc.level == "component" and doc.spec_type and doc.spec_type not in COMPONENT_TYPES:
        report.findings.append(
            Finding("error", "7", doc.path, f"invalid component type '{doc.spec_type}'")
        )

    if "ai_config" in doc.data:
        if doc.spec_type not in AI_NATIVE_TYPES:
            report.findings.append(
                Finding(
                    "error",
                    "6",
                    doc.path,
                    "ai_config is only allowed on AI-native component types",
                )
            )

    if "realized_by" in doc.data and doc.level != "capability":
        report.findings.append(
            Finding("error", "8", doc.path, "realized_by is only valid on capability specs")
        )
    if "used_by" in doc.data and doc.level != "foundation":
        report.findings.append(
            Finding("error", "8", doc.path, "used_by is only valid on foundation specs")
        )


def check_references(doc: SpecDoc, by_id: dict[str, SpecDoc], report: Report) -> None:
    def require_id(spec_id: str, rule: str, hint: str) -> None:
        if spec_id not in by_id:
            report.findings.append(
                Finding("error", rule, doc.path, f"{hint} '{spec_id}' does not exist")
            )

    for cap_id in as_str_list(doc.data.get("implements")):
        if not cap_id.startswith("capability."):
            report.findings.append(
                Finding("error", "3", doc.path, f"implements id missing capability. prefix: {cap_id}")
            )
        require_id(cap_id, "3", "implements")

    realized = doc.data.get("realized_by") if isinstance(doc.data.get("realized_by"), dict) else {}
    for container_id in as_str_list(realized.get("containers")):
        require_id(container_id, "4", "realized_by.containers")
    for component_id in as_str_list(realized.get("components")):
        require_id(component_id, "4", "realized_by.components")

    capabilities = dig(doc.data, "system_context", "capabilities")
    for cap_id in as_str_list(capabilities):
        if not cap_id.startswith("capability."):
            report.findings.append(
                Finding(
                    "error",
                    "5",
                    doc.path,
                    f"system_context.capabilities missing capability. prefix: {cap_id}",
                )
            )
        require_id(cap_id, "5", "system_context.capabilities")

    replaced = str(doc.meta.get("replaced_by") or "")
    if replaced:
        require_id(replaced, "14", "replaced_by")

    for foundation_id in as_str_list(doc.data.get("uses")):
        require_id(foundation_id, "uses", "uses")


def check_bidirectional(docs: list[SpecDoc], by_id: dict[str, SpecDoc], report: Report) -> None:
    for doc in docs:
        for cap_id in as_str_list(doc.data.get("implements")):
            cap = by_id.get(cap_id)
            if not cap:
                continue
            realized = cap.data.get("realized_by") if isinstance(cap.data.get("realized_by"), dict) else {}
            bucket = "containers" if doc.level == "container" else "components"
            if doc.spec_id not in as_str_list(realized.get(bucket)):
                report.findings.append(
                    Finding(
                        "error",
                        "18",
                        doc.path,
                        f"implements {cap_id} but that spec does not list this id in realized_by.{bucket}",
                    )
                )

        for foundation_id in as_str_list(doc.data.get("uses")):
            foundation = by_id.get(foundation_id)
            if not foundation:
                continue
            used_by = (
                foundation.data.get("used_by")
                if isinstance(foundation.data.get("used_by"), dict)
                else {}
            )
            bucket = "containers" if doc.level == "container" else "components"
            if doc.spec_id not in as_str_list(used_by.get(bucket)):
                report.findings.append(
                    Finding(
                        "error",
                        "18",
                        doc.path,
                        f"uses {foundation_id} but that spec does not list this id in used_by.{bucket}",
                    )
                )

        deps = dig(doc.data, "implementation", "dependencies", "internal")
        if deps is None:
            deps = dig(doc.data, "dependencies", "internal")
        for dep_id in as_str_list(deps):
            dep = by_id.get(dep_id)
            if not dep:
                report.findings.append(
                    Finding("error", "18", doc.path, f"dependencies.internal '{dep_id}' does not exist")
                )
                continue
            reverse = dig(dep.data, "implementation", "depended_on_by", "components")
            if reverse is None:
                reverse = dig(dep.data, "depended_on_by", "components")
            if doc.spec_id not in as_str_list(reverse):
                report.findings.append(
                    Finding(
                        "error",
                        "18",
                        doc.path,
                        f"depends on {dep_id} but that spec does not list this id in depended_on_by.components",
                    )
                )

        depends_on = dig(doc.data, "relationships", "depends_on")
        for other_id in as_str_list(depends_on):
            other = by_id.get(other_id)
            if not other:
                report.findings.append(
                    Finding(
                        "error",
                        "18",
                        doc.path,
                        f"relationships.depends_on '{other_id}' does not exist",
                    )
                )
                continue
            reverse = dig(other.data, "depended_on_by", "containers")
            if reverse is None:
                reverse = dig(other.data, "implementation", "depended_on_by", "containers")
            if doc.spec_id not in as_str_list(reverse):
                report.findings.append(
                    Finding(
                        "error",
                        "18",
                        doc.path,
                        f"depends on {other_id} but that spec does not list this id in depended_on_by.containers",
                    )
                )


def check_classification(docs: list[SpecDoc], by_id: dict[str, SpecDoc], report: Report) -> None:
    def classification_of(doc: SpecDoc) -> str | None:
        value = dig(doc.data, "constraints", "data_classification")
        if not value:
            value = dig(
                doc.data,
                "implementation",
                "technical_constraints",
                "security",
                "data_classification",
            )
        return str(value) if value else None

    for doc in docs:
        if doc.level != "component":
            continue
        child = classification_of(doc)
        if child is None:
            continue
        child_rank = CLASSIFICATION_RANK.get(child)
        if child_rank is None:
            report.findings.append(
                Finding("error", "15", doc.path, f"unknown data_classification '{child}'")
            )
            continue
        for cap_id in as_str_list(doc.data.get("implements")):
            cap = by_id.get(cap_id)
            if not cap:
                continue
            parent = classification_of(cap)
            if parent is None:
                continue
            parent_rank = CLASSIFICATION_RANK.get(parent)
            if parent_rank is None:
                continue
            if child_rank < parent_rank:
                report.findings.append(
                    Finding(
                        "error",
                        "15",
                        doc.path,
                        f"data_classification '{child}' is weaker than {cap_id} '{parent}'",
                    )
                )


def check_rollout_and_tests(doc: SpecDoc, report: Report) -> None:
    rollout = dig(doc.data, "implementation", "rollout")
    if rollout is None:
        rollout = doc.data.get("rollout")
    if isinstance(rollout, dict):
        strategy = str(rollout.get("strategy") or "")
        flag = str(rollout.get("feature_flag") or "")
        if strategy in {"feature_flag", "dark_launch"} and not flag:
            report.findings.append(
                Finding(
                    "error",
                    "17",
                    doc.path,
                    f"rollout.strategy '{strategy}' requires rollout.feature_flag",
                )
            )

    classification = dig(doc.data, "constraints", "data_classification") or dig(
        doc.data,
        "implementation",
        "technical_constraints",
        "security",
        "data_classification",
    )
    test_strategy = dig(doc.data, "implementation", "validation", "test_strategy")
    if classification in {"confidential", "regulated"} and isinstance(test_strategy, dict):
        security = test_strategy.get("security")
        if security in (None, "", False):
            report.findings.append(
                Finding(
                    "warning",
                    "16",
                    doc.path,
                    "confidential/regulated data_classification implies a security test gate",
                )
            )


def check_analytics(docs: list[SpecDoc], by_id: dict[str, SpecDoc], report: Report) -> None:
    emitters: dict[str, list[str]] = {}
    for doc in docs:
        if doc.level != "capability":
            continue
        events = doc.data.get("analytics_events")
        uses = as_str_list(doc.data.get("uses"))
        if not events and "foundation.analytics_conventions" not in uses:
            continue
        realized = doc.data.get("realized_by") if isinstance(doc.data.get("realized_by"), dict) else {}
        realized_components = set(as_str_list(realized.get("components")))
        event_names: list[str] = []
        if isinstance(events, list):
            for event in events:
                if not isinstance(event, dict):
                    continue
                name = str(event.get("name") or "")
                emitted_by = str(event.get("emitted_by") or "")
                if name:
                    event_names.append(name)
                    emitters.setdefault(name, []).append(emitted_by or doc.spec_id)
                if emitted_by and emitted_by not in realized_components:
                    report.findings.append(
                        Finding(
                            "error",
                            "19",
                            doc.path,
                            f"analytics_events {name} emitted_by '{emitted_by}' is not in realized_by.components",
                        )
                    )
                owner = by_id.get(emitted_by)
                if owner:
                    planning_events = dig(owner.data, "planning", "analytics", "events")
                    names = []
                    if isinstance(planning_events, list):
                        for item in planning_events:
                            if isinstance(item, dict) and item.get("name"):
                                names.append(str(item["name"]))
                    if name and name not in names:
                        report.findings.append(
                            Finding(
                                "error",
                                "19",
                                owner.path,
                                f"must list analytics event '{name}' in planning.analytics.events",
                            )
                        )
        derived = dig(doc.data, "success_metrics", "derived_from")
        if isinstance(derived, dict):
            for metric, sources in derived.items():
                for source in as_str_list(sources):
                    if source not in event_names:
                        report.findings.append(
                            Finding(
                                "error",
                                "19",
                                doc.path,
                                f"success_metrics.derived_from {metric} references unknown event '{source}'",
                            )
                        )

    for name, owners in emitters.items():
        unique = [owner for owner in owners if owner]
        if len(set(unique)) > 1:
            report.findings.append(
                Finding(
                    "error",
                    "19",
                    None,
                    f"analytics event '{name}' is emitted by more than one component: {unique}",
                )
            )


def check_capability_flows(doc: SpecDoc, report: Report) -> None:
    """Rule 22: a flow mapping needs a non-empty id. Strings stay valid. goal is optional."""
    if doc.level != "capability":
        return
    flows = doc.data.get("flows")
    if not isinstance(flows, list):
        return
    for index, item in enumerate(flows):
        if isinstance(item, str):
            if not item.strip():
                report.findings.append(
                    Finding("error", "22", doc.path, f"flows[{index}] string must be non-empty")
                )
            continue
        if isinstance(item, dict):
            ident = item.get("id")
            if not isinstance(ident, str) or not ident.strip():
                report.findings.append(
                    Finding(
                        "error",
                        "22",
                        doc.path,
                        f"flows[{index}] mapping requires a non-empty id",
                    )
                )
            continue
        report.findings.append(
            Finding(
                "error",
                "22",
                doc.path,
                f"flows[{index}] must be a string or a mapping",
            )
        )


def check_refs_and_names(doc: SpecDoc, report: Report) -> None:
    refs = doc.data.get("refs")
    refs_by_id: dict[str, dict[str, Any]] = {}
    if isinstance(refs, list):
        for ref in refs:
            if isinstance(ref, dict) and ref.get("id"):
                refs_by_id[str(ref["id"])] = ref

    blobs: list[str] = []
    diagrams = doc.data.get("diagrams")
    if isinstance(diagrams, list):
        for diagram in diagrams:
            if isinstance(diagram, dict):
                mermaid = diagram.get("mermaid") or ""
                blobs.append(str(mermaid))
                blobs.append(str(diagram.get("description") or ""))

    used_ids = set()
    for blob in blobs:
        used_ids.update(REF_INTERPOLATION_RE.findall(blob))

    for ref_id in used_ids:
        ref = refs_by_id.get(ref_id)
        if not ref:
            report.findings.append(
                Finding("error", "20", doc.path, f"diagram interpolates unknown ref '{ref_id}'")
            )
            continue
        if not (ref.get("url") or ref.get("path")):
            report.findings.append(
                Finding(
                    "error",
                    "20",
                    doc.path,
                    f"ref '{ref_id}' used in a diagram must have url or path",
                )
            )

    names: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key in {"name", "id"} and isinstance(value, str):
                    names.append(value)
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(dig(doc.data, "planning", "analytics") or {})
    walk(dig(doc.data, "implementation", "observability") or {})
    walk(dig(doc.data, "implementation", "contracts") or {})
    walk(doc.data.get("analytics_events") or [])

    normalized: dict[str, str] = {}
    for name in names:
        key = re.sub(r"[^a-z0-9]", "", name.lower())
        if not key:
            continue
        previous = normalized.get(key)
        if previous and previous != name and (
            CAMEL_RE.search(name) or CAMEL_RE.search(previous) or "_" in name or "_" in previous
        ):
            report.findings.append(
                Finding(
                    "warning",
                    "21",
                    doc.path,
                    f"conflicting identifiers '{previous}' and '{name}'",
                )
            )
        normalized.setdefault(key, name)


def validate(spec_root: Path) -> Report:
    report = Report()
    docs, load_findings = load_specs(spec_root)
    report.findings.extend(load_findings)
    report.file_count = len(docs)
    by_id = index_by_id(docs)

    for doc in docs:
        check_meta_and_layout(doc, spec_root, report)
        check_capability_flows(doc, report)
        check_references(doc, by_id, report)
        check_rollout_and_tests(doc, report)
        check_refs_and_names(doc, report)

    check_bidirectional(docs, by_id, report)
    check_classification(docs, by_id, report)
    check_analytics(docs, by_id, report)
    return report


def resolve_spec_root(spec_root: Path | None, config_dir: Path) -> Path:
    if spec_root is not None:
        return spec_root.resolve()
    cfg = load_config(config_dir.resolve())
    return (Path(cfg["_config_dir"]) / cfg.get("specRoot", "specs")).resolve()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate SpecPlane specs")
    parser.add_argument(
        "--spec-root",
        type=Path,
        help="Path to specs/ (default: specplane.config.json specRoot, else ./specs)",
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=Path.cwd(),
        help="Directory to search for specplane.config.json",
    )
    parser.add_argument(
        "--strict-warnings",
        action="store_true",
        help="Treat warnings as errors",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    spec_root = resolve_spec_root(args.spec_root, args.config_dir)

    report = validate(spec_root)
    for finding in report.findings:
        print(finding.format())

    error_count = len(report.errors)
    warn_count = len(report.warnings)
    print(
        f"Checked {report.file_count} spec(s): {error_count} error(s), {warn_count} warning(s)."
    )
    if error_count:
        return 1
    if args.strict_warnings and warn_count:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
