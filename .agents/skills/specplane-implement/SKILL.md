---
name: specplane-implement
description: Run the SpecPlane change ritual when the user describes a product change, bug, experiment, feature, install/docs that state a promise, or asks to implement. PRE: retrieve when a promise might move (if unsure, retrieve). POST check_sync --change after those changes. Typos/renames skip retrieve. Do not use for bootstrap or YAML-only authoring.
---

# SpecPlane Implement

The user talks about the product. You run SpecPlane. They should not type `retrieve` or `blast`. Intended chat shape: [`docs/golden-journey.md`](../../../docs/golden-journey.md).

Do not slurp `specs/`. Call the kernel CLI. No SpecPlane API key. Do not add git hooks or CI.

## Hard gates (not optional)

Developers paste a prompt and expect codegen. You still run SpecPlane **when a product promise might move**. Do not skip because it looks like docs, packaging, README, “just implement,” or “no new capabilities.”

**PRE — if the request could reasonably move a promise** (behavior, contracts, events, security, rollout, how the product is obtained: init/install/README CLI claims):

1. Guess the capability (or component) id. Call `retrieve`. If none exists, say so.
2. Classify **only after** that retrieve.
3. If not trivial: open `specs/changes/<id>/`, `blast`, ask at most one unresolved consequential question, **wait**, then implement.

**PRE — skip retrieve** only when it cannot reasonably move a promise: typo, 4px, rename helper, same-behavior refactor. Say “no spec impact.” If unsure, retrieve — do not guess trivial.

**POST — after a non-trivial implement, before claiming done:**

1. `validate`.
2. `check_sync --change <slug> --changed-ids` with every id you retrieved, blasted, or whose realization files you edited. `<slug>` is this request’s `specs/changes/<slug>/` folder. The default changed-set is **spec YAML in git only**. An empty default is not a pass if you touched app code or `tools/specplane/`. A coverage pass is declared coverage, not behavioral agreement.
3. Do not silently pick spec vs code. Do not edit live 5C YAML until the user accepts (promote).

The kernel does not watch the chat. If you do not call retrieve/check_sync, SpecPlane is silent. Clarifying questions are the coding agent following this skill, not a SpecPlane daemon.

If `tools/specplane/cli.py` is missing, say so and stop implementing product behavior.

## Load

Read `specplane/core_prompt/applicable/README.md`. When writing code, load `06-system-container-component.md` for contracts. Load `08-validation-rules.md` only if live links/versions will change **at promote**.

Do not load the full master prompt.

## Kernel

Prefer `specplane` if it is on PATH, else `python3 tools/specplane/cli.py`.

```bash
python3 tools/specplane/cli.py retrieve <id> --spec-root specs
python3 tools/specplane/cli.py blast <id> --spec-root specs
python3 tools/specplane/cli.py validate --spec-root specs
python3 tools/specplane/cli.py check_sync --spec-root specs --change <slug> --changed-ids id1,id2
```

Do not invent a graph by reading the whole tree. You may open files the CLI already named.

## Procedure

1. **PRE.** If this could move a promise, guess the capability id and `retrieve` it (or say none exists). Paraphrase as a short human projection. If it cannot (typo / 4px / rename / same-behavior refactor), say “no spec impact” and do it — no retrieve. If unsure, retrieve.

2. **Propose a class** (do not quiz the user on taxonomy):
   - **trivial** — cannot reasonably move a promise (typo, 4px, rename helper, behavior-free refactor). Just do it. State “no spec impact.” Stop here.
   - **fix** — live spec already promises this; it is broken or incomplete.
   - **evolve** — the promise itself changes (including how the product is obtained: install, init, “what the README says the CLI does”).
   - **learn** — experiment; may not become live law.

   Ceremony follows **semantic consequence**, not diff size. One-line `danger` token change can be evolve. A large internal refactor can be trivial.

   If the class is obvious, state it and continue. Ask “proceed?” only when it could reasonably be another class. **Wait** for that answer before writing code.

3. **Open a change** unless trivial. Create `specs/changes/<slug>/`:
   - `proposal.yaml` — `kind`, `promise_ids`, `why`
   - `delta.yaml` — ADDED / MODIFIED / REMOVED
   - `success.yaml` — named sensors (`must:` lines are enough)
   - `decision.md` — only if a human must choose

   Do **not** edit live `capability.*.yaml` / `foundation.*.yaml` until promote. New capabilities with no live id: Phase 1 live file **or** ADDED in this folder; prefer a change folder if this request is an evolve of something that exists.

4. **Blast** the promise id and components you will touch. Tell the user “likely affected,” not hop-rule homework. Foundations are terminal.

5. **Interrupt sparingly.** Ask only unresolved consequential questions (prefer one). Record the answer in `decision.md`. **Wait** before implementing. Isolated UI nits are not interruptions; a global foundation/token used by many ids is.

6. **Implement** from the projection: live promise + delta + blast + decisions. Match capabilities, errors, events, and `success.yaml`. Keep bidirectional links if you touch `implements` / `uses` (on files in the change, or at promote).

7. **POST reconcile.** Run `validate` and `check_sync --change <slug> --changed-ids` for ids you touched (including realization files). Coverage pass is not behavior verified. Optionally `python3 tools/specplane/drift.py --scope changed` as a reminder. Do not pick spec vs code when they disagree — report it.

8. **Promote only after the user accepts.** Then: apply the delta to live YAML, bump `meta.version` + changelog on those live files, move the folder to `specs/changes/_archive/<slug>/`. Retrieve should then show one live graph.

If this repo has no `specs/`, say so and point at bootstrap. Do not copy SpecPlane’s own `specs/` into another app.
