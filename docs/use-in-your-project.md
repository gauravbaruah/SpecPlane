# Use SpecPlane in your project

If you have not tried the kernel yet, start with [`try.md`](./try.md) (`examples/tiny-saas`, reset links 60 → 15).

This page puts the **kit** into *your* product repo. Your `specs/` is your overlay. Do **not** copy SpecPlane’s `specs/` into your app — that tree is SpecPlane specifying its CLI, not a template product.

## Setup (once)

In the **product** repo (must not be the SpecPlane kit root):

```bash
pip install specplane
# or: uv tool install specplane
specplane init
# optional: --kit-only   skip tools/specplane
#           --force      replace dest/specplane
#           --dest PATH  if you are not already in the product repo
```

The current release is the pre-release `0.1.0a1`. Python 3.10 or newer. There is no `npx` package. To pin a commit: `uvx --from git+https://github.com/gauravbaruah/SpecPlane.git@main specplane init`.

Fallback from a checkout (Python 3.10+ and PyYAML):

```bash
pip install -e /path/to/SpecPlane    # or: pip install pyyaml
python3 /path/to/SpecPlane/tools/specplane/cli.py init
```

That copies `specplane/`, skills, rules, and the CLI; writes or appends `AGENTS.md`; creates empty `specs/` folders (`capabilities`, `foundations`, `containers`, `components`, `changes`). It does **not** copy this repo’s kernel `specs/`, does not add an example capability, and does not write GitHub Actions. It does not ask which coding agent you use — skills for Cursor, Claude Code, and Codex are copied together.

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

Copy the `specplane/` directory, skills, and rules — **not** the whole SpecPlane git repo, and **not** this repo’s `specs/` folder. Pin the SpecPlane commit you copied from (schema **v9.1.0**; default branch `main`).

Prefer `specplane init`. Manual rsync is the fallback:

```bash
# Schema + foundations (required path: specplane/)
rsync -a --delete /path/to/SpecPlane/specplane/ ./specplane/

# Skills
mkdir -p .agents/skills .cursor/skills .cursor/rules
rsync -a /path/to/SpecPlane/.agents/skills/specplane-* .agents/skills/
rsync -a /path/to/SpecPlane/.cursor/skills/specplane-* .cursor/skills/
rsync -a /path/to/SpecPlane/.cursor/rules/specplane-*.mdc .cursor/rules/

# Toolkit (optional). Needed for retrieve/blast/check_sync. Init does not copy a workflow.
mkdir -p tools/specplane
rsync -a /path/to/SpecPlane/tools/specplane/cli.py \
          /path/to/SpecPlane/tools/specplane/kernel.py \
          /path/to/SpecPlane/tools/specplane/impact.py \
          /path/to/SpecPlane/tools/specplane/validate.py \
          /path/to/SpecPlane/tools/specplane/drift.py \
          /path/to/SpecPlane/tools/specplane/initkit.py \
          /path/to/SpecPlane/tools/specplane/mcp_stdio.py \
          /path/to/SpecPlane/tools/specplane/ci_gate.py \
          /path/to/SpecPlane/tools/specplane/view.py \
          /path/to/SpecPlane/tools/specplane/README.md \
          /path/to/SpecPlane/tools/specplane/requirements.txt \
          tools/specplane/
rsync -a /path/to/SpecPlane/tools/specplane/viewer/ tools/specplane/viewer/
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

### Optional local MCP

Skills already call the kernel. To expose retrieve, blast, impact, check_sync, list_gaps, and run as tools, start the same server with `specplane mcp`. Validate, promote, and reconcile stay CLI-only.

**Cursor** (`~/.cursor/mcp.json`) or **Claude Desktop** (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "specplane": {
      "command": "specplane",
      "args": ["mcp"]
    }
  }
}
```

**Claude Code** — same JSON in the project `.mcp.json`, or `claude mcp add specplane -- specplane mcp`.

If `specplane` is not on PATH, point `command` at `python3` and `args` at that repo’s `tools/specplane/mcp_stdio.py`. That `python3` must be able to import PyYAML (`pip install pyyaml` or `pip install -e /path/to/SpecPlane`).

### Optional CI

Paste [`docs/ci.md`](./ci.md) if a pull request should ask whether a change is accounted for by declared intent and bound evidence. Init copies `ci_gate.py`. Init does not write that workflow. It is not a required GitHub check unless you turn branch protection on yourself. `check_sync` still does not execute sensors. A coverage pass is declared coverage, not behavioral agreement.

### Consuming `AGENTS.md`

```markdown
# SpecPlane (this product)

This project uses SpecPlane v9.1.0. Specs live in `specs/`. Schema files live in `specplane/`.

Do not ingest `specplane/core_prompt/specplane_schema_prompt_v9.1.0.md` into a coding session.

Nouns, verbs, and the loop are in `specplane/dialect.md`.

1. For spec work, open `specplane/core_prompt/applicable/README.md` and load only the section for the task.
2. Skills: specplane-bootstrap, specplane-author, specplane-flows, specplane-implement, specplane-validate, specplane-infer, specplane-explain.
3. Product requests in natural language use **specplane-implement**. PRE: retrieve when a promise might move (if unsure, retrieve). POST: check_sync --change <slug> --changed-ids, then run --change <slug>. If this change already has a check, bind it (`run.unittest` or `run.argv`). Do not invent a test so SpecPlane has something to run. Do not parse `test_strategy`. Unbound `must:` is `not_run` on `run`, not a pass and not a certificate. `run` invokes bound checks only; it does not create tests or certify behavior. Typos skip retrieve. Do not slurp `specs/`.
4. Optional: if `tools/specplane/cli.py` is present, the agent runs it in-session. Do not add git hooks or CI jobs unless you choose to.

Rules:
- Filename without extension equals `meta.id`.
- Capability Phase 1 is valid without architecture.
- Bidirectional links in the same change (`implements` ↔ `realized_by`, `uses` ↔ `used_by`).
- Changelog on live 5C files when `meta.version` changes. In-flight work lives in `specs/changes/`.
- Brownfield (an existing repo): use specplane-infer. The coding agent walks one named root and writes Phase 1 YAML tagged inferred. Greenfield stays specplane-bootstrap. There is no scan CLI and no infer CLI. `promote --ids` makes named inferred ids live. Greenfield can declare `implementation.realization.paths` without infer. `reconcile` checks that join; it does not write code or parse source. It is CLI-only.
- Specs before code when behavior, contracts, events, rollout, security, or how the product is obtained change. Trivial work (typo/4px/rename): no retrieve. If unsure, retrieve.
```

## First session

After `init`, empty `specs/` folders already exist. Ask the agent:

> Use schema v9.1.0. Add a Phase 1 capability for \<name\> and a system spec.

That should trigger `specplane-bootstrap` / `specplane-author`. You should get:

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
| “Reminders should trigger from observations” (or any feature/bug/experiment) | PRE retrieve → classify → change folder if not trivial → blast → implement → POST `check_sync --change <slug> --changed-ids`, then `run --change <slug>` |
| Move that button 4px / typo / rename helper | No retrieve. Just do it. “No spec impact.” |
| Add a capability / foundation / component (explicit spec work) | `specplane-author` → applicable sections 03 + 04–07. If the thing already exists and behavior is changing, switch to implement. |
| Review / validate specs | `specplane-validate` → `cli.py validate` / `check_sync`, then sections 08 and 11 |
| “Ship it” / accept the change | Promote delta into live YAML, archive the change folder |

Authoring order for a **new** tree: **capability Phase 1** → foundations you actually need → system/containers → components with `implements` / `uses`. After that, in-flight work belongs in `specs/changes/`. Index of nouns, verbs, and the loop: [`specplane/dialect.md`](../specplane/dialect.md).

## Updating SpecPlane

Re-copy `specplane/`, skills, and rules from a newer SpecPlane commit. Diff your consuming `AGENTS.md` if the loading contract changed. Do not merge `legacy/`, `specs/` (this repo’s kernel product), or private folders.

## Not included yet

- An `npx` package (`pip install specplane` and `uv tool install specplane` are the obtaining commands)
- An init wizard that picks Cursor vs Claude vs Codex (all three get the same skills)
- Copying this kit into an important product until a real session matches [`golden-journey.md`](./golden-journey.md)
