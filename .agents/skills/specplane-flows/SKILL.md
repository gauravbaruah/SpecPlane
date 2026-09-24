---
name: specplane-flows
description: >-
  Enhance SpecPlane capability flows with optional journey, object-lifecycle,
  and information-flow richness. Use when the user asks to review, complete,
  or improve user journeys, UX/info flows, object lifecycles, malloc-use-free
  completeness, or what is missing on a flow. Do not invent unanswered behavior.
---

# SpecPlane Flows

Review and enrich `capability.flows`. Do not add a sixth C. Do not require every file to have journey + lifecycle + information.

## Load

1. `specplane/core_prompt/applicable/README.md`
2. `specplane/core_prompt/applicable/04-capability.md` (flow mapping + `open_questions`)
3. If a component realization is in scope: `06-system-container-component.md` (`planning.user_flows` stays a sliver)

Do not load the full master prompt.

## PRE

If `tools/specplane/cli.py` exists and you have a capability id:

```bash
python3 tools/specplane/cli.py retrieve <id> --spec-root specs
```

Do not slurp `specs/`. Open only files the CLI named.

## What to do

1. **Keep the string index.** Existing `flows: ["Sign-up", "Login"]` stays valid. Promote a string to a mapping only when this file needs the richness.
2. **Ask which kinds this file needs** (not all three by default):
   - **journey** — where the person starts, paths, how it ends
   - **lifecycle** — `malloc → use → free` for objects this flow creates
   - **information** — collected, moved, retained, destroyed
3. **Walk the implied envelope.** For each object: create → use → modify → share → archive? → restore? → delete? → what remains? For each journey: entry, stages, success, abandonment, exceptions, recovery.
4. **Do not invent answers.** If terminate/recover/ownership/retention is unspecified, write an `open_questions` item (`question`, optional `id` / `raised_from` / `status: open`). Capability-level `open_questions` or component `validation.open_questions` — same slot family; do not add a second key.
5. **Stories are a lens.** One or two `stories:` rows as evidence is fine. Do not generate a Jira-sized `user_stories` list.
6. **Cross-capability journeys are composed.** Do not copy a Discover→Cancel saga into every capability. Record the piece this file owns; note other capability ids in `open_questions` or `raised_from` if a hop is missing.
7. **External guidance is optional.** Web/UX research may be labeled `External guidance` and become questions or suggested spec edits. It is not law. Do not stuff best-practice essays into YAML.
8. **Components realize pieces.** You may set `planning.user_flows.flow_ref`. Do not copy lifecycle tables onto the component.

## Write rules

- In-flight work goes in `specs/changes/<slug>/` when this is an evolve of a live capability. New Phase 1 capabilities may take mappings on the live file.
- Prefer inference → questions → (after a human answers) spec mutation. Resolved questions graduate into the mapping (`lifecycle`, `recovery`, …) and get `status: resolved`.
- After edits: `python3 tools/specplane/cli.py validate --spec-root specs` when the CLI exists.

## Done when

The file is more digestible (named pieces + only the kinds it needs), gaps are **questions** not invented requirements, and a string-only neighbor file was left string-only.
