# SpecPlane Core

Master schema, applicable split, and foundation boilerplates.

**Default schema: v9.1.0.** Use v6.1.0 only when you want C4 without capability or foundation layers.

## Reference vs applicable

| | File | When to use |
|---|---|---|
| **Reference** | [`core_prompt/specplane_schema_prompt_v9.1.0.md`](core_prompt/specplane_schema_prompt_v9.1.0.md) | Complete prompt in one file. Humans browsing. Schema changes. Do **not** dump into an agent session. |
| **Applicable** | [`core_prompt/applicable/README.md`](core_prompt/applicable/README.md) | Split of the same prompt. Agents load **one section per task**. |

v6.1.0 (C4 only): [`core_prompt/specplane_schema_prompt_v6.1.0_progressive_disclosure.md`](core_prompt/specplane_schema_prompt_v6.1.0_progressive_disclosure.md) — [`README_v6.1.0.md`](core_prompt/README_v6.1.0.md)

Older versions live in [`core_prompt/archived/`](core_prompt/archived/). v5.5.1 and v7 are **not** current.

## Agent files

Repo root [`AGENTS.md`](../AGENTS.md) is the router. [`CLAUDE.md`](../CLAUDE.md) includes it. Skills in `.agents/skills/` (mirrored under `.cursor/skills/`) tell the agent which applicable section to open.

## Foundations

[`foundations/`](foundations/) — 19 boilerplate specs (design system, API conventions, security, AI guidelines, and others). Copy into a project's `specs/foundations/` and fill in.

## Supporting prompts

- [`supporting_prompts/spec_validation_prompt_examples.md`](supporting_prompts/spec_validation_prompt_examples.md)
- [`supporting_prompts/widget_spec_examples.md`](supporting_prompts/widget_spec_examples.md)
- [`supporting_prompts/when_making_changes.md`](supporting_prompts/when_making_changes.md) — spec first, then code

## How to author

**In a product repo:** follow [Use SpecPlane in your project](../docs/use-in-your-project.md), then ask the agent to bootstrap `specs/`.

**In this schema repo:**

1. Open [`AGENTS.md`](../AGENTS.md) or [`core_prompt/README_START_HERE.md`](core_prompt/README_START_HERE.md).
2. Follow the applicable loading contract — do not attach the full v9.1.0 file.
3. Capability-first: Phase 1 (`responsibilities`, `flows`, `business_value`, `constraints`) is enough to start.

Specs capture **what** and **how well**, not **how**. Same spec can guide web, mobile, and API implementations.

### Spec types

| Spec | Owner | Question |
|---|---|---|
| Capability | PM | Why does this exist? |
| Foundation | Cross-cutting | What rules apply everywhere? |
| System / Container | Architecture | Where does this run? |
| Component | Engineering | What does it do and how well? |

## Quality

A good spec has a one-sentence purpose, measurable acceptance criteria, named failure modes, realistic constraints, and language-agnostic contracts. Components `implements` capabilities and `uses` foundations; keep the reverse links in the same change.
