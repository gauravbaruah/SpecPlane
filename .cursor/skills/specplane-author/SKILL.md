---
name: specplane-author
description: Create or expand SpecPlane YAML specs (capability, foundation, system, container, component, AI-native types). Use when the user explicitly asks to write, add, or update a specification file. If they described a product change in natural language, use specplane-implement instead.
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

1. If this is a **behavior change to something that already exists**, stop and follow `specplane-implement` (retrieve, classify, change folder). Do not silently patch live YAML.
2. If `tools/specplane/cli.py` exists and you have an id, `retrieve` it first. Do not slurp `specs/`.
3. Identify level and (for components) `meta.type` / `meta.domain`.
4. **Where to write:**
   - Brand-new capability with no live id: Phase 1 live file is OK (`responsibilities`, `flows`, `business_value`, `constraints`).
   - In-flight work or an open change: put ADDED/MODIFIED YAML in `specs/changes/<id>/`, not as a changelog novel on the live file.
5. Set `meta.id` to the filename without extension. Use snake_case ids.
6. If adding `implements`, `uses`, or internal dependencies, update the other side of the link in the same change.
7. Add a `changelog` row and bump `meta.version` only on **live** 5C files. Change-folder YAML (`proposal` / `delta` / `success`) is not 5C meta.
8. If `tools/specplane/cli.py` exists, run `validate` in this session. Do not add git hooks or CI.
9. Summarize what was authored and what is still Phase-incomplete.
