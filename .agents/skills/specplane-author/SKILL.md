---
name: specplane-author
description: Create or expand SpecPlane YAML specs (capability, foundation, system, container, component, AI-native types). Use when the user asks to write, add, or update a SpecPlane specification.
---

# SpecPlane Author

## Load

1. Read `specplane/core_prompt/applicable/README.md`.
2. Read `03-shared-meta.md`.
3. Read **only** the type section:
   - capability → `04-capability.md`
   - foundation → `05-foundation.md` and copy shape from `specplane/foundations/` if starting from boilerplate
   - system / container / component → `06-system-container-component.md`
   - agent / tool / workflow / evaluator / tool_registry / state_store → `06` then `07-ai-native.md`
4. Skim the matching example in `10-worked-examples.md` if the type is capability or component.

Do not load `specplane_schema_prompt_v9.1.0.md` unless a field is missing from those sections.

## Procedure

1. Identify level and (for components) `meta.type` / `meta.domain`.
2. Start minimal: capability Phase 1, or component `meta` + `implements` + planning. Expand only if asked or if the change requires it.
3. Set `meta.id` to the filename without extension. Use snake_case ids.
4. If adding `implements`, `uses`, or internal dependencies, update the other side of the link.
5. Add a `changelog` row; bump `meta.version` on edits.
6. If `tools/specplane/validate.py` exists, run it in this session. Do not add git hooks or CI.
7. Summarize what was authored and what is still Phase-incomplete.
