# Golden journey — agent ritual

This is what a SpecPlane-aware coding agent should do when someone describes a product change in plain language.

**Intended experience:** you talk about the product. The coding agent uses SpecPlane. You never type `retrieve` or `blast`. You answer only consequential decisions. Agents implement. SpecPlane reconciles.

The transcript below is a **scripted example** (a reminders capability). Kernel commands in asides are what the agent runs, not what you type.

---

## Protocol (what the skill must do)

**PRE** when a promise might move. **POST** before you say you are done. The human pasted a prompt; you still run SpecPlane. The kernel does not watch the chat — Codex/Cursor must call it.

1. Hear a natural-language request. Do **not** ask the human which CLI command to run.
2. If this could move a promise: find the live capability (or say none exists). Call `retrieve` **before** code or docs that state that promise. Typos/renames skip retrieve. If unsure, retrieve.
3. Propose a class. Do not make the human memorize these words:
   - **trivial** — cannot reasonably move a promise (typo, 4px, rename helper, behavior-free refactor). Just do it. Say “no spec impact.”
   - **fix** — live spec already promises this; it is broken or incomplete.
   - **evolve** — the promise itself changes (including install / init / what the README says the CLI does).
   - **learn** — experiment; we do not know yet whether this becomes law.
4. Ceremony scales with **semantic consequence**, not diff size. A one-line token change can be evolve. A 2,000-line refactor can be trivial.
5. If not trivial: open `specs/changes/<id>/` (`proposal.yaml`, `delta.yaml`, `success.yaml`; `decision.md` only if a human must choose). Do **not** turn the live capability into a changelog novel.
6. Call `blast`. Translate to “likely affected.”
7. Ask **only** unresolved consequential questions (prefer one). Record the answer in `decision.md`. Wait.
8. Give the coding agent a **minimal projection** (live promise + delta + blast + decision). Implement. Add tests that match `success.yaml`.
9. **POST:** `validate` + `check_sync --change <slug> --changed-ids` on the ids you touched (and whose realization files you edited). The default changed-set is spec YAML only — do not treat an empty default as a pass. Coverage pass is declared coverage, not behavioral agreement. Do not silently pick spec vs code.
10. **Promote** into live YAML only after the human accepts. Archive the change folder.

You never need a SpecPlane API key. The coding agent already in the editor is the intelligence. The kernel is deterministic.

---

## The request

**User:** Reminders should be triggerable from observations, not just fixed times.

Moderately consequential, not a redesign of the product. Existing promise is `capability.adaptive_reminders` in this example.

---

## Transcript

### 1. Understand

**Agent:** This looks like the existing capability **adaptive reminders** — users get reminders tied to a reference time, delivered as push notifications. You want observations to be able to trigger them as well. That changes the live promise, not just plumbing.

I’ll retrieve current intent and compute blast before touching code.

<aside>

```bash
python3 tools/specplane/cli.py retrieve capability.adaptive_reminders --spec-root specs
```

</aside>

### 2. Retrieve — human projection (not YAML)

**Agent:** Live promise today:

- Reminders fire from a **fixed schedule** relative to a reference time
- Reference-time semantics are already specified
- Delivery is push notification
- Success is “reminder received near the intended moment,” not “reacted to a new observation”

No open change folder on this id.

### 3. Classify

**Agent:** This appears to be an **evolve** — the product should do something it does not promise today. Proceed, and I’ll open a change against `capability.adaptive_reminders`?

**User:** Yes.

### 4. Create the delta (agent does this)

<aside>

Creates `specs/changes/observation_triggered_reminders/`:

- `proposal.yaml` — kind `evolve`, promise_ids include `capability.adaptive_reminders` plus any components already known
- `delta.yaml` — MODIFIED: scheduled-only → scheduled **or** observation-triggered
- `success.yaml` — named sensors (e.g. observation event → reminder intent; late-observation rule once decided)
- no `decision.md` yet

Does **not** edit `specs/capabilities/capability.adaptive_reminders.yaml` yet.

</aside>

**Agent:** Opened `change.observation_triggered_reminders` (evolve). In-flight work lives there so the live capability stays the current promise.

### 5. Blast

<aside>

```bash
python3 tools/specplane/cli.py blast capability.adaptive_reminders --spec-root specs
python3 tools/specplane/cli.py blast component.reminder_scheduler --spec-root specs
```

</aside>

**Agent:** Likely affected:

- reminder scheduler
- observation pipeline
- notification service
- reminder configuration UX

Foundations listed (not exploded): notification / event conventions.

### 6. One consequential question

**Agent:** One product decision before implementation:

If an observation arrives **late** (after the window that would still be useful), should it still trigger a reminder?

- **[A]** Yes — always fire
- **[B]** No — drop it
- **[C]** Only within a configurable window

Everything else can follow from the live spec + this delta.

**User:** C.

### 7. Record the decision

<aside>

Writes `decision.md`: late observations fire only inside a configurable window; outside the window, drop and count a miss. Not a silent default.

</aside>

**Agent:** Recorded: late observations trigger only inside a configurable window. That’s enough to implement.

### 8. Coding context (minimal projection)

**Agent:** Implementation context:

| | |
|---|---|
| Live | scheduled reminders, reference time, push delivery |
| Delta | observations may trigger; window policy = C |
| Blast | scheduler, observation pipeline, notifications, settings UX |
| Success | observation-in-window → reminder intent; observation-out-of-window → no send + miss metric |
| Do not | invent a new capability; do not “fix” unrelated reminder copy; do not expand blast through every `used_by` on a foundation |

Proceeding to code.

### 9. Implement

The coding agent implements against that projection. The user does not paste YAML. The user does not classify files as capability vs component.

### 10. Verify

Tests (or the sensors in `success.yaml`) cover:

- observation inside window → reminder
- observation outside window → no reminder
- existing fixed-time reminders still fire

### 11. Reconcile

<aside>

```bash
python3 tools/specplane/cli.py validate --spec-root specs
python3 tools/specplane/cli.py check_sync --spec-root specs \
  --change observation_triggered_reminders \
  --changed-ids capability.adaptive_reminders,component.reminder_scheduler,component.observation_pipeline
```

</aside>

**Agent:** Coverage is declared on this change — SpecPlane did not verify behavior. Structural validate passed. Ready to promote when you say this is the new live promise.

### 12. Promote

**User:** Ship it.

**Agent:** Promoted the delta into live `capability.adaptive_reminders` (version bump + changelog). Archived `specs/changes/observation_triggered_reminders/`. Retrieve now shows one live graph, no leftover “scheduled-only” promise.

---

## Counter-examples (must stay boring)

| User says | Agent does |
|---|---|
| Move that button 4px down | Just do it. No change folder. “No spec impact.” |
| Fix this typo | Just do it. |
| Rename this internal helper | Just do it. |
| Refactor this class; same behavior | Just do it. If unsure whether behavior moved, retrieve — do not guess trivial. |
| Password reset is broken | **fix** — live spec already promises reset. Thin change folder if the path is non-trivial; then implement. No new promise. |
| Reset links expire in 15 minutes, not 60 | **evolve** — same shape as the journey above. |
| Try an AI-generated recovery flow and see if completion rises | **learn** — hypothesis + success sensor; may not promote to live. |
| Make destructive actions green instead of red | Retrieve `foundation.design_system`. If `danger = red` is used broadly: **interrupt** — this instance only, or the global token? That one-line CSS can be evolve. |

---

## What this journey is not

- A SpecPlane-hosted agent or API key
- SpecPlane watching the chat or tapping Codex — leftover/uncovered ids surface only if the agent calls retrieve / blast / list_gaps / check_sync. Clarifying questions are the agent following the skill
- A GitHub App, viewer, or a separate coach product
- You becoming a YAML clerk
- A new 5C type or kernel command

## Try it on tiny-saas

Five-minute path: [`try.md`](./try.md) and [`examples/tiny-saas`](../examples/tiny-saas/). Sentence that matches the live fixture:

> Reset links should expire in 15 minutes instead of 60.

Open `examples/tiny-saas` as the workspace (not this repo’s kernel `specs/`). Kernel goldens (`tools/specplane/testdata/golden/messy_auth/`) still prove CLI stdout. **This** file is the human+agent loop.
