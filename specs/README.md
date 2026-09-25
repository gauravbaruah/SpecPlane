# Kernel product specs

`specs/` is the **kernel product** — SpecPlane specifying its own CLI (first slice: epistemic bit, retrieve, blast, check_sync, change folders, run).

`specplane/` is the **kit** — schema, applicable sections, foundation boilerplates. Copy the kit into other apps.

**Do not copy this `specs/` tree into other apps.** It is not a starter product. Consumers write their own `specs/` against the kit. `capability.specplane_retrieve` is namespaced on purpose.

`design-docs/` is gitignored strategy, not specs. H01’s location is superseded; YAML lives here and is committed. Schema v9.1.0. Default branch: `main`. Handoff: [`../design-docs/handoffs/H02-relocate-specs.md`](../design-docs/handoffs/H02-relocate-specs.md) (local).

This pass **implemented the simple CLI** in `tools/specplane/cli.py`. Schema v9.1.0 is still unfrozen for the four-value bit field; v1 maps `deprecated`/`replaced_by` → replaced. `list_gaps` is a CLI command; MCP stdio wraps retrieve / blast / check_sync / list_gaps / run. `run` joins a bound check; it is not a test runner. Skills/`AGENTS.md` follow [`docs/golden-journey.md`](../docs/golden-journey.md).

---

## Tree

```text
specs/
├── README.md                          ← you are here
├── system.specplane_kernel.yaml
├── changes/
│   ├── honest_kernel/                 ← first-slice kernel (kind: evolve)
│   ├── kit_init/                      ← v0 copier + empty specs/ dirs
│   ├── check_sync_honesty/
│   └── list_gaps_mcp/
├── capabilities/
│   ├── capability.specplane_validate.yaml
│   ├── capability.specplane_retrieve.yaml
│   ├── capability.specplane_blast.yaml
│   ├── capability.specplane_check_sync.yaml
│   ├── capability.specplane_list_gaps.yaml
│   ├── capability.specplane_change_folders.yaml
│   ├── capability.specplane_init.yaml
│   ├── capability.specplane_run.yaml
│   └── capability.specplane_promote.yaml
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
    ├── component.cli_list_gaps.yaml
    ├── component.cli_run.yaml
    ├── component.cli_promote.yaml
    ├── component.cli_reconcile.yaml
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
| CLI `list_gaps` + MCP stdio | `capability.specplane_list_gaps` + `component.cli_list_gaps` + `component.mcp_stdio` | same kernel; catalog retrieve/blast/check_sync/list_gaps/run; validate CLI-only |
| CLI `run` | `capability.specplane_run` + `component.cli_run` + `component.mcp_stdio` | join + invoke of a bound check; not a test runner |
| CLI `promote --ids` | `capability.specplane_promote` + `component.cli_promote` | named inferred ids become live; the agent walks via `specplane-infer` |
| CLI `reconcile` | `capability.specplane_reconcile` + `component.cli_reconcile` | optional declared `realization.paths`; missing and unmapped app files are advisory; CLI-only. Greenfield does not need infer. |
| Change folders | `capability.specplane_change_folders` + `specs/changes/` | loaded by retrieve/check_sync; skipped by structural validate |

**Brownfield:** skill `specplane-infer` writes Phase 1 YAML tagged `inferred`. CLI `promote --ids` makes named ids live. No source-parsing infer CLI. No MCP infer.

**Explicitly later:** YAML→MD, PR comment, hints, viewer, GitHub App, coach, OpenSpec pack, `npx`/`uvx`/`scan`, QA agent, Figma ingest, hosted MCP.

**Still later / schema**

- Pointer field from live id → change object (Q71).
- Four-value bit as a real `meta` field (v1 maps deprecated/replaced_by).
- check_sync does not parse application source (timeout 30 vs 60). `run` invokes a check already bound on a change; it does not become the test runner.

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
| CLI | `validate`, `retrieve`, `blast`, `check_sync`, `list_gaps`, `run`, `promote`, `init` |
| MCP | `retrieve`, `blast`, `check_sync`, `list_gaps`, `run` — validate and promote are **not** MCP tools. `run` joins a bound check; it is not a test runner. No infer tool. |
| `list_gaps` CLI | Source of truth; MCP wraps the same kernel (H02 MCP-only superseded) |
| `container.specplane_tools` | Keep — 5C layout, not a SKU |
| `check_sync` heuristic | v1: `--changed-ids` or git diff **plus untracked** `specs/**/*.yaml` (not `changes/`). Phase 1 (no join edges) is advisory. Linked empty blast still fails. |
| Live-id pointer field | Q71 recorded; field name waits for schema unfreeze |
| `changes/` | `specs/changes/` — same layout consuming repos will use |

Older Qs still used: 53 four-value bit; 43 retrieve+check_sync together; 54 infer not a 6th MCP tool; 94/98 full blast, interruption later; 96 Phase 1 bar; 97 retrieve-time join.

---

## How a coding agent should consume this

Follow [`docs/golden-journey.md`](../docs/golden-journey.md) and `specplane-implement`. Do not slurp `specs/`.

1. Call `tools/specplane/cli.py retrieve|blast|check_sync|list_gaps|run` (and `validate`). MCP stdio wraps those five; not validate. `run` invokes bound checks only.
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
