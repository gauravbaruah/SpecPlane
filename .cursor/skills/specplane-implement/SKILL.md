---
name: specplane-implement
description: Run the SpecPlane change ritual when the user describes a product change, bug, experiment, or feature in natural language, or asks to implement against specs. Classifies trivial/fix/evolve/learn, calls retrieve/blast/check_sync, opens specs/changes/, asks only consequential questions, then implements. Do not use for initializing a specs tree (bootstrap) or when the user only asked to author YAML.
---

# SpecPlane Implement

The user talks about the product. You run SpecPlane. They should not type `retrieve` or `blast`. Intended chat shape: [`docs/golden-journey.md`](../../../docs/golden-journey.md).

Do not slurp `specs/`. Call the kernel CLI. No SpecPlane API key. Do not add git hooks or CI.

## Load

Read `specplane/core_prompt/applicable/README.md`. When writing code, load `06-system-container-component.md` for contracts. Load `08-validation-rules.md` only if live links/versions will change **at promote**.

Do not load the full master prompt.

## Kernel

```bash
python3 tools/specplane/cli.py retrieve <id> --spec-root specs
python3 tools/specplane/cli.py blast <id> --spec-root specs
python3 tools/specplane/cli.py validate --spec-root specs
python3 tools/specplane/cli.py check_sync --spec-root specs --changed-ids id1,id2
```

If `tools/specplane/cli.py` is missing, say so. Do not invent a graph by reading the whole tree. You may open files the CLI already named.

## Procedure

1. **Match live intent.** Guess the capability id from the request. `retrieve` it (or say none exists). Paraphrase as a short human projection: current promise, constraints, open changes. Not a YAML dump.

2. **Propose a class** (do not quiz the user on taxonomy):
   - **trivial** — typo, 4px, rename helper, refactor with the same behavior. Just do it. State “no spec impact.” Stop here.
   - **fix** — live spec already promises this; it is broken or incomplete.
   - **evolve** — the promise itself changes.
   - **learn** — experiment; may not become live law.

   Ceremony follows **semantic consequence**, not diff size. One-line `danger` token change can be evolve. A large internal refactor can be trivial.

   If the class is obvious, state it and continue. Ask “proceed?” only when it could reasonably be another class.

3. **Open a change** unless trivial. Create `specs/changes/<slug>/`:
   - `proposal.yaml` — `kind`, `promise_ids`, `why`
   - `delta.yaml` — ADDED / MODIFIED / REMOVED
   - `success.yaml` — named sensors (`must:` lines are enough)
   - `decision.md` — only if a human must choose

   Do **not** edit live `capability.*.yaml` / `foundation.*.yaml` until promote. New capabilities with no live id: Phase 1 live file **or** ADDED in this folder; prefer a change folder if this request is an evolve of something that exists.

4. **Blast** the promise id and components you will touch. Tell the user “likely affected,” not hop-rule homework. Foundations are terminal.

5. **Interrupt sparingly.** Ask only unresolved consequential questions (prefer one). Record the answer in `decision.md`. **Wait** before implementing. Isolated UI nits are not interruptions; a global foundation/token used by many ids is.

6. **Implement** from the projection: live promise + delta + blast + decisions. Match capabilities, errors, events, and `success.yaml`. Keep bidirectional links if you touch `implements` / `uses` (on files in the change, or at promote).

7. **Reconcile.** Run `validate` and `check_sync --changed-ids` for ids you touched. Optionally `python3 tools/specplane/drift.py --scope changed` as a reminder. Do not pick spec vs code when they disagree — report it.

8. **Promote only after the user accepts.** Then: apply the delta to live YAML, bump `meta.version` + changelog on those live files, move the folder to `specs/changes/_archive/<slug>/`. Retrieve should then show one live graph.

If this repo has no `specs/`, say so and point at bootstrap. Do not copy SpecPlane’s own `specs/` into another app.
