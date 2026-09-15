---
name: specplane-bootstrap
description: Initialize a SpecPlane specs/ tree (capabilities, foundations, system, containers, components). Use when the user asks to set up SpecPlane, scaffold specs, or start a new spec workspace.
---

# SpecPlane Bootstrap

## Load

Read `specplane/core_prompt/applicable/02-file-layout.md` and `03-shared-meta.md`. Do not load the full master prompt.

## Procedure

1. Create:
   - `specs/capabilities/`
   - `specs/foundations/`
   - `specs/containers/`
   - `specs/components/`
2. Add one `specs/system.<name>.yaml`.
3. If the user named capabilities or foundations, create those files; otherwise create one example capability and copy needed files from `specplane/foundations/`.
4. Every file: `meta.id` equals filename without extension, semver `version`, `introduced_in`, at least one `changelog` entry.
5. If `tools/specplane/validate.py` exists, run it in this session. Do not add git hooks or CI.
6. Report the tree and the next authoring step (usually capability Phase 1).
