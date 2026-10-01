---
name: specplane-validate
description: Validate SpecPlane YAML and kernel sync (naming, links, changelog, retrieve leftovers, check_sync). Use when the user asks to review, audit, or check specs — not for implementing a product change.
---

# SpecPlane Validate

## Load

Read `specplane/core_prompt/applicable/08-validation-rules.md` and `11-guidance-and-checklists.md`. Do not load the full master prompt.

## Procedure

1. Prefer the kernel CLI when present (`--spec-root specs`). Do not add git hooks or CI jobs.

   ```bash
   python3 tools/specplane/cli.py validate --spec-root specs
   python3 tools/specplane/cli.py check_sync --spec-root specs
   ```

   `python3 tools/specplane/validate.py` is validate-only. Use `cli.py retrieve <id>` / `blast <id>` when the review is about one promise or impact, not the whole tree.

   Set `SPECPLANE_CALLER=cursor_skill` on those commands. A local event is recorded unless `telemetry disable` was run. Nothing is uploaded.

   If a command prints a line that starts with `SpecPlane ·`, quote that line in the reply the user sees, unchanged. If it does not, do not invent a SpecPlane receipt. Do not say SpecPlane caught a bug or revised the code unless that printed line says so.

2. Optionally run `python3 tools/specplane/drift.py --scope changed` as a reminder, not as a required gate.

3. Read sections 08 and 11 for findings the CLI cannot see (wording, completeness).

4. Report by severity:
   - blocker: CLI errors (id/filename, links, semver, changelog, `check_sync` uncovered ids)
   - warn: CLI warnings plus incomplete Phase 2/3; leftover graphs `retrieve` marked replaced
   - info: naming or wording

5. Suggest the smallest fix per finding. Do not rewrite unrelated sections. Do not silently pick spec vs code.
