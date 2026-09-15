---
name: specplane-validate
description: Validate SpecPlane YAML for naming, required meta, changelog, bidirectional links, and completeness. Use when the user asks to review, audit, or check specs, or before committing spec changes.
---

# SpecPlane Validate

## Load

Read `specplane/core_prompt/applicable/08-validation-rules.md` and `11-guidance-and-checklists.md`. Do not load the full master prompt.

## Procedure

1. Check each changed (or named) spec against rules 1–21 in section 08.
2. Run the quality checklist in section 11 for that spec type.
3. Report by severity:
   - blocker: missing required meta, broken id/filename, one-sided links, version bump without changelog
   - warn: incomplete Phase 2/3, missing diagrams, weak acceptance criteria
   - info: naming or wording
4. Suggest the smallest fix per finding. Do not rewrite unrelated sections.
