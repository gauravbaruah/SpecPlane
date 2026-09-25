---
name: specplane-infer
description: Map an existing repository into a handful of Phase 1 inferred capability specs. Use when the user says map this, brownfield, what's already here, or infer specs from this repo. Not for an empty tree (use specplane-bootstrap). Never write live specs and never scan source from a CLI.
---

# SpecPlane Infer

Brownfield on-ramp. One named root. One shot. A handful of capabilities. Then stop.

The coding agent walks the tree. SpecPlane does not. There is no `infer` CLI and no MCP infer. `inferred` is not live.

## When

- The user has an existing repo and asks to map it, brownfield it, or say what is already here.
- They may name a path, a service, or "the API". That name is the root. Use the workspace root only when they did not name a smaller one.

## When not

- Empty `specs/` and they want to start a product: `specplane-bootstrap`. Greenfield init does not infer.
- They described a product change: `specplane-implement`.
- They asked to author one spec they already understand: `specplane-author`.
- Drift, `realization.paths`, or "does this code match the spec": that is not this skill.

## Load

1. `specplane/core_prompt/applicable/README.md`
2. `03-shared-meta.md`
3. `04-capability.md`

Do not load the full v9.1.0 reference. Do not invent containers, components, systems, or evaluators.

## Walk

You already have the tree, the languages, and the configs. Read the README, manifests, and the directories under the named root. Different languages are your problem. Do not ask the kernel to parse `.py`, `.go`, or `.ts`.

Write at most **7** capabilities. If the root is larger, say what you left out and stop. Do not boil a monorepo.

## Write

Phase 1 capability files only, under `specs/capabilities/`. Filename equals `meta.id`.

Five questions, in the usual fields:

| Question | Field |
|---|---|
| Purpose | `meta.purpose` |
| Contract | `responsibilities` |
| Failure | `constraints` (what must not happen). A flow name if the failure is a path. Do not invent a `failure:` key. |
| Constraint | `constraints` |
| Success | `business_value.user_outcome` |

Also required so the file validates: `flows` as string names when you know them, `business_value.objective`, `revenue_dependency`, `strategic_priority`, `constraints.data_classification`, `meta` (`id`, `level: capability`, `version`, `introduced_in`, `status`, `review_state`, `last_updated`), and a `changelog` row.

Every file:

- `tags` includes `inferred`.
- `refs` cite repo-relative paths that show why the guess exists. Cites are evidence of the guess. They are not `realization.paths`.

```yaml
meta:
  id: "capability.billing_checkout"
  purpose: "Customer completes paid checkout"
  level: "capability"
  owner: ""
  tags: ["inferred"]
  last_updated: "YYYY-MM-DD"
  status: "planned"
  version: "1.0.0"
  review_state: "unreviewed"
  introduced_in: "1.0.0"
changelog:
  - date: "YYYY-MM-DD"
    author: "infer"
    summary: "Inferred Phase 1 from the named root"
    breaking: false
responsibilities:
  - "Accept payment and record the order"
flows:
  - "Checkout"
business_value:
  user_outcome: "Customer completes paid checkout"
  objective: "Take payment"
  revenue_dependency: "high"
  strategic_priority: "core"
constraints:
  security: []
  legal: []
  ux:
    - "Do not confirm the order when payment fails"
  data_classification: "confidential"
refs:
  - id: "cite_checkout"
    type: "other"
    path: "src/billing/checkout.py"
    title: "Why this guess"
```

Do not set `realized_by`. Do not omit `inferred`. Do not overwrite a file that is already live (no `inferred` tag).

## Stop

After the handful, stop. Tell the human the ids and the cites. Ask which ids to promote. Wait.

## Promote

Only after the human names ids:

```bash
python3 tools/specplane/cli.py promote --ids id1,id2 --spec-root specs
```

That command drops `inferred` on those files and adds a changelog row. It does not promote unnamed ids. Do not drop the tag yourself.

`retrieve` prints `inferred (not live)` until then. `list_gaps` lists `inferred_unpromoted` and stays advisory.

## Again later

A later map is a new change folder under `specplane-implement` when a live promise would move. Do not re-infer on a schedule. Do not stamp live to match code.
