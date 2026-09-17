# Use SpecPlane in your project

This repo is the schema **kit** plus (in this GitHub tree) SpecPlane’s own **kernel product** specs. Your product repo is where *your* `specs/` lives. Do **not** copy SpecPlane’s `specs/` into your app — that tree is SpecPlane specifying its CLI, not a template product.

There is no npm package or marketplace plugin yet — you copy a small set of kit files, then let the agent scaffold *your* specs.

## What you are installing

| In this repo | In your project | Why |
|---|---|---|
| `specplane/` | `specplane/` (same path) | Schema reference, applicable sections, foundation boilerplates |
| `AGENTS.md` | `AGENTS.md` (use the consuming template below) | Tells the agent what to load |
| `CLAUDE.md` | `CLAUDE.md` | Claude Code reads this; it should include `AGENTS.md` |
| `.agents/skills/specplane-*` | `.agents/skills/specplane-*` | Portable skills (Cursor, Claude, Codex) |
| `.cursor/skills/specplane-*` | `.cursor/skills/specplane-*` | Cursor discovery |
| `tools/specplane/` | `tools/specplane/` | Optional: kernel CLI (`cli.py`, `kernel.py`, `validate.py`, `drift.py`) for the agent to run locally |
| `tools/specplane/specplane.config.json.example` | `specplane.config.json` | Spec root and schema version |

Copy the `specplane/` directory, skills, and rules — **not** the whole SpecPlane git repo, and **not** this repo’s `specs/` folder. Pin the SpecPlane commit or tag you copied from (today: branch `main` / schema **v9.1.0**; kernel specs live on `kernel-first-slice` until merged).

## Setup (once)

From a clone of [SpecPlane](https://github.com/gauravbaruah/SpecPlane), in your product repo:

```bash
# Schema + foundations (required path: specplane/)
rsync -a --delete /path/to/SpecPlane/specplane/ ./specplane/

# Skills
mkdir -p .agents/skills .cursor/skills .cursor/rules
rsync -a /path/to/SpecPlane/.agents/skills/specplane-* .agents/skills/
rsync -a /path/to/SpecPlane/.cursor/skills/specplane-* .cursor/skills/
rsync -a /path/to/SpecPlane/.cursor/rules/specplane-*.mdc .cursor/rules/

# Toolkit (optional — agent/local only, not CI). Needed for retrieve/blast/check_sync.
mkdir -p tools/specplane
rsync -a /path/to/SpecPlane/tools/specplane/cli.py \
          /path/to/SpecPlane/tools/specplane/kernel.py \
          /path/to/SpecPlane/tools/specplane/validate.py \
          /path/to/SpecPlane/tools/specplane/drift.py \
          /path/to/SpecPlane/tools/specplane/README.md \
          /path/to/SpecPlane/tools/specplane/requirements.txt \
          tools/specplane/
cp /path/to/SpecPlane/tools/specplane/specplane.config.json.example specplane.config.json
# then, if you want the agent to run checks: pip install -r tools/specplane/requirements.txt

```

Add a consuming `AGENTS.md` (below) and:

```md
# CLAUDE.md
@AGENTS.md
```

Commit those files. Open the **product** repo in Cursor or Claude Code (not only the SpecPlane clone).

If you already have an `AGENTS.md`, keep your project rules and append the SpecPlane loading contract rather than replacing the file.

### Consuming `AGENTS.md`

```markdown
# SpecPlane (this product)

This project uses SpecPlane v9.1.0. Specs live in `specs/`. Schema files live in `specplane/`.

Do not ingest `specplane/core_prompt/specplane_schema_prompt_v9.1.0.md` into a coding session.

1. For spec work, open `specplane/core_prompt/applicable/README.md` and load only the section for the task.
2. Skills: specplane-bootstrap, specplane-author, specplane-implement, specplane-validate.
3. Product requests in natural language use **specplane-implement** (retrieve → change folder → blast → decide → code → check_sync). Do not slurp `specs/`.
4. Optional: if `tools/specplane/cli.py` is present, the agent runs it in-session. Do not add git hooks or CI jobs unless you choose to.

Rules:
- Filename without extension equals `meta.id`.
- Capability Phase 1 is valid without architecture.
- Bidirectional links in the same change (`implements` ↔ `realized_by`, `uses` ↔ `used_by`).
- Changelog on live 5C files when `meta.version` changes. In-flight work lives in `specs/changes/`.
- Specs before code when behavior, contracts, events, rollout, or security change. Trivial work: say “no spec impact” and skip the change folder.
```

## First session

Ask the agent:

> Set up SpecPlane for this repo. Use schema v9.1.0. Create a `specs/` tree and a Phase 1 capability for \<name\>.

That should trigger `specplane-bootstrap`, then `specplane-author`. You should get:

```
specs/
├── capabilities/capability.<name>.yaml
├── foundations/          # copies from specplane/foundations/ as needed
├── system.<product>.yaml
├── containers/
├── components/
└── changes/              # empty until a real evolve/fix/learn
```

Daily requests after that are product language, not more scaffolding. See [`golden-journey.md`](./golden-journey.md).

Do **not** paste the full master prompt into chat.

## Daily use

You speak product language. The agent should run the ritual in [`golden-journey.md`](./golden-journey.md). You should not type `retrieve` or `blast`.

| You say | Agent should |
|---|---|
| “Reminders should trigger from observations” (or any feature/bug/experiment) | `specplane-implement` → retrieve, propose trivial/fix/evolve/learn, open `specs/changes/` if consequential, blast, ask only consequential questions, implement, `check_sync` |
| Move that button 4px / typo / rename helper | Just do it. “No spec impact.” No change folder. |
| Add a capability / foundation / component (explicit spec work) | `specplane-author` → applicable sections 03 + 04–07. If the thing already exists and behavior is changing, switch to implement. |
| Review / validate specs | `specplane-validate` → `cli.py validate` / `check_sync`, then sections 08 and 11 |
| “Ship it” / accept the change | Promote delta into live YAML, archive the change folder |

Authoring order for a **new** tree: **capability Phase 1** → foundations you actually need → system/containers → components with `implements` / `uses`. After that, in-flight work belongs in `specs/changes/`.

## Updating SpecPlane

Re-copy `specplane/`, skills, and rules from a newer SpecPlane commit. Diff your consuming `AGENTS.md` if the loading contract changed. Do not merge `legacy/`, `specs/` (this repo’s kernel product), or private folders.

## Not included yet

- Marketplace plugin or installer (Cursor / Claude Code / Codex)
- Git hooks or CI/CD wiring for validate/drift in product repos
- A supported spec viewer (the Docusaurus tool under `legacy/` is archived)
- Copying this kit into an important product until a real session matches [`golden-journey.md`](./golden-journey.md)
