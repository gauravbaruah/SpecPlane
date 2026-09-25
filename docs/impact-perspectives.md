# Impact perspectives

One connected SpecPlane graph. One affected subgraph. Several questions asked of that same subgraph.

```text
selected id or open change
        |
        v
  affected subgraph     (deterministic join-key walk, with paths)
        |
        +-- system
        +-- product
        +-- quality
        +-- governance
        +-- ownership
```

`blast` still prints the capability / component / foundation buckets that `check_sync` uses. `impact` is the explainable form of that same membership for a spec id, and it also accepts an open change folder with no git diff.

Perspectives are projections. They are not personas, not extra graphs, and not `qa_view` / `security_view` / `pm_view` objects.

## What the walk includes

The walk matches `blast` for a spec id:

- `implements` and `realized_by.components` (a capability reached through `implements` is not expanded again)
- component `dependencies.internal` and `depended_on_by.components`
- `uses` reaches a foundation and stops (no fan-out through `used_by`)
- a foundation start is one hop to direct users
- `roadmap.depends_on` / `roadmap.enables` are declared product links and are not join-key edges

`impact` also records containers named by `realized_by.containers` without walking `relationships.contains`, and it derives a containing system or container when the inverse edge is the only link. Derived nodes are marked `epistemic_state: derived`. They are not added to the `blast` buckets.

A change root uses `promise_ids`. Distance 1 is that promise. Further hops are transitive. Each affected id keeps the path that explains it.

## What each projection reads

Only fields the schema already has. Nothing is classified by name.

| Perspective | Reads |
|---|---|
| System | The affected ids, grouped by level. Paths stay on `affected`. |
| Product | Capability responsibilities, flows, business value, constraints, success metrics, analytics events, roadmap, open questions, and component `flow_ref`. |
| Quality | Acceptance criteria, test strategy, journeys (flow exceptions and recovery), observability and analytics events, contracts, rollout. |
| Governance | Populated `constraints` keys, and component `technical_constraints.security` (including `compliance` when that field is set). |
| Ownership | `meta.owner` when set. `CODEOWNERS` only when that file exists and a component declares `realization.paths` that match. |

Foundations have no governed-concern field. A foundation in the subgraph is listed as unclassified. Its id is not treated as a privacy or security finding.

`CODEOWNERS` matches are `epistemic_state: derived` and `source: CODEOWNERS`. They do not overwrite `meta.owner`.

## What absence means

Missing fields stay unknown:

- `No ownership information represented.`
- `Governance relationship not identified in current model.`
- `Verification not represented for acceptance criteria on <id>.`
- `Possible impact through inferred dependency.`

A declared test strategy or sensor is evidence that the spec asked for a check. It is not evidence the check passed, and it is not a safety claim.

There is no confidence score. v9.1 edges do not carry one.

## Agents

The impact engine is this deterministic walk. An agent may propose a missing relationship (ownership, a governed concern, a test implication) as inferred spec content with provenance. After that content is in the graph, the same walk propagates it. The agent does not answer "what are the security implications?" as a second blast.

## Schema

No new perspective object, RACI model, or governance enum in this pass. Governed concerns are the constraint and security fields the schema already defines. A future classification for foundations would be a schema change of its own, not a viewer mode.
