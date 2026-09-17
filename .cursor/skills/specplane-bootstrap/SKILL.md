---
name: specplane-bootstrap
description: Initialize a SpecPlane specs/ tree (capabilities, foundations, system, containers, components, changes). Use when the user asks to set up SpecPlane, scaffold specs, or start a new spec workspace.
---

# SpecPlane Bootstrap

## Load

Read `specplane/core_prompt/applicable/02-file-layout.md` and `03-shared-meta.md`. Do not load the full master prompt.

## Procedure

1. Create if missing (`cli.py init` may already have empty dirs):
   - `specs/capabilities/`
   - `specs/foundations/`
   - `specs/containers/`
   - `specs/components/`
   - `specs/changes/` (in-flight write path; keep empty until a real change)
2. Add one `specs/system.<name>.yaml` if none exists.
3. If the user named capabilities or foundations, create those files; otherwise create one example capability and copy needed files from `specplane/foundations/`.
4. Every **5C** file: `meta.id` equals filename without extension, semver `version`, `introduced_in`, at least one `changelog` entry. Do not invent fake 5C meta for files under `specs/changes/`.
5. If `tools/specplane/cli.py` exists, run `validate` in this session; else `validate.py`. Do not add git hooks or CI.
6. Report the tree. Next step is usually a Phase 1 capability. Daily product requests after that use `specplane-implement` (see [`docs/golden-journey.md`](../../../docs/golden-journey.md)), not more scaffolding.
