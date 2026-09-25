# SpecPlane

Git-native YAML specifications for what a system should do and how well — not how it is implemented.

Default schema: **v9.1.0** (5C: Capability, System, Container, Component, plus Foundations). Simpler C4-only path: **v6.1.0**.

## Two trees in this repo

Do not collapse these. That is how the recursive definition stays honest.

| Tree | What it is | Agents |
|---|---|---|
| `specplane/` | The **kit** — schema, applicable sections, foundation *boilerplates* | Load applicable sections. Copy this into other products. |
| `specs/` | The **kernel product** — what SpecPlane-the-CLI must do and how well (first slice: bit, retrieve, blast, check_sync, change folders) | Author and implement *this product* from here. |
| `tools/specplane/` | Realization of the kernel (`cli.py`: validate, retrieve, blast, check_sync, reconcile, list_gaps, run, promote, init; optional MCP) | Implement against `specs/`, not against brainstorm prose. Call the CLI; do not slurp `specs/`. |
| `design-docs/` | Local strategy (gitignored) | Do not publish. Do not treat as specs. |

**Copy-the-kit** into another repo copies `specplane/`, skills, and rules. It does **not** copy `specs/`. Those YAML files are SpecPlane specifying itself, not a starter app.

## Agent loading contract

Do **not** ingest the full master prompt into a coding session.

1. Read this file.
2. For spec work, open [`specplane/core_prompt/applicable/README.md`](specplane/core_prompt/applicable/README.md) and load **only** the section that matches the task.
3. Open [`specplane/core_prompt/specplane_schema_prompt_v9.1.0.md`](specplane/core_prompt/specplane_schema_prompt_v9.1.0.md) only when changing the schema itself or when the user asks for the complete reference.

| Task | Skill | Applicable sections |
|---|---|---|
| Init a `specs/` tree | `specplane-bootstrap` | 02, 03 |
| Product request in natural language (feature, bug, experiment) | `specplane-implement` | retrieve/blast first; 06 when coding; 08 at promote |
| Create or expand YAML (user asked to spec) | `specplane-author` | 03 + the matching type (04–07), example in 10 |
| Enhance journeys / lifecycles / info flows | `specplane-flows` | 04 (and 06 if a component sliver); do not invent answers |
| Review or check a spec | `specplane-validate` | 08, 11; `cli.py validate` / `check_sync` |
| Map an existing repo (brownfield) | `specplane-infer` | 03, 04; stop and ask which ids to promote |

Intended chat shape (human never types `retrieve`): [`docs/golden-journey.md`](docs/golden-journey.md).

## This repository

Ships the **kit** and the **kernel product specs**. Other products still copy the kit: [docs/use-in-your-project.md](docs/use-in-your-project.md).

```
specplane/                 # kit: language
specs/                     # kernel product: overlay of what we are building
tools/specplane/           # kernel realization (CLI)
examples/tiny-saas/        # synthetic try-path (not kernel specs, not a private product)
.agents/skills/specplane-*
.cursor/skills/specplane-* # keep identical to .agents
.cursor/rules/
legacy/specplane_viewer/   # archived; do not extend
```

Private and gitignored (do not commit, do not publish): `trial-implementations/`, `experiments/`, `legacy/initial_ideation_validation/`, `legacy/specplane_viewer/test_cases/`, `design-docs/`.

## Spec rules (`specs/` in this repo or any consumer)

- Filename without extension equals `meta.id`.
- Capability-first: Phase 1 is valid without architecture.
- Bidirectional links in the same change: `implements` ↔ `realized_by`, `uses` ↔ `used_by`, `dependencies.internal` ↔ `depended_on_by`.
- Changelog entry whenever `meta.version` changes **on live 5C files**.
- In-flight writes go in `specs/changes/<id>/`. Do not turn live YAML into diaries.
- Call `tools/specplane/cli.py retrieve|blast|check_sync|run`; do not slurp `specs/`.
- **PRE / POST:** retrieve when a promise might move (if unsure, retrieve); `check_sync --change <slug> --changed-ids`, then `run --change <slug>`, after those changes. Typos/renames skip retrieve. Ceremony scales with semantic consequence, not diff size. A coverage pass is declared coverage, not behavioral agreement. `run` invokes bound checks only; it does not create tests or certify behavior.
- Specs before code when behavior, contracts, events, rollout, security, **or how the product is obtained** (init/install/README CLI claims) change.

## Working on SpecPlane itself

Two different jobs — pick one per session:

1. **Kit / schema** — field changes go in the v9.1.0 **reference** first, then the matching applicable section. Do not put schema prose into `specs/`.
2. **Kernel product** — if it could move a kernel promise, PRE retrieve, open a change folder, **wait** on consequential questions, then implement in `tools/specplane/`. That tree is the app: POST must `check_sync --change <slug> --changed-ids`, then `run --change <slug>`, for the matching `component.cli_*`. Do not invent CLI behavior that is not in `specs/`.

Do not resurrect the Docusaurus viewer. Do not copy private consumer toolkits (Bhajami, Progress Flow) into this repo. Do not treat `specplane/foundations/` boilerplates as the kernel product tree.

