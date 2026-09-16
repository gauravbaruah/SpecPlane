---
name: specplane-validate
description: Validate SpecPlane YAML for naming, required meta, changelog, bidirectional links, and completeness. Use when the user asks to review, audit, or check specs.
---

# SpecPlane Validate

## Load

Read `specplane/core_prompt/applicable/08-validation-rules.md` and `11-guidance-and-checklists.md`. Do not load the full master prompt.

## Procedure

1. If `tools/specplane/validate.py` exists, run it in this session (`--spec-root specs`). Do not add git hooks or CI jobs.
2. Optionally run `python3 tools/specplane/drift.py --scope changed` as a reminder, not as a required gate.
3. Read `specplane/core_prompt/applicable/08-validation-rules.md` and `11-guidance-and-checklists.md` for findings the CLI cannot see (wording, completeness).
4. Report by severity:
   - blocker: CLI errors (id/filename, links, semver, changelog)
   - warn: CLI warnings plus incomplete Phase 2/3
   - info: naming or wording
5. Suggest the smallest fix per finding. Do not rewrite unrelated sections.
