# Kernel product specs

`specs/` is the **kernel product** — SpecPlane specifying its own CLI (first slice: epistemic bit, retrieve, blast, check_sync, change folders).

`specplane/` is the **kit** — schema, applicable sections, foundation boilerplates. Copy the kit into other apps.

**Do not copy this `specs/` tree into other apps.** It is not a starter product. Consumers write their own `specs/` against the kit. `capability.specplane_retrieve` is namespaced on purpose.

`design-docs/` is gitignored strategy, not specs. H01’s location is superseded; YAML lives here and is committed. Schema v9.1.0. Branch: `kernel-first-slice`. Handoff: [`../design-docs/handoffs/H02-relocate-specs.md`](../design-docs/handoffs/H02-relocate-specs.md) (local).

This pass **stops for examination**. No schema edits, no CLI implementation.

---

## Tree

```text
specs/
├── README.md                          ← you are here
├── system.specplane_kernel.yaml
├── changes/honest_kernel/             ← in-flight delta this slice *is* (kind: evolve)
│   ├── proposal.yaml
│   ├── delta.yaml
│   ├── success.yaml
│   └── decision.md
├── capabilities/
│   ├── capability.specplane_validate.yaml
│   ├── capability.specplane_retrieve.yaml
│   ├── capability.specplane_blast.yaml
│   ├── capability.specplane_check_sync.yaml
│   ├── capability.specplane_list_gaps.yaml
│   └── capability.specplane_change_folders.yaml
├── foundations/
│   ├── foundation.epistemic_status.yaml    ← live | inferred | in-flight | replaced
│   ├── foundation.join_key.yaml
│   ├── foundation.error_handling.yaml
│   └── foundation.observability_standards.yaml
├── containers/
│   └── container.specplane_tools.yaml      ← 5C layout, not a SKU
└── components/specplane_tools/
    ├── component.cli_validate.yaml
    ├── component.cli_retrieve.yaml
    ├── component.cli_blast.yaml
    ├── component.cli_check_sync.yaml
    └── component.mcp_stdio.yaml
```

These YAML files still use **v9.1.0** `meta.status` / `review_state` (`planned`, `draft`, `unreviewed`). The four-value bit is specified as `foundation.epistemic_status`, not applied as a new field yet.

---

## What is Phase 1 vs later

**Phase 1 (this pass)** — capabilities have `responsibilities`, `flows`, `business_value`, `constraints`. Kill-test capabilities also have `success_metrics` (jobs 2–3). Components are planning + `implements` + `uses` + dependency links. Not how.

**In this slice, not yet a schema/CLI commit**

| Ship | Spec ids |
|---|---|
| Epistemic bit | `foundation.epistemic_status` |
| Join key | `foundation.join_key` |
| CLI `validate` / `retrieve` / `blast` / `check_sync` | matching capabilities + `component.cli_*` |
| MCP `retrieve` / `blast` / `check_sync` / `list_gaps` | `component.mcp_stdio` (validate is CLI; agents shell out) |
| Change folders | `capability.specplane_change_folders` + `specs/changes/honest_kernel/` |

**Explicitly later (do not author here):** infer CLI, YAML→MD, PR comment, hints, viewer, GitHub App, coach, OpenSpec pack, `init/scan`, QA agent, Figma ingest, hosted MCP, Autonomous Build Pack stdout tables.

**Phase-incomplete on purpose**

- `capability.specplane_change_folders` has empty `realized_by` — the write path is the folder convention, not a sixth CLI personality (`open_delta` is the folder).
- `list_gaps` has no `component.cli_*` — MCP-only this slice (H02).
- Components have no `implementation.interface` / contracts / rollout — not how.
- Blast edge traversal (foundations terminal or not) is **Build Pack**, not these files.
- Exact CLI stdout and exit codes are **Build Pack**.
- How `check_sync` detects a named behavior in code waits for the Build Pack. No grep rules in Phase 1.
- Pointer field from live id → change object is **schema unfreeze** (Q71 default recorded in `changes/honest_kernel/`; no new v9.1.0 meta key).

---

## H02 defaults (applied)

| Topic | Default |
|---|---|
| CLI | `validate`, `retrieve`, `blast`, `check_sync` |
| MCP | `retrieve`, `blast`, `check_sync`, `list_gaps` — validate is **not** an MCP tool |
| `list_gaps` CLI | Not this slice |
| `container.specplane_tools` | Keep — 5C layout, not a SKU |
| `check_sync` heuristic | Fail-when stays; do not invent |
| Live-id pointer field | Q71 recorded; field name waits for schema unfreeze |
| `changes/` | `specs/changes/` — same layout consuming repos will use |

Older Qs still used: 53 four-value bit; 43 retrieve+check_sync together; 54 infer not a 6th MCP tool; 94/98 full blast, interruption later; 96 Phase 1 bar; 97 retrieve-time join.

---

## How a coding agent should consume this

After examination (roadmap sign-off box 2):

1. Implement from **this** tree + the Build Pack (not written yet). Do not invent CLI behavior that is not here.
2. Overlay, not Tessl: agents still write the CLI in `tools/specplane/`; these specs do not compile into Python.
3. Call retrieve/blast/check_sync once they exist; shell out for validate; do not teach “read `specs/`” as the habit.
4. Sequence: Build Pack (stdout, blast traversal, fixtures) → unfreeze schema/`validate.py` on this branch → three agent tasks (validate+retrieve+blast → check_sync+folders → MCP/skill).
5. Copy-the-kit to other products copies `specplane/`, skills, and rules — **not** this folder.

```bash
python3 tools/specplane/validate.py --spec-root specs
```

v9.1.0 `validate.py` loads every `*.yaml` under the spec root. `specs/changes/` is convention, not 5C; those files are not kernel spec types yet. Structural validate is the 5C tree.

---

## Out of slice

Viewer, GitHub App, coach, infer-the-world, copying this `specs/` into other apps, Claude’s enum, `raw/` directories, flattening L22 vs L28 GTM tensions.
