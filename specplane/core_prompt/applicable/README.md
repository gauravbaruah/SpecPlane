# SpecPlane v9.1.0 — Applicable split

Use this directory when **authoring or reviewing specs**. Do not paste the full master prompt into a coding session.

| Document | Role |
|---|---|
| **This file** | Loading contract: which section to read for which task |
| **Section files `01`–`11`** | Applicable split of the v9.1.0 prompt |
| [`specplane_schema_prompt_v9.1.0.md`](../specplane_schema_prompt_v9.1.0.md) | Canonical **reference** — the complete prompt in one file |

The section files are the same schema, split so an agent loads only what the current task needs. If a section and the reference disagree, the reference wins; fix the section.

## Do not load the full prompt when

- Creating or editing a capability, foundation, container, or component spec
- Implementing code from a spec, or a natural-language product change (`specplane-implement`)
- Validating naming, links, or completeness
- Adding a diagram or ref

## Do load the full reference when

- Changing the SpecPlane schema itself
- The user asks for the complete prompt
- You cannot tell which section applies after reading this file and `01`

## Load by task

Always start from this table. Read **only** the listed sections unless a field you need is missing — then open the next listed fallback, not the whole reference.

| Task | Read (in order) |
|---|---|
| First orientation | this file, then [`01-philosophy-and-5c.md`](01-philosophy-and-5c.md) |
| Product request (feature, bug, experiment) | skill `specplane-implement`; [`docs/golden-journey.md`](../../../docs/golden-journey.md); then `06` when coding |
| New `specs/` tree / naming | [`02-file-layout.md`](02-file-layout.md) |
| Any new spec (required meta) | [`03-shared-meta.md`](03-shared-meta.md) |
| Capability spec | `03`, [`04-capability.md`](04-capability.md), capability example in [`10-worked-examples.md`](10-worked-examples.md) |
| Enhance flows / journeys / lifecycles | skill `specplane-flows`; then `04` (and `06` if touching a component sliver) |
| Foundation spec | `03`, [`05-foundation.md`](05-foundation.md), boilerplate in `specplane/foundations/` |
| System / container / component | `03`, [`06-system-container-component.md`](06-system-container-component.md), component example in `10` |
| Agent, tool, workflow, evaluator | `06`, then [`07-ai-native.md`](07-ai-native.md) |
| Validate, review, changelog, links | [`08-validation-rules.md`](08-validation-rules.md), [`11-guidance-and-checklists.md`](11-guidance-and-checklists.md) |
| Diagrams and `{{refs.*}}` | [`09-diagrams-and-refs.md`](09-diagrams-and-refs.md) |
| Schema change to SpecPlane | the [full reference](../specplane_schema_prompt_v9.1.0.md) |

## Progressive disclosure

1. Capability Phase 1 (`responsibilities`, `flows`, `business_value`, `constraints`) is enough to start.
2. Do not invent `realized_by` during early PM work.
3. Components declare `implements` and `uses`; keep the other side of each link in the same change.
4. Specs describe what and how well, not how to implement.

## Related

- Using SpecPlane in a product repo: [`docs/use-in-your-project.md`](../../../docs/use-in-your-project.md)
- Agent ritual (golden journey): [`docs/golden-journey.md`](../../../docs/golden-journey.md)
- Repo router: [`AGENTS.md`](../../../AGENTS.md)
- Simpler C4-only schema (no capability/foundation layer): [`specplane_schema_prompt_v6.1.0_progressive_disclosure.md`](../specplane_schema_prompt_v6.1.0_progressive_disclosure.md)
