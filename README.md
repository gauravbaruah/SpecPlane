# SpecPlane

**Keep coding agents aligned with what you actually meant to build.**

SpecPlane is a git-native specification graph for software built by humans and AI agents.

Coding agents can change software extraordinarily quickly, but intent, architecture, constraints, tests, ownership, and evidence live in different places. SpecPlane keeps those relationships explicit and lets agents retrieve only the context relevant to a change.

Product intent, architecture, implementation, quality, governance, ownership, and evidence stay connected in one graph. Humans and agents work through the projections they need.

**Free now:** kit, local kernel, skills, optional MCP. No SpecPlane API key.

**In development:** local read-only viewer for exploring SpecPlane projections.

**Later:** hosted collaboration and review surfaces, a required GitHub check, and a spec coach.

<img src="./SpecPlane_Logo.png" alt="SpecPlane" width="160">

## The loop

You speak product language. The agent uses SpecPlane. You answer only consequential decisions.

You tell your coding agent:

> Reset links should expire in 15 minutes instead of 60.

SpecPlane **retrieves** the current promise, **classifies** this as an evolve (the live promise is 60 minutes), **blasts** what else is tied to that id, asks **one question** only if a decision is unresolved, and gives the agent the minimum context to **implement**. **Impact** reads that same subgraph as system, product, quality, governance, or ownership. Then **check_sync** — did the change stay aligned with the declared promise? If a success sensor already binds a check, **run** invokes that check and prints the evidence beside the claim. It does not certify the implementation.

You do not operate the CLI. The coding agent does.

**Ask** — you speak product language.

![Ask: reset links 60 to 15, retrieve, classify evolve](./docs/ask.gif)

**Impact** — blast names who else is tied to that id. The same subgraph can be read as system, product, quality, governance, or ownership.

![Impact: blast component.password_reset](./docs/impact.gif)

**Ship** — implement, then check_sync.

![Ship: check_sync pass](./docs/ship.gif)

### SpecPlane should stay out of your way

| You ask | What happens |
|---|---|
| “Fix the typo” | Agent just fixes it |
| “Rename this helper” | Agent just does it |
| “Reset links expire in 15m, not 60m” | SpecPlane tracks the product change |
| “Make destructive actions green” | SpecPlane warns if this changes a shared design rule |
| “Map what’s already in this repo” | The agent uses **specplane-infer**, writes a handful of inferred capabilities, and waits for you to name which ids to promote |

Ceremony scales with **semantic consequence**, not diff size. Full transcript: [`docs/golden-journey.md`](./docs/golden-journey.md).

**Works with your coding agent.** Cursor, Claude Code, and Codex use the same deterministic kernel through **skills** today. Local MCP exposes retrieve, blast, impact, check_sync, list_gaps, and run when you want tool-native calls. You are not meant to type those commands.

## Try it

Synthetic example — not a real product, not this repo’s kernel `specs/`.

```bash
git clone https://github.com/gauravbaruah/SpecPlane.git
```

Open **`examples/tiny-saas`** as the workspace. Ask Cursor:

> Reset links should expire in 15 minutes instead of 60.

Auth, billing, notifications, one open billing change, and `src/auth.py` with a 60-minute reset TTL. Details: [`examples/tiny-saas/README.md`](./examples/tiny-saas/README.md) and [`docs/try.md`](./docs/try.md).

`blast` of a single id (not the whole loop): [docs/blast.gif](./docs/blast.gif).

## Use it in your product

From **your** app repo (not onto SpecPlane itself):

```bash
uvx --from git+https://github.com/gauravbaruah/SpecPlane.git@main specplane init
```

That command copies the kit and creates empty `specs/` folders. It does not copy SpecPlane’s own kernel `specs/`. Pin `@main` (or a commit SHA). There is no PyPI / `npx specplane` package.

If `uvx` is not installed: `python3 /path/to/SpecPlane/tools/specplane/cli.py init` from a checkout.

Then ask for a Phase 1 capability. Schema **v9.1.0**. More: [`docs/use-in-your-project.md`](./docs/use-in-your-project.md).

Already have a repo? Ask the agent to map what is here. That uses the **specplane-infer** skill: the agent walks one named root and writes at most seven Phase 1 capabilities tagged `inferred`, with path cites. You name which ids become live. The agent then runs `promote --ids`. SpecPlane does not ship a scan command. The coding agent does the walk.

Already know which files realize a component? Declare them as `implementation.realization.paths` (a repo-relative file, or a directory prefix ending in `/`). Maps are optional. Greenfield can declare maps without infer. `reconcile` reports a missing declared path and an unmapped changed app file. SpecPlane does not write your code, does not parse source to learn values, and does not turn an infer cite into a map. When a mapped file changes, `check_sync`'s default changed-set can include that component id. `--changed-ids` still overrides. A coverage pass is still declared coverage, not behavioral agreement. `reconcile` is a CLI command, not an MCP tool.

## Not this

Not a GRC or HIPAA company. Not OpenAPI-as-source-of-truth. Not “we cut rework by 50%.” Not a toy app you deploy. The Docusaurus viewer under `legacy/` is archived — do not resurrect it.

## This repository

| Path | What it is |
|---|---|
| `specplane/` | Kit — schema, applicable sections, foundation boilerplates |
| `specs/` | Kernel product — SpecPlane specifying its CLI. **Do not copy into other apps.** |
| `tools/specplane/` | Local CLI + MCP |
| `examples/tiny-saas/` | Synthetic overlay + small `src/` for the try path |
| `.agents/skills/` and `.cursor/skills/` | Same skills (keep identical) |
| `docs/golden-journey.md` | Intended human+agent loop |
| `legacy/` | Archived viewer — not the product path |

Default schema **v9.1.0** (Capability, System, Container, Component, plus Foundations) is the structural model inside the graph. `impact` projects one affected subgraph as system, product, quality, governance, and ownership. Detail: [`docs/impact-perspectives.md`](./docs/impact-perspectives.md). Agent loading: [`AGENTS.md`](./AGENTS.md). You do not need that ontology to try the loop.

## License

Apache 2.0 — see [LICENSE](LICENSE).
