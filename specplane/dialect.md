# SpecPlane dialect

How little YAML is enough. Specs say **what** and **how well**, not **how**.

You speak product language. The agent runs retrieve / blast / check_sync / run. You do not type those.

## Nouns

| Word | What it is | Enough |
|---|---|---|
| **Capability** | Value: what the product promises, and how well | Phase 1: `responsibilities`, named `flows`, `business_value`, `constraints`. Five questions: purpose, contract, failure, constraint, success. |
| **Constraint** | A limit on that value | A field on the capability, or a **foundation** if it applies everywhere. Not a sixth C. |
| **Foundation** | Shared rule (design, errors, security) | Copy a boilerplate from `specplane/foundations/` when you actually need it. Do not staff every foundation on day 1. |
| **System / container / component** | Where it runs (C4) | After Phase 1, when a slice has a home. Keep `implements` ↔ `realized_by` in the same change. |
| **Change** | In-flight promise | `learn` / `fix` / `evolve` under `specs/changes/<slug>/`. Live YAML stays small. `must:` is the claim. |
| **Bind** | Claim → a check you already own | `run.unittest` or `run.argv` on that change. SpecPlane is not the test runner. Do not invent a test so SpecPlane has something to run. |

Code is realization (C4 level 4), not a fifth C.

## Order

1. One capability, Phase 1. Architecture can wait.
2. Foundations you actually need.
3. System / containers / components when the slice has a home.
4. After that, daily work is a **change**, not a novel on the live file.

## Too much

- Filling every schema field
- Journeys / lifecycles until the flow *is* the question
- AI-native component types until you have an agent to specify
- Treating `test_strategy` as a command SpecPlane will run
- A second handbook named Best Practices

Schema reference when you are authoring a type: `specplane/core_prompt/applicable/README.md` (load only that type). Change ritual: `docs/golden-journey.md`.
