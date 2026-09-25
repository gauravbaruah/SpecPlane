"""One affected subgraph, five projections.

Blast buckets stay on ``kernel.blast``. This module explains the same join-key
closure and projects it. Agents may propose missing spec edges; they are not
this engine. See docs/impact-perspectives.md.
"""

from __future__ import annotations

from collections import deque
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

import yaml

from kernel import Change, Kernel, bit_of
from validate import as_str_list, dig


QUESTIONS = {
    "system": "What parts of the modeled system may this change affect?",
    "product": "What product promises, behavior, and success definitions may need reconsideration?",
    "quality": "Given this affected subgraph, what behavior or evidence should be reconsidered or revalidated?",
    "governance": "Which governed concerns intersect the affected subgraph?",
    "ownership": "Who or what organizational function is associated with the affected things?",
}

_SYSTEM_NOTE = (
    "Ids and paths live on impact.affected. This projection does not recompute blast."
)
_INFERRED_NOTE = "Possible impact through inferred dependency."
_DERIVED_NOTE = (
    "Derived from an inverse relationship. Not a declared edge on the affected id."
)
_MISSING_SPEC = "Target spec is not in the graph."
_STRATEGY_NOTE = (
    "Declared test strategy. Presence is not evidence the behavior was revalidated."
)
_SENSOR_NOTE = "Declared sensor. Presence is not evidence the signal is healthy."
_ROLLOUT_NOTE = "Declared rollout intent. Presence is not evidence the change was verified."
_FOUNDATION_GAP = (
    "Foundation is in the affected subgraph. v9.1 has no governed-concern "
    "classification on foundations, so this impact does not identify a governance "
    "relationship from the foundation record."
)
_GOVERNANCE_GAP = "Governance relationship not identified in current model."
_OWNERSHIP_GAP = "No ownership information represented."
_ROADMAP_NOTE = "Declared roadmap edge. Join-key blast does not expand this edge."

# Higher rank may upgrade a weaker arrival (a change can both mention a node and need its start expansion).
_RANK = {
    "terminal": 0,
    "foundation_user": 1,
    "component": 2,
    "capability": 2,
    "container": 2,
    "foundation": 2,
    "system": 2,
    "change": 2,
}

_LEVEL_ORDER = ("change", "system", "container", "capability", "component", "foundation")
_SECURITY_KEYS = (
    "authentication",
    "authorization",
    "data_protection",
    "data_classification",
    "threats",
    "mitigations",
    "data_retention",
)


def impact(kernel: Kernel, root: str) -> dict[str, Any] | None:
    graph = affected_subgraph(kernel, root)
    if graph is None:
        return None
    affected = graph["affected"]
    perspectives = {
        "system": project_system(affected),
        "product": project_product(kernel, affected),
        "quality": project_quality(kernel, affected),
        "governance": project_governance(kernel, affected),
        "ownership": project_ownership(kernel, graph),
    }
    return {
        "root": graph["root"],
        "root_kind": graph["root_kind"],
        "affected": affected,
        "open_changes": graph["open_changes"],
        "unresolved": graph["unresolved"],
        "perspectives": perspectives,
    }


def format_impact(payload: dict[str, Any]) -> str:
    return yaml.safe_dump(
        {"impact": payload},
        sort_keys=False,
        allow_unicode=True,
    )


def affected_subgraph(kernel: Kernel, root: str) -> dict[str, Any] | None:
    """Join-key closure with paths. Membership matches blast() for a spec id."""
    doc = kernel.by_id.get(root)
    change = None if doc else _find_change(kernel, root)
    if doc is None and change is None:
        return None

    nodes: dict[str, dict[str, Any]] = {}
    expand_mode: dict[str, str] = {}
    expanded: dict[str, int] = {}
    queued: set[str] = set()
    queue: deque[str] = deque()
    unresolved: list[dict[str, str]] = []

    def consider(target: str, relationship: str, via: str, mode: str) -> None:
        if target not in nodes:
            target_doc = kernel.by_id.get(target)
            epistemic = "declared"
            note = ""
            if target_doc is not None and bit_of(target_doc) == "inferred":
                epistemic = "inferred"
                note = _INFERRED_NOTE
            elif target_doc is None:
                epistemic = "not_represented"
                note = _MISSING_SPEC
                unresolved.append({"id": target, "statement": _MISSING_SPEC})
            parent = nodes[via]["distance"]
            nodes[target] = _node(
                target,
                _level_of(kernel, target),
                parent + 1,
                epistemic,
                relationship,
                via,
                note,
            )
        rank = _RANK[mode]
        if rank > expanded.get(target, -1):
            expanded[target] = rank
            expand_mode[target] = mode
            if target not in queued:
                queued.add(target)
                queue.append(target)

    def seed(target: str, mode: str) -> None:
        target_doc = kernel.by_id.get(target)
        epistemic = "declared"
        note = ""
        if target_doc is not None and bit_of(target_doc) == "inferred":
            epistemic = "inferred"
            note = "This spec is inferred."
        nodes[target] = _node(target, _level_of(kernel, target), 0, epistemic, "selected", "", note)
        expanded[target] = _RANK[mode]
        expand_mode[target] = mode
        queued.add(target)
        queue.append(target)

    if doc is not None:
        root_id = doc.spec_id
        root_kind = doc.level
        seed(root_id, _start_mode(doc.level))
    else:
        assert change is not None
        root_id = f"change.{change.path.name}"
        root_kind = "change"
        seed(root_id, "change")
        # Level on the change root is change, not a guessed spec level.
        nodes[root_id]["level"] = "change"
        for promise_id in change.promise_ids:
            if promise_id not in kernel.by_id:
                consider(promise_id, "promises", root_id, "terminal")
                continue
            promised = kernel.by_id[promise_id]
            consider(promise_id, "promises", root_id, _start_mode(promised.level))

    while queue:
        current = queue.popleft()
        queued.discard(current)
        rank_at_start = expanded[current]
        _expand(kernel, current, expand_mode[current], consider)
        if expanded[current] > rank_at_start and current not in queued:
            queued.add(current)
            queue.append(current)

    _derive_containment(kernel, nodes)
    affected = [_public_node(nodes, spec_id) for spec_id in _sorted_ids(nodes)]
    caps, comps, founds = _blast_ids(affected)
    named = set(caps) | set(comps) | set(founds)
    if root_kind != "change":
        named.add(root_id)
    open_changes = sorted(
        {
            item.change_id
            for item in kernel.changes
            if item.open and named & set(item.promise_ids)
        }
    )
    return {
        "root": root_id,
        "root_kind": root_kind,
        "change": change,
        "affected": affected,
        "open_changes": open_changes,
        "unresolved": unresolved,
    }


def project_system(affected: list[dict[str, Any]]) -> dict[str, Any]:
    by_level: dict[str, list[str]] = {}
    for node in affected:
        by_level.setdefault(str(node["level"]), []).append(str(node["id"]))
    ordered = {level: by_level[level] for level in _LEVEL_ORDER if level in by_level}
    for level, ids in by_level.items():
        if level not in ordered:
            ordered[level] = ids
    return {"question": QUESTIONS["system"], "by_level": ordered, "note": _SYSTEM_NOTE}


def project_product(kernel: Kernel, affected: list[dict[str, Any]]) -> dict[str, Any]:
    affected_ids = {str(node["id"]) for node in affected}
    flow_ids = _flow_ids(kernel, affected)
    items: list[dict[str, Any]] = []
    gaps: list[dict[str, str]] = []
    for node in affected:
        if node["level"] != "capability":
            continue
        doc = kernel.by_id.get(str(node["id"]))
        if doc is None:
            continue
        subject = doc.spec_id
        responsibilities = as_str_list(doc.data.get("responsibilities"))
        for text in responsibilities:
            items.append(_item(subject, "responsibility", "responsibilities", text))
        flows = doc.data.get("flows")
        if isinstance(flows, list) and flows:
            for flow in flows:
                items.append(_flow_item(subject, flow))
        else:
            gaps.append(
                {"subject": subject, "statement": f"Flows are not represented on {subject}."}
            )
        business = doc.data.get("business_value")
        if isinstance(business, dict):
            for key in ("user_outcome", "objective", "revenue_dependency", "strategic_priority"):
                value = business.get(key)
                if _filled(value):
                    items.append(
                        _item(subject, "business_value", f"business_value.{key}", f"{key}: {value}")
                    )
        constraints = doc.data.get("constraints")
        if isinstance(constraints, dict):
            for key, statements in _constraint_entries(constraints):
                items.append(
                    _item(subject, "constraint", f"constraints.{key}", "; ".join(statements))
                )
        metrics = doc.data.get("success_metrics")
        if isinstance(metrics, dict) and _filled(metrics.get("primary")):
            items.append(
                _item(
                    subject,
                    "success_metric",
                    "success_metrics.primary",
                    str(metrics.get("primary")),
                )
            )
            targets = metrics.get("targets")
            if isinstance(targets, dict):
                for name, target in targets.items():
                    items.append(
                        _item(
                            subject,
                            "success_target",
                            "success_metrics.targets",
                            f"{name}: {target}",
                        )
                    )
            derived = metrics.get("derived_from")
            if isinstance(derived, dict):
                for name, sources in derived.items():
                    items.append(
                        _item(
                            subject,
                            "success_metric_source",
                            "success_metrics.derived_from",
                            f"{name}: {sources}",
                        )
                    )
        else:
            gaps.append(
                {
                    "subject": subject,
                    "statement": f"Success metrics are not represented on {subject}.",
                }
            )
        events = doc.data.get("analytics_events")
        if isinstance(events, list):
            for event in events:
                if isinstance(event, dict) and event.get("name"):
                    items.append(
                        _item(
                            subject,
                            "analytics_event",
                            "analytics_events",
                            str(event.get("name")),
                        )
                    )
        for question in _questions(doc.data.get("open_questions")):
            items.append(_item(subject, "open_question", "open_questions", question))
        roadmap = doc.data.get("roadmap")
        if isinstance(roadmap, dict) and any(
            _filled(roadmap.get(key)) for key in ("phase", "priority", "depends_on", "enables")
        ):
            if _filled(roadmap.get("phase")) or _filled(roadmap.get("priority")):
                items.append(
                    _item(
                        subject,
                        "roadmap",
                        "roadmap",
                        f"phase={roadmap.get('phase') or ''} priority={roadmap.get('priority') or ''}",
                    )
                )
            for related, kind in (
                ("depends_on", "roadmap_dependency"),
                ("enables", "roadmap_enables"),
            ):
                for related_id in as_str_list(roadmap.get(related)):
                    items.append(
                        {
                            "subject": subject,
                            "kind": kind,
                            "related_id": related_id,
                            "in_affected_subgraph": related_id in affected_ids,
                            "epistemic_state": "declared",
                            "source": f"roadmap.{related}",
                            "detail": related_id,
                            "note": _ROADMAP_NOTE,
                        }
                    )
        else:
            gaps.append(
                {"subject": subject, "statement": f"Roadmap is not represented on {subject}."}
            )
    for node in affected:
        if node["level"] != "component":
            continue
        doc = kernel.by_id.get(str(node["id"]))
        if doc is None:
            continue
        flow_ref = str(dig(doc.data, "planning", "user_flows", "flow_ref") or "")
        if not flow_ref:
            continue
        resolved = flow_ref in flow_ids
        items.append(
            {
                "subject": doc.spec_id,
                "kind": "flow_ref",
                "epistemic_state": "declared",
                "source": "planning.user_flows.flow_ref",
                "detail": flow_ref,
                "resolved": resolved,
            }
        )
        if not resolved:
            gaps.append(
                {
                    "subject": doc.spec_id,
                    "statement": (
                        f"flow_ref '{flow_ref}' is not a flow id on an affected capability."
                    ),
                }
            )
    return {"question": QUESTIONS["product"], "items": items, "gaps": gaps}


def project_quality(kernel: Kernel, affected: list[dict[str, Any]]) -> dict[str, Any]:
    criteria: list[dict[str, Any]] = []
    verification: list[dict[str, Any]] = []
    missing: list[dict[str, str]] = []
    journeys: list[dict[str, Any]] = []
    sensors: list[dict[str, Any]] = []
    contracts: list[dict[str, Any]] = []
    rollout: list[dict[str, Any]] = []
    gaps: list[dict[str, str]] = []

    for node in affected:
        level = node["level"]
        if level not in {"capability", "component"}:
            continue
        doc = kernel.by_id.get(str(node["id"]))
        if doc is None:
            continue
        subject = doc.spec_id
        saw_quality = False
        if level == "capability":
            metrics = doc.data.get("success_metrics")
            if isinstance(metrics, dict) and _filled(metrics.get("primary")):
                saw_quality = True
                criteria.append(
                    {
                        "subject": subject,
                        "kind": "success_metric",
                        "epistemic_state": "declared",
                        "source": "success_metrics.primary",
                        "detail": str(metrics.get("primary")),
                        "note": "Declared success definition. This is not a verification result.",
                    }
                )
            flows = doc.data.get("flows")
            if isinstance(flows, list):
                for flow in flows:
                    if not isinstance(flow, dict):
                        continue
                    flow_id = str(flow.get("id") or "")
                    kinds = [str(k) for k in flow.get("kinds") or []]
                    if "journey" in kinds or flow.get("exceptions") or flow.get("recovery"):
                        saw_quality = True
                        journeys.append(
                            {
                                "subject": subject,
                                "kind": "journey",
                                "flow_id": flow_id,
                                "epistemic_state": "declared",
                                "source": "flows",
                                "exceptions": _texts(flow.get("exceptions")),
                                "recovery": _texts(flow.get("recovery")),
                            }
                        )
            for event in _event_names(doc.data.get("analytics_events")):
                saw_quality = True
                sensors.append(_sensor(subject, "analytics_event", "analytics_events", event))
        else:
            validation = dig(doc.data, "implementation", "validation")
            if not isinstance(validation, dict):
                validation = {}
            acceptance = _texts(validation.get("acceptance_criteria"))
            edge_cases = _texts(validation.get("edge_cases"))
            for text in acceptance:
                saw_quality = True
                criteria.append(
                    {
                        "subject": subject,
                        "kind": "acceptance_criterion",
                        "epistemic_state": "declared",
                        "source": "validation.acceptance_criteria",
                        "detail": text,
                    }
                )
            for text in edge_cases:
                saw_quality = True
                criteria.append(
                    {
                        "subject": subject,
                        "kind": "edge_case",
                        "epistemic_state": "declared",
                        "source": "validation.edge_cases",
                        "detail": text,
                    }
                )
            strategies = _strategy_entries(validation.get("test_strategy"))
            for name, detail in strategies:
                saw_quality = True
                verification.append(
                    {
                        "subject": subject,
                        "kind": "test_strategy",
                        "name": name,
                        "epistemic_state": "declared",
                        "source": "validation.test_strategy",
                        "detail": detail,
                        "note": _STRATEGY_NOTE,
                    }
                )
            if (acceptance or edge_cases) and not _strategy_is_evidence(strategies):
                missing.append(
                    {
                        "subject": subject,
                        "statement": (
                            f"Verification not represented for acceptance criteria on {subject}."
                        ),
                    }
                )
            readiness = validation.get("readiness")
            if _filled(readiness):
                saw_quality = True
                verification.append(
                    {
                        "subject": subject,
                        "kind": "readiness",
                        "epistemic_state": "declared",
                        "source": "validation.readiness",
                        "detail": str(readiness),
                        "note": "Declared readiness. This is not a verification result.",
                    }
                )
            for question in _questions(validation.get("open_questions")):
                saw_quality = True
                gaps.append(
                    {
                        "subject": subject,
                        "statement": f"Unresolved validation question on {subject}: {question}",
                    }
                )
            obs = dig(doc.data, "implementation", "observability")
            if isinstance(obs, dict):
                for kind in ("metrics", "logs", "traces", "slis", "slos"):
                    for name in _texts(obs.get(kind)):
                        saw_quality = True
                        sensors.append(
                            _sensor(subject, kind, f"observability.{kind}", name)
                        )
                alerting = obs.get("alerting")
                if isinstance(alerting, dict):
                    for severity in ("critical", "warning"):
                        for name in _texts(alerting.get(severity)):
                            saw_quality = True
                            sensors.append(
                                _sensor(
                                    subject,
                                    "alert",
                                    f"observability.alerting.{severity}",
                                    name,
                                )
                            )
            for event in _event_names(dig(doc.data, "planning", "analytics", "events")):
                saw_quality = True
                sensors.append(
                    _sensor(subject, "analytics_event", "planning.analytics.events", event)
                )
            contract_block = dig(doc.data, "implementation", "contracts")
            if isinstance(contract_block, dict):
                for kind in ("apis", "events", "states"):
                    for detail in _texts(contract_block.get(kind)):
                        saw_quality = True
                        contracts.append(
                            {
                                "subject": subject,
                                "kind": kind,
                                "epistemic_state": "declared",
                                "source": f"contracts.{kind}",
                                "detail": detail,
                            }
                        )
            roll = dig(doc.data, "implementation", "rollout")
            if isinstance(roll, dict) and (
                _filled(roll.get("strategy")) or _filled(roll.get("rollback_trigger"))
            ):
                saw_quality = True
                rollout.append(
                    {
                        "subject": subject,
                        "epistemic_state": "declared",
                        "source": "rollout",
                        "strategy": str(roll.get("strategy") or ""),
                        "rollback_trigger": str(roll.get("rollback_trigger") or ""),
                        "note": _ROLLOUT_NOTE,
                    }
                )
        if not saw_quality:
            gaps.append(
                {
                    "subject": subject,
                    "statement": f"Quality evidence not represented on {subject}.",
                }
            )
    return {
        "question": QUESTIONS["quality"],
        "criteria": criteria,
        "verification": verification,
        "missing_verification": missing,
        "journeys": journeys,
        "sensors": sensors,
        "contracts": contracts,
        "rollout": rollout,
        "gaps": gaps,
    }


def project_governance(kernel: Kernel, affected: list[dict[str, Any]]) -> dict[str, Any]:
    concerns: list[dict[str, Any]] = []
    unclassified: list[dict[str, str]] = []
    for node in affected:
        doc = kernel.by_id.get(str(node["id"]))
        if node["level"] == "foundation":
            unclassified.append({"id": str(node["id"]), "statement": _FOUNDATION_GAP})
            continue
        if doc is None or node["level"] not in {"capability", "component"}:
            continue
        if node["level"] == "capability":
            constraints = doc.data.get("constraints")
            if isinstance(constraints, dict):
                for key, statements in _constraint_entries(constraints):
                    concerns.append(
                        {
                            "subject": doc.spec_id,
                            "concern": key,
                            "epistemic_state": "declared",
                            "source": f"constraints.{key}",
                            "statements": statements,
                        }
                    )
            continue
        security = dig(doc.data, "implementation", "technical_constraints", "security")
        if not isinstance(security, dict):
            continue
        compliance = security.get("compliance")
        if _filled(compliance):
            concerns.append(
                {
                    "subject": doc.spec_id,
                    "concern": "compliance",
                    "epistemic_state": "declared",
                    "source": "technical_constraints.security.compliance",
                    "statements": [str(compliance)],
                }
            )
        statements: list[str] = []
        for key in _SECURITY_KEYS:
            value = security.get(key)
            if isinstance(value, list):
                texts = _texts(value)
                if texts:
                    statements.append(f"{key}: {', '.join(texts)}")
            elif _filled(value):
                statements.append(f"{key}: {value}")
        if statements:
            concerns.append(
                {
                    "subject": doc.spec_id,
                    "concern": "security",
                    "epistemic_state": "declared",
                    "source": "technical_constraints.security",
                    "statements": statements,
                }
            )
    gaps: list[dict[str, str]] = []
    if not concerns:
        gaps.append({"subject": "", "statement": _GOVERNANCE_GAP})
    return {
        "question": QUESTIONS["governance"],
        "concerns": concerns,
        "unclassified_foundations": unclassified,
        "gaps": gaps,
    }


def project_ownership(kernel: Kernel, graph: dict[str, Any]) -> dict[str, Any]:
    rules = _codeowners_rules(kernel.spec_root)
    associations: list[dict[str, Any]] = []
    gaps: list[dict[str, str]] = []
    change: Change | None = graph.get("change")
    for node in graph["affected"]:
        spec_id = str(node["id"])
        if node["level"] == "change":
            owner = ""
            if change is not None:
                owner = str(change.data.get("owner") or "")
            if owner.strip():
                associations.append(
                    _owner(spec_id, owner.strip(), "declared", "change.owner")
                )
            else:
                gaps.append({"subject": spec_id, "statement": _OWNERSHIP_GAP})
            continue
        doc = kernel.by_id.get(spec_id)
        declared = str(doc.meta.get("owner") or "").strip() if doc else ""
        if declared:
            associations.append(_owner(spec_id, declared, "declared", "meta.owner"))
        paths = as_str_list(dig(doc.data, "implementation", "realization", "paths")) if doc else []
        derived = _owners_for_paths(paths, rules)
        for owner in derived:
            associations.append(
                {
                    "subject": spec_id,
                    "owner": owner,
                    "epistemic_state": "derived",
                    "source": "CODEOWNERS",
                    "paths": paths,
                }
            )
        if not declared and not derived:
            gaps.append({"subject": spec_id, "statement": _OWNERSHIP_GAP})
    return {
        "question": QUESTIONS["ownership"],
        "associations": associations,
        "gaps": gaps,
    }


def _expand(kernel: Kernel, current: str, mode: str, consider: Any) -> None:
    doc = kernel.by_id.get(current)
    if mode == "change" or mode == "terminal" or doc is None:
        return
    if mode == "component":
        for cap_id in as_str_list(doc.data.get("implements")):
            consider(cap_id, "implements", current, "terminal")
        for foundation_id in as_str_list(doc.data.get("uses")):
            consider(foundation_id, "uses", current, "terminal")
        for dep_id in as_str_list(dig(doc.data, "implementation", "dependencies", "internal")):
            _consider_neighbor(dep_id, "dependencies.internal", current, consider)
        for dep_id in as_str_list(dig(doc.data, "implementation", "depended_on_by", "components")):
            _consider_neighbor(dep_id, "depended_on_by.components", current, consider)
        for dep_id in as_str_list(dig(doc.data, "relationships", "contains")):
            _consider_neighbor(dep_id, "relationships.contains", current, consider)
        return
    if mode == "capability":
        realized = doc.data.get("realized_by") if isinstance(doc.data.get("realized_by"), dict) else {}
        for comp_id in as_str_list(realized.get("components")):
            consider(comp_id, "realized_by.components", current, "component")
        for container_id in as_str_list(realized.get("containers")):
            consider(container_id, "realized_by.containers", current, "terminal")
        for foundation_id in as_str_list(doc.data.get("uses")):
            consider(foundation_id, "uses", current, "terminal")
        return
    if mode == "foundation":
        used = doc.data.get("used_by") if isinstance(doc.data.get("used_by"), dict) else {}
        for comp_id in as_str_list(used.get("components")):
            consider(comp_id, "used_by.components", current, "foundation_user")
        for container_id in as_str_list(used.get("containers")):
            consider(container_id, "used_by.containers", current, "terminal")
            other = kernel.by_id.get(container_id)
            if other:
                for cap_id in as_str_list(other.data.get("implements")):
                    consider(cap_id, "implements", container_id, "terminal")
        return
    if mode == "foundation_user":
        for cap_id in as_str_list(doc.data.get("implements")):
            consider(cap_id, "implements", current, "terminal")
        return
    if mode == "container":
        for cap_id in as_str_list(doc.data.get("implements")):
            consider(cap_id, "implements", current, "terminal")
        for foundation_id in as_str_list(doc.data.get("uses")):
            consider(foundation_id, "uses", current, "terminal")
        for comp_id in as_str_list(dig(doc.data, "relationships", "contains")):
            if comp_id.startswith("component."):
                consider(comp_id, "relationships.contains", current, "component")
        return
    if mode == "system":
        for cap_id in as_str_list(dig(doc.data, "system_context", "capabilities")):
            consider(cap_id, "system_context.capabilities", current, "terminal")


def _consider_neighbor(target: str, relationship: str, via: str, consider: Any) -> None:
    if target.startswith("foundation."):
        consider(target, relationship, via, "terminal")
    elif target.startswith("capability."):
        consider(target, relationship, via, "terminal")
    elif target.startswith("component."):
        consider(target, relationship, via, "component")


def _derive_containment(kernel: Kernel, nodes: dict[str, dict[str, Any]]) -> None:
    containers_for: dict[str, list[str]] = {}
    systems_for_cap: dict[str, list[str]] = {}
    systems_for_container: dict[str, list[str]] = {}
    for doc in kernel.docs:
        if doc.level == "container":
            for contained in as_str_list(dig(doc.data, "relationships", "contains")):
                containers_for.setdefault(contained, []).append(doc.spec_id)
        elif doc.level == "system":
            for cap_id in as_str_list(dig(doc.data, "system_context", "capabilities")):
                systems_for_cap.setdefault(cap_id, []).append(doc.spec_id)
            for container_id in as_str_list(dig(doc.data, "relationships", "contains")):
                systems_for_container.setdefault(container_id, []).append(doc.spec_id)

    def add(target: str, relationship: str, via: str) -> None:
        if target in nodes or via not in nodes:
            return
        parent = nodes[via]["distance"]
        nodes[target] = _node(
            target,
            _level_of(kernel, target),
            parent + 1,
            "derived",
            relationship,
            via,
            _DERIVED_NOTE,
        )

    component_ids = [spec_id for spec_id, node in nodes.items() if node["level"] == "component"]
    for comp_id in component_ids:
        for container_id in containers_for.get(comp_id, []):
            add(container_id, "relationships.contains", comp_id)
    capability_ids = [spec_id for spec_id, node in nodes.items() if node["level"] == "capability"]
    for cap_id in capability_ids:
        for system_id in systems_for_cap.get(cap_id, []):
            add(system_id, "system_context.capabilities", cap_id)
    container_ids = [spec_id for spec_id, node in list(nodes.items()) if node["level"] == "container"]
    for container_id in container_ids:
        for system_id in systems_for_container.get(container_id, []):
            add(system_id, "relationships.contains", container_id)


def _node(
    spec_id: str,
    level: str,
    distance: int,
    epistemic: str,
    relationship: str,
    via: str,
    note: str,
) -> dict[str, Any]:
    return {
        "id": spec_id,
        "level": level,
        "distance": distance,
        "direct": distance <= 1,
        "epistemic_state": epistemic,
        "relationship": relationship,
        "via": via,
        "note": note,
    }


def _public_node(nodes: dict[str, dict[str, Any]], spec_id: str) -> dict[str, Any]:
    node = nodes[spec_id]
    epistemic = str(node["epistemic_state"])
    source = "spec" if epistemic != "derived" else f"inverse:{node['relationship']}"
    return {
        "id": node["id"],
        "level": node["level"],
        "distance": node["distance"],
        "direct": node["direct"],
        "epistemic_state": epistemic,
        "relationship": node["relationship"],
        "source": source,
        "path": _path(nodes, spec_id),
        "note": node["note"],
    }


def _path(nodes: dict[str, dict[str, Any]], spec_id: str) -> list[dict[str, str]]:
    steps: list[dict[str, str]] = []
    current = spec_id
    seen: set[str] = set()
    while nodes[current].get("via"):
        prev = str(nodes[current]["via"])
        if current in seen or prev not in nodes:
            break
        seen.add(current)
        steps.append(
            {
                "from": prev,
                "relationship": str(nodes[current]["relationship"]),
                "to": current,
            }
        )
        current = prev
    steps.reverse()
    return steps


def _sorted_ids(nodes: dict[str, dict[str, Any]]) -> list[str]:
    return sorted(nodes, key=lambda spec_id: (nodes[spec_id]["distance"], spec_id))


def _blast_ids(affected: list[dict[str, Any]]) -> tuple[set[str], set[str], set[str]]:
    caps: set[str] = set()
    comps: set[str] = set()
    founds: set[str] = set()
    for node in affected:
        if node["epistemic_state"] == "derived":
            continue
        level = node["level"]
        spec_id = str(node["id"])
        if level == "capability":
            caps.add(spec_id)
        elif level == "component":
            comps.add(spec_id)
        elif level == "foundation":
            founds.add(spec_id)
    return caps, comps, founds


def _start_mode(level: str) -> str:
    if level in _RANK and level != "terminal" and level != "foundation_user":
        return level
    return "terminal"


def _level_of(kernel: Kernel, spec_id: str) -> str:
    doc = kernel.by_id.get(spec_id)
    if doc is not None:
        return doc.level
    for prefix, level in (
        ("capability.", "capability"),
        ("foundation.", "foundation"),
        ("component.", "component"),
        ("container.", "container"),
        ("system.", "system"),
        ("change.", "change"),
    ):
        if spec_id.startswith(prefix):
            return level
    return ""


def _find_change(kernel: Kernel, token: str) -> Change | None:
    folder = token[7:] if token.startswith("change.") else token
    for change in kernel.changes:
        if change.path.name == folder or change.change_id == token or change.change_id == folder:
            return change
    return None


def _item(subject: str, kind: str, source: str, detail: str) -> dict[str, Any]:
    return {
        "subject": subject,
        "kind": kind,
        "epistemic_state": "declared",
        "source": source,
        "detail": detail,
    }


def _flow_item(subject: str, flow: Any) -> dict[str, Any]:
    if isinstance(flow, str):
        return _item(subject, "flow", "flows", flow)
    if isinstance(flow, dict):
        flow_id = str(flow.get("id") or "")
        goal = str(flow.get("goal") or "")
        detail = flow_id or goal
        item = _item(subject, "flow", "flows", detail)
        item["flow_id"] = flow_id
        if goal:
            item["goal"] = goal
        kinds = flow.get("kinds")
        if isinstance(kinds, list) and kinds:
            item["kinds"] = [str(kind) for kind in kinds]
        return item
    return _item(subject, "flow", "flows", str(flow))


def _sensor(subject: str, kind: str, source: str, detail: str) -> dict[str, Any]:
    return {
        "subject": subject,
        "kind": kind,
        "epistemic_state": "declared",
        "source": source,
        "detail": detail,
        "note": _SENSOR_NOTE,
    }


def _owner(subject: str, owner: str, epistemic: str, source: str) -> dict[str, Any]:
    return {
        "subject": subject,
        "owner": owner,
        "epistemic_state": epistemic,
        "source": source,
    }


def _constraint_entries(constraints: dict[str, Any]) -> list[tuple[str, list[str]]]:
    entries: list[tuple[str, list[str]]] = []
    for key, value in constraints.items():
        if isinstance(value, str) and value.strip():
            entries.append((str(key), [value.strip()]))
        elif isinstance(value, list):
            texts = _texts(value)
            if texts:
                entries.append((str(key), texts))
    return entries


def _texts(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            if isinstance(item, str) and item.strip():
                out.append(item)
            elif isinstance(item, dict):
                label = item.get("name") or item.get("id") or item.get("question")
                if isinstance(label, str) and label.strip():
                    out.append(label)
        return out
    return []


def _questions(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            out.append(item)
        elif isinstance(item, dict):
            text = item.get("question") or item.get("id")
            if isinstance(text, str) and text.strip():
                out.append(text)
    return out


def _event_names(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    names: list[str] = []
    for item in value:
        if isinstance(item, dict) and item.get("name"):
            names.append(str(item["name"]))
        elif isinstance(item, str) and item.strip():
            names.append(item)
    return names


def _strategy_entries(value: Any) -> list[tuple[str, str]]:
    if not isinstance(value, dict):
        return []
    entries: list[tuple[str, str]] = []
    for key, raw in value.items():
        if raw is False or raw is None or raw == "":
            if raw is False:
                entries.append((str(key), "false"))
            continue
        if raw is True:
            entries.append((str(key), "true"))
        elif _filled(raw):
            entries.append((str(key), str(raw)))
    return entries


def _strategy_is_evidence(entries: list[tuple[str, str]]) -> bool:
    """A declared non-empty strategy is intent, not a pass. Explicit false is not evidence."""
    return any(detail not in {"false", ""} for _name, detail in entries)


def _filled(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return len(value) > 0
    return True


def _flow_ids(kernel: Kernel, affected: list[dict[str, Any]]) -> set[str]:
    found: set[str] = set()
    for node in affected:
        if node["level"] != "capability":
            continue
        doc = kernel.by_id.get(str(node["id"]))
        if doc is None:
            continue
        flows = doc.data.get("flows")
        if not isinstance(flows, list):
            continue
        for flow in flows:
            if isinstance(flow, dict) and isinstance(flow.get("id"), str) and flow["id"].strip():
                found.add(flow["id"])
    return found


def _codeowners_rules(spec_root: Path) -> list[tuple[str, list[str]]]:
    for candidate in (spec_root.parent / "CODEOWNERS", spec_root / "CODEOWNERS"):
        if candidate.is_file():
            return _parse_codeowners(candidate.read_text(encoding="utf-8"))
    return []


def _parse_codeowners(text: str) -> list[tuple[str, list[str]]]:
    rules: list[tuple[str, list[str]]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split()
        if len(parts) < 2:
            continue
        rules.append((parts[0], parts[1:]))
    return rules


def _owners_for_paths(paths: list[str], rules: list[tuple[str, list[str]]]) -> list[str]:
    found: list[str] = []
    for path in paths:
        owners: list[str] = []
        for pattern, pattern_owners in rules:
            if _codeowners_match(pattern, path):
                owners = pattern_owners
        for owner in owners:
            if owner not in found:
                found.append(owner)
    return found


def _codeowners_match(pattern: str, path: str) -> bool:
    pat = pattern.strip()
    if pat.startswith("/"):
        pat = pat[1:]
    rel = path.strip().lstrip("/")
    if not pat or not rel:
        return False
    if pat.endswith("/"):
        return rel.startswith(pat) or f"{rel}/".startswith(pat)
    return fnmatch(rel, pat)
