# SpecPlane (this product)

This project uses SpecPlane v9.1.0. Specs live in `specs/`. Schema files live in `specplane/`.

Do not ingest `specplane/core_prompt/specplane_schema_prompt_v9.1.0.md` into a coding session.

1. For spec work, open `specplane/core_prompt/applicable/README.md` and load only the section for the task.
2. Skills: specplane-bootstrap, specplane-author, specplane-implement, specplane-validate.
3. Product requests in natural language use **specplane-implement** (retrieve → change folder → blast → decide → code → check_sync). Do not slurp `specs/`.
4. Optional: if `tools/specplane/cli.py` is present, the agent runs it in-session. Do not add git hooks or CI jobs unless you choose to.

Rules:
- Filename without extension equals `meta.id`.
- Capability Phase 1 is valid without architecture.
- Bidirectional links in the same change (`implements` ↔ `realized_by`, `uses` ↔ `used_by`).
- Changelog on live 5C files when `meta.version` changes. In-flight work lives in `specs/changes/`.
- Specs before code when behavior, contracts, events, rollout, or security change. Trivial work: say “no spec impact” and skip the change folder.
