# SpecPlane

Git-native YAML specifications for what a system should do and how well — not how it is implemented.

Default schema: **v9.1.0** (5C: Capability, System, Container, Component, plus Foundations). Simpler C4-only path: **v6.1.0**.

## Agent loading contract

Do **not** ingest the full master prompt into a coding session.

1. Read this file.
2. For spec work, open [`specplane/core_prompt/applicable/README.md`](specplane/core_prompt/applicable/README.md) and load **only** the section that matches the task.
3. Open [`specplane/core_prompt/specplane_schema_prompt_v9.1.0.md`](specplane/core_prompt/specplane_schema_prompt_v9.1.0.md) only when changing the schema itself or when the user asks for the complete reference.

| Task | Skill | Applicable sections |
|---|---|---|
| Init a `specs/` tree | `specplane-bootstrap` | 02, 03 |
| Create or expand a spec | `specplane-author` | 03 + the matching type (04–07), example in 10 |
| Implement code from a spec | `specplane-implement` | 06 contracts/validation; 08 for links |
| Review or check a spec | `specplane-validate` | 08, 11 |

## This repository

This repo ships the schema, foundations, and agent files. It is not a product app with a `specs/` tree of its own.

```
specplane/core_prompt/specplane_schema_prompt_v9.1.0.md   # reference (complete)
specplane/core_prompt/applicable/                         # applicability (split)
specplane/foundations/                                    # 19 boilerplate foundation YAMLs
.agents/skills/specplane-*                                # portable skills (source)
.cursor/skills/specplane-*                                # Cursor copy — keep identical to .agents
.cursor/rules/                                            # Cursor always-on + YAML globs
legacy/specplane_viewer/                                  # archived viewer; do not extend
```

Private and gitignored (do not commit, do not publish): `trial-implementations/`, `experiments/`, `legacy/initial_ideation_validation/`, `legacy/specplane_viewer/test_cases/`, `design-docs/research_references/`.

## Spec rules (when a consuming project has `specs/`)

- Filename without extension equals `meta.id`.
- Capability-first: Phase 1 is valid without architecture.
- Bidirectional links in the same change: `implements` ↔ `realized_by`, `uses` ↔ `used_by`, `dependencies.internal` ↔ `depended_on_by`.
- Changelog entry whenever `meta.version` changes.
- Specs before code when behavior, contracts, events, rollout, or security change. If there is no spec impact, say so.

## Working on SpecPlane itself

- Schema field changes go in the v9.1.0 **reference** file first, then the matching applicable section.
- Do not resurrect the Docusaurus viewer as the product path.
- Do not copy private consumer toolkits (Bhajami, Progress Flow) into this repo.
