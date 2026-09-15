---
name: specplane-implement
description: Implement or change code from SpecPlane specs so behavior and specs stay aligned. Use when the user asks to build, code, or refactor against a spec, or when a behavior change may need a spec update.
---

# SpecPlane Implement

## Load

Read `specplane/core_prompt/applicable/README.md`. Then load `06-system-container-component.md` for contracts, validation, and rollout. Load `08-validation-rules.md` if links or versions will change.

Do not load the full master prompt.

## Procedure

1. Find the matching spec(s) under `specs/` (or say if this repo has none).
2. If behavior, contracts, events, dependencies, rollout, or security change: update those spec fields in the same task, with changelog + version bump.
3. If there is no spec impact, state that before writing code.
4. Implement to the spec: capabilities, errors, states, acceptance criteria, emitted events.
5. Keep bidirectional links valid if you touched `implements` / `uses` / dependencies.
6. Summarize spec files changed, code files changed, and any remaining drift.
