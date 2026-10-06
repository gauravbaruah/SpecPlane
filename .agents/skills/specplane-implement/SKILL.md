---
name: specplane-implement
description: Run the SpecPlane change ritual when the user describes a product change, bug, experiment, feature, install/docs that state a promise, or asks to implement. PRE: retrieve when a promise might move (if unsure, retrieve). On a miss, wait on interpretations before YAML, then on reuse before code. POST: check_sync --change, then run --change. Typos/renames skip retrieve. Do not use for bootstrap or YAML-only authoring.
---

# SpecPlane Implement

The user talks about the product. You run SpecPlane. They should not type `retrieve` or `blast`. Intended chat shape: [`docs/golden-journey.md`](../../../docs/golden-journey.md).

Do not slurp `specs/`. Call the kernel CLI. No SpecPlane API key. Do not add git hooks or CI. Do not slurp the tree. Do not parse source in the kernel.

## Hard gates (not optional)

Developers paste a prompt and expect codegen. You still run SpecPlane **when a product promise might move**. Do not skip because it looks like docs, packaging, README, “just implement,” or “no new capabilities.”

**PRE — if the request could reasonably move a promise** (behavior, contracts, events, security, rollout, how the product is obtained: init/install/README CLI claims):

1. Guess the capability (or component) id. Call `retrieve`. If none exists, say so. Classify **only after** that retrieve.

**Hit** — a live id matches (fix or evolve of that promise). One wait at most. A known-id fix does not get a second gate. A typo is not a wait.

- Open `specs/changes/<id>/` and `blast`. Draft the **delta on the existing promise** unless the human said this is new value.
- Do not recommend a parallel capability or component for the same job. Prefer reuse, extend, or compose of the ids `blast` named. Build last, and only when nothing already owns the job.
- Ask at most one unresolved consequential question. **Wait**, then implement.

**Miss** — no live capability matches. Do not open a change yet.

- **Intent gate — before any YAML.** Offer two or three interpretations and the likely flows. **Wait.** A narrower reading (“I only meant a PDF”) may mean no new capability. Do not author a new capability file until this gate has an answer, unless the human pasted a decided spec.
- Open the change folder. Draft Phase 1 / `delta.yaml` **from the chosen interpretation**, linking existing `implements` / `realized_by` / `uses` where the graph already has them. Use declared `realization.paths` already in hand. Do not invent a stack. Do not mint a component from a class name.
- `blast` and `impact`.
- **Realization gate — before code.** Classify reuse, extend, compose, or build (build last). Even **build** (a new component) lists connections, constraints, what blast named, and what not to duplicate. **Wait.** Then implement spec and code.

**PRE — skip retrieve** only when it cannot reasonably move a promise: typo, 4px, rename helper, same-behavior refactor. Say “no spec impact.” If unsure, retrieve — do not guess trivial.

Guide the spec so the reply can name, in substance:

- **Reuse** — mechanisms the graph already has.
- **Extend** — a flow or responsibility on an existing capability.
- **Compose** — existing ids joined, with no second stack.
- **Build** — only the piece nothing owns. Still list connections, constraints, and avoid.

A new noun can still be a hit. “Add team invitations” is extend/compose when retrieve already has membership, auth, or notifications — not a parallel capability plus a new mailer. “Users should be able to share a journey” is a miss until the human picks a reading (read-only link, grant a registered user, or collaboration). Infer stays the brownfield walk. If this is a product change, do not switch to authoring a new capability until the intent gate has an answer.

**POST — after a non-trivial implement, before claiming done:**

1. `validate`.
2. `check_sync --change <slug> --changed-ids` with every id you retrieved, blasted, or whose realization files you edited. `<slug>` is this request’s `specs/changes/<slug>/` folder. The default changed-set is spec YAML in git, plus component ids whose declared `implementation.realization.paths` match a changed file. `--changed-ids` is an explicit override. An empty default is not a pass if you touched app code or `tools/specplane/`. If a map exists, run `reconcile` or report missing and unmapped paths. Maps are optional: do not require one to implement, and do not copy inferred cites into `realization.paths`. A coverage pass is declared coverage, not behavioral agreement.
3. `run --change <slug>`. This invokes binds already on that change (`run.argv` or `run.unittest` / `test:`). It does not create tests, exec English `must:` lines, or certify that the implementation satisfies the spec. If this change already has a check, bind it (`run.unittest` or `run.argv`). Do not invent a test so SpecPlane has something to run. Do not parse `test_strategy`. Unbound `must:` is `not_run` on `run`, not a pass and not a certificate. Exit 0 when nothing failed or errored.
4. Do not silently pick spec vs code. Do not edit live 5C YAML until the user accepts (promote).

The kernel does not watch the chat. If you do not call retrieve/check_sync, SpecPlane is silent. Clarifying questions are the coding agent following this skill, not a SpecPlane daemon.

If `tools/specplane/cli.py` is missing, say so and stop implementing product behavior.

## Load

Read `specplane/core_prompt/applicable/README.md`. Nouns, verbs, and the loop: [`specplane/dialect.md`](../../../specplane/dialect.md). When writing code, load `06-system-container-component.md` for contracts. Load `08-validation-rules.md` only if live links/versions will change **at promote**.

Do not load the full master prompt.

## Kernel

Prefer `specplane` if it is on PATH, else `python3 tools/specplane/cli.py`.

```bash
python3 tools/specplane/cli.py retrieve <id> --spec-root specs
python3 tools/specplane/cli.py blast <id> --spec-root specs
python3 tools/specplane/cli.py impact <id> --spec-root specs
python3 tools/specplane/cli.py validate --spec-root specs
python3 tools/specplane/cli.py check_sync --spec-root specs --change <slug> --changed-ids id1,id2
python3 tools/specplane/cli.py reconcile --spec-root specs
python3 tools/specplane/cli.py run --spec-root specs --change <slug>
```

When you run the CLI, set `SPECPLANE_CALLER=cursor_skill`. That is the only signal that a skill invoked it. A local event is recorded unless the human has run `usage disable`. Nothing is uploaded. Do not put a path, a spec id, or a secret in `SPECPLANE_CALLER`, `SPECPLANE_RUN_ID`, or `SPECPLANE_SESSION_ID`.

If a command prints a line that starts with `SpecPlane ·`, quote that line in the reply the user sees, unchanged. If it does not, do not invent a SpecPlane receipt. Do not say SpecPlane caught a bug or revised the code unless that printed line says so.

During an open change, the implementation context is that change. Live text and the change stay labeled. Canonical synchronization stays pending until the user accepts. For the file you are editing, run `context <path>`. If it says the file is unmapped, leave it unmapped. Do not invent a component.

Do not invent a graph by reading the whole tree. You may open files the CLI already named.

## Procedure

1. **PRE.** If this could move a promise, guess the capability id and `retrieve` it (or say none exists). Paraphrase as a short human projection. Do not slurp the tree. Do not parse source in the kernel. If it cannot (typo / 4px / rename / same-behavior refactor), say “no spec impact” and do it — no retrieve. If unsure, retrieve.

2. **Propose a class** (do not quiz the user on taxonomy):
   - **trivial** — cannot reasonably move a promise (typo, 4px, rename helper, behavior-free refactor). Just do it. State “no spec impact.” Stop here.
   - **fix** — live spec already promises this; it is broken or incomplete.
   - **evolve** — the promise itself changes (including how the product is obtained: install, init, “what the README says the CLI does”).
   - **learn** — experiment; may not become live law.

   Ceremony follows **semantic consequence**, not diff size. One-line `danger` token change can be evolve. A large internal refactor can be trivial.

   If the class is obvious, state it and continue. Ask “proceed?” only when it could reasonably be another class. **Wait** for that answer before writing code.

3. **Intent gate when retrieve missed.** If no live capability matches, do not open a change yet. Offer two or three interpretations and the likely flows. **Wait.** A narrower reading may mean no new capability.

4. **Open a change** unless trivial, and unless that intent gate is still open. Create `specs/changes/<slug>/`:
   - `proposal.yaml` — `kind`, `promise_ids`, `why`
   - `delta.yaml` — ADDED / MODIFIED / REMOVED
   - `success.yaml` — named sensors (`must:` lines are enough). If this change already has a check, bind it (`run.unittest` or `run.argv`). Do not invent a test so SpecPlane has something to run. Do not parse `test_strategy`. Unbound `must:` is `not_run` on `run`, not a pass and not a certificate.
   - `decision.md` — only if a human must choose

   On a miss, draft from the chosen interpretation and from ids the graph already has (`implements` / `realized_by` / `uses`, declared `realization.paths`). Do not invent a stack. On a hit, draft the delta on the existing promise. Do not add a parallel capability or component for the same job. Do **not** edit live `capability.*.yaml` / `foundation.*.yaml` until promote. New capabilities with no live id: Phase 1 live file **or** ADDED in this folder; prefer a change folder if this request is an evolve of something that exists. Do not mint a component from a class name.

5. **Blast** the promise id and components you will touch. On a miss, also run `impact`. Tell the user “likely affected,” not hop-rule homework. Foundations are terminal.

6. **Realization, then wait.**
   - Miss: classify reuse, extend, compose, or build (build last). Even a new component lists connections, constraints, what blast named, and what not to duplicate. **Wait** before code.
   - Hit: prefer reuse, extend, or compose of the ids blast named. Ask only one unresolved consequential question. **Wait** once. A known-id fix does not get a second gate.
   - Isolated UI nits are not interruptions; a global foundation/token used by many ids is. Record the answer in `decision.md`.

7. **Implement** from the projection: live promise + delta + blast + decisions. Match capabilities, errors, events, and `success.yaml`. If the work needs a check, add **the product’s** check and bind it (`run.unittest` or `run.argv`). If this change already has a check, bind it (`run.unittest` or `run.argv`). English `must:` is enough when there is no check yet. Do not invent a test so SpecPlane has something to run. Do not parse `test_strategy`. Keep bidirectional links if you touch `implements` / `uses` (on files in the change, or at promote).

8. **POST reconcile.** Run `validate`, `check_sync --change <slug> --changed-ids` for ids you touched (including realization files), then `run --change <slug>`. If this change already has a check, bind it (`run.unittest` or `run.argv`). Do not invent a test so SpecPlane has something to run. Do not parse `test_strategy`. Unbound `must:` is `not_run` on `run`, not a pass and not a certificate. When a component already declares `realization.paths`, also run `reconcile` or report missing / unmapped_changed. Maps are optional. Do not invent one by copying inferred cites. Coverage pass is declared coverage, not behavioral agreement. A `run` pass means bound checks exited 0, not that the implementation satisfies the spec. Optionally `python3 tools/specplane/drift.py --scope changed` as a coarse reminder; `reconcile` is the declared-path check. Do not pick spec vs code when they disagree — report it.

9. **Promote only after the user accepts.** Run `specplane promote <slug>`: apply the delta to live YAML, bump `meta.version` + changelog on those live files, move the folder to `specs/changes/_archive/<slug>/`. Retrieve should then show one live graph. Do not `git mv` by hand unless the command is missing.

If this repo has no `specs/`, say so and point at bootstrap. Do not copy SpecPlane’s own `specs/` into another app.

## Impact perspectives

`impact <id>` is one affected subgraph plus projections (system, product, quality, governance, ownership). `blast` stays the bucket tree that `check_sync` uses. Do not invent stakeholder views (`qa_view`, `security_view`, and the like) or ask a model to re-decide blast. Agents may propose missing spec relationships as inferred; they are not the impact engine. Absence of a governed concern or owner is "not represented", never "no security impact" or "no QA required". See [`docs/impact-perspectives.md`](../../../docs/impact-perspectives.md).
