# Kernel product specs

`specs/` is the **kernel product** — SpecPlane specifying its own CLI (first slice: epistemic bit, retrieve, blast, check_sync, change folders).

`specplane/` is the **kit** — schema, applicable sections, foundation boilerplates. Copy the kit into other apps.

**Do not copy this `specs/` tree into other apps.** It is not a starter product. Consumers write their own `specs/` against the kit. `capability.specplane_retrieve` is namespaced on purpose.

`design-docs/` is gitignored strategy, not specs. H01’s location is superseded; YAML lives here and is committed. Schema v9.1.0. Branch: `kernel-first-slice`. Handoff: [`../design-docs/handoffs/H02-relocate-specs.md`](../design-docs/handoffs/H02-relocate-specs.md) (local).

This pass **implemented the simple CLI** in `tools/specplane/cli.py`. Schema v9.1.0 is still unfrozen for the four-value bit field; v1 maps `deprecated`/`replaced_by` → replaced. MCP is not built yet. Skills/`AGENTS.md` now follow [`docs/golden-journey.md`](../docs/golden-journey.md) (change ritual); they no longer teach “edit live YAML in the same task.”

---

## Tree

```text
specs/
├── README.md                          ← you are here
├── system.specplane_kernel.yaml
├── changes/
│   ├── honest_kernel/                 ← first-slice kernel (kind: evolve)
│   └── kit_init/                      ← v0 copier + empty specs/ dirs
├── capabilities/
│   ├── capability.specplane_validate.yaml
│   ├── capability.specplane_retrieve.yaml
│   ├── capability.specplane_blast.yaml
│   ├── capability.specplane_check_sync.yaml
│   ├── capability.specplane_list_gaps.yaml
│   ├── capability.specplane_change_folders.yaml
│   └── capability.specplane_init.yaml
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
    ├── component.cli_init.yaml
    └── component.mcp_stdio.yaml
```

These YAML files still use **v9.1.0** `meta.status` / `review_state` (`planned`, `draft`, `unreviewed`). The four-value bit is specified as `foundation.epistemic_status`, not applied as a new field yet.

---

## What is Phase 1 vs later

**Phase 1 (this pass)** — capabilities have `responsibilities`, `flows`, `business_value`, `constraints`. Kill-test capabilities also have `success_metrics` (jobs 2–3). Components are planning + `implements` + `uses` + dependency links. Not how.

**In this slice**

| Ship | Spec ids | Code |
|---|---|---|
| Epistemic bit (retrieve default-graph) | `foundation.epistemic_status` | mapped from v9.1.0 status until schema unfreeze |
| Join key | `foundation.join_key` | graph walk uses these ids |
| CLI `validate` / `retrieve` / `blast` / `check_sync` | matching capabilities + `component.cli_*` | `tools/specplane/cli.py` |
| CLI `init` | `capability.specplane_init` + `component.cli_init` | `tools/specplane/initkit.py` — copy kit, empty `specs/` dirs, no kernel `specs/` |
| MCP `retrieve` / `blast` / `check_sync` / `list_gaps` | `component.mcp_stdio` | not built this pass |
| Change folders | `capability.specplane_change_folders` + `specs/changes/` | loaded by retrieve/check_sync; skipped by structural validate |

**Explicitly later:** infer CLI, YAML→MD, PR comment, hints, viewer, GitHub App, coach, OpenSpec pack, `npx`/`uvx`/`scan`, QA agent, Figma ingest, hosted MCP, MCP stdio, `list_gaps` CLI.

**Still later / schema**

- Pointer field from live id → change object (Q71).
- Four-value bit as a real `meta` field (v1 maps deprecated/replaced_by).
- check_sync does not parse application source (timeout 30 vs 60). Sensors as runnable tests come next.

```bash
python3 tools/specplane/cli.py validate --spec-root specs
python3 tools/specplane/cli.py retrieve capability.specplane_retrieve --spec-root specs
python3 tools/specplane/cli.py blast component.cli_retrieve --spec-root specs
python3 tools/specplane/cli.py check_sync --spec-root specs --changed-ids component.cli_retrieve
```

---

## H02 defaults (applied)

| Topic | Default |
|---|---|
| CLI | `validate`, `retrieve`, `blast`, `check_sync`, `init` |
| MCP | `retrieve`, `blast`, `check_sync`, `list_gaps` — validate is **not** an MCP tool |
| `list_gaps` CLI | Not this slice |
| `container.specplane_tools` | Keep — 5C layout, not a SKU |
| `check_sync` heuristic | v1: `--changed-ids` or spec YAML in git vs open change `promise_ids` |
| Live-id pointer field | Q71 recorded; field name waits for schema unfreeze |
| `changes/` | `specs/changes/` — same layout consuming repos will use |

Older Qs still used: 53 four-value bit; 43 retrieve+check_sync together; 54 infer not a 6th MCP tool; 94/98 full blast, interruption later; 96 Phase 1 bar; 97 retrieve-time join.

---

## How a coding agent should consume this

Follow [`docs/golden-journey.md`](../docs/golden-journey.md) and `specplane-implement`. Do not slurp `specs/`.

1. Call `tools/specplane/cli.py retrieve|blast|check_sync` (and `validate`).
2. Overlay, not Tessl: the CLI does not compile specs into the product.
3. Copy-the-kit via `cli.py init` (or rsync). Never copy this `specs/` folder.
4. `validate.py` skips `specs/changes/` (convention, not 5C).
5. In-flight writes go in `specs/changes/`. Promote live YAML only after the human accepts.

```bash
python3 tools/specplane/cli.py validate --spec-root specs
python3 tools/specplane/cli.py retrieve capability.specplane_retrieve --spec-root specs
```

---

## Out of slice

Viewer, GitHub App, coach, infer-the-world, copying this `specs/` into other apps, Claude’s enum, `raw/` directories, flattening L22 vs L28 GTM tensions.
