# SpecPlane dialect

How little YAML is enough. Specs say **what** and **how well**, not **how**.

This page is the index: the nouns, the verbs, and how they join. You speak product language. The agent runs the verbs. You decide, and you say when a change becomes the live promise. You do not type `retrieve` or `blast`.

## Nouns

| Word | What it is | Enough |
|---|---|---|
| **Capability** | Value: what the product promises, and how well | Phase 1: `responsibilities`, named `flows`, `business_value`, `constraints`. Five questions: purpose, contract, failure, constraint, success. |
| **Constraint** | A limit on that value | A field on the capability, or a **foundation** if it applies everywhere. Not a sixth C. |
| **Foundation** | Shared rule (design, errors, security) | Copy a boilerplate from `specplane/foundations/` when you actually need it. Do not staff every foundation on day 1. |
| **System / container / component** | Where it runs (C4) | After Phase 1, when a slice has a home. Keep `implements` ↔ `realized_by` in the same change. |
| **Change** | The in-flight promise | A folder `specs/changes/<slug>/` with kind `learn`, `fix`, or `evolve`. The live file stays the current promise until you promote. |
| **Bind** | Claim → a check you already own | `run.unittest` or `run.argv` on that change. SpecPlane is not the test runner. Do not invent a test so SpecPlane has something to run. |

Code is realization (C4 level 4), not a fifth C.

## Verbs

| Verb | Who | What it does |
|---|---|---|
| **init** | You, once | Copy the kit into a product repo and create empty `specs/` folders. |
| **retrieve** | Agent | Read one live promise before writing. |
| **blast** | Agent | Say what else that promise touches. Foundations stop the walk. |
| **validate** | Agent | Check YAML shape, links, and changelog. |
| **check_sync** | Agent | Check that this change names the ids that moved. A pass is declared coverage, not proof the product behaves. |
| **run** | Agent | Invoke a check already bound on this change. English `must:` is not executed. |
| **promote** | Agent, after you say ship it | Write that change into the live spec and archive the folder (`promote <slug>`). Until you say ship it, the live file is unchanged. |
| **accept** | Agent, after you name inferred ids | Drop `inferred` on those ids (`accept --ids`). Not the change packet. |

A SpecPlane change is complete when its canonical specifications have been updated, its change packet has been archived, and the resulting repository state passes validation. Completion occurs before merge; merge publishes that completed state.

## Workflows

### Start a tree

1. **init**.
2. One **capability**, Phase 1. Architecture can wait.
3. **Foundations** you actually need.
4. **System / containers / components** when the slice has a home.
5. After that, daily work is a **change**, not a novel on the live file.

### Change the product

1. You say what should be true.
2. The agent **retrieves** the capability, or says none exists.
3. If none exists, the agent offers two or three interpretations and the likely flows. It waits. It does not open a change yet. A narrower reading may mean no new capability.
4. The agent opens a **change** from that choice, or from the live promise when retrieve hit. It drafts from ids the graph already has. It does not edit the live file. On a hit it does not add a parallel capability or component for the same job.
5. The agent **blasts**. It classifies the realization as reuse, extend, compose, or build (build last). Even a new component lists connections, constraints, and what not to duplicate. On a miss it waits again before code. On a hit it asks only when a real decision is open, and it waits once.
6. The agent implements. If a check already exists, **bind** it. Do not invent a test so SpecPlane has something to run.
7. The agent runs **validate**, **check_sync**, then **run**. Unbound `must:` is `not_run`, not a pass and not a certificate.
8. You say whether this is the new live promise.
9. Only then does the agent **promote** (`specplane promote <slug>`). Retrieve shows one graph. The PR that merges is already that completed state.

### Leave it alone

A typo, a few pixels, a rename, or the same behavior: no change folder, no retrieve, no promote.

## Too much

- Filling every schema field
- Journeys / lifecycles until the flow *is* the question
- AI-native component types until you have an agent to specify
- Treating `test_strategy` as a command SpecPlane will run
- A second handbook named Best Practices

Schema reference when you are authoring a type: `specplane/core_prompt/applicable/README.md` (load only that type). The long form of “Change the product” is `docs/golden-journey.md`.
