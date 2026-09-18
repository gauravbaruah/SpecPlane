# SpecPlane

**Keep coding agents aligned with what you actually meant to build.**

SpecPlane keeps product intent, architecture, constraints, and code changes connected in git — so agents can retrieve the right context, see blast radius, and surface decisions before they guess.

It is a **git-native overlay of what a living product should do and how well** — not how it is implemented. You speak product language. The agent uses SpecPlane. You answer only consequential decisions.

<img src="./SpecPlane_Logo.png" alt="SpecPlane" width="160">

## The loop

You tell your coding agent:

> Sessions should expire in 15 minutes instead of 30.

SpecPlane retrieves the current promise, notices this is a product-behavior change, computes what else is affected, asks you one unresolved question if necessary, and gives the coding agent the minimum context it needs.

The agent implements. SpecPlane checks that the change stayed aligned with intent.

Ceremony scales with **semantic consequence**, not diff size. A 4px nudge is not a spec. A one-line change to a shared rule can be.

### SpecPlane should stay out of your way

| You ask | What happens |
|---|---|
| “Fix the typo” | Agent just fixes it |
| “Rename this helper” | Agent just does it |
| “Sessions expire in 15m, not 30m” | SpecPlane tracks the product change |
| “Make destructive actions green” | SpecPlane warns if this changes a shared design rule |

Full transcript: [`docs/golden-journey.md`](./docs/golden-journey.md).

## See impact

`blast` on the golden auth tree — who else is tied to `component.session_manager`:

![blast component.session_manager on the messy_auth golden tree](./docs/blast.gif)

That GIF is **see impact**, not the whole loop. The whole loop is retrieve → classify → change folder → blast → decide → implement → `check_sync`. Run it yourself in the next section; do not wait for a staged Cursor recording.

## Try it in five minutes

Clone **this** repo. Do not copy files into a second app yet.

```bash
git clone https://github.com/gauravbaruah/SpecPlane.git
cd SpecPlane
pip install -e .
```

**Ask normally** — current promise (live bit, leftovers, open change):

```bash
specplane retrieve capability.authentication \
  --spec-root tools/specplane/testdata/golden/messy_auth/specs
```

**See impact** — likely affected components and constraints (foundations are listed, not exploded):

```bash
specplane blast component.session_manager \
  --spec-root tools/specplane/testdata/golden/messy_auth/specs
```

**Ship safely** — changed ids vs open change folders; then the gap queue:

```bash
specplane check_sync \
  --spec-root tools/specplane/testdata/golden/messy_auth/specs \
  --changed-ids capability.authentication

specplane list_gaps \
  --spec-root tools/specplane/testdata/golden/messy_auth/specs
```

The golden tree is a small **auth overlay** (session timeout is 30 minutes; passkeys are in-flight). It is not a running SaaS. SpecPlane’s job is the overlay.

Then say this to your coding agent (in a throwaway overlay — **not** this repo’s `specs/`, which is SpecPlane’s own CLI):

> Sessions should expire in 15 minutes instead of 30.

Recipe for Cursor / Claude Code / Codex, plus optional MCP: [`docs/try.md`](./docs/try.md).

**Works with your coding agent.** Cursor, Claude Code, and Codex can use the same deterministic kernel through skills today. Local MCP (`tools/specplane/mcp_stdio.py`) exposes `retrieve`, `blast`, `check_sync`, and `list_gaps` when you want tool-native calls. You are not meant to operate this by hand.

## Use it in your product

After the five-minute try: copy the **kit** into *your* repo. Your `specs/` is your overlay. This GitHub tree’s `specs/` is SpecPlane specifying its own CLI — do **not** copy that into an app.

From a SpecPlane checkout, in the product repo:

```bash
pip install -e /path/to/SpecPlane   # gives the `specplane` command
specplane init
```

`python3 /path/to/SpecPlane/tools/specplane/cli.py init` still works without the editable install. Empty `specs/` folders are created. Then ask for a Phase 1 capability. Schema **v9.1.0**.

There is no published `npx specplane` / `uvx specplane init` yet. `init` copies kit files from a checkout; we will not pretend a registry package does that.

Details: [`docs/use-in-your-project.md`](./docs/use-in-your-project.md).

## Free now

Kit + local kernel (`validate`, `retrieve`, `blast`, `check_sync`, `list_gaps`, `init`) + skills + optional stdio MCP. No SpecPlane API key.

## Later (not shipped)

Paid when the free loop is loved: a spec **coach**, a **required GitHub check**, a **viewer** over the same ids. Do not treat those as available today.

## Not this

Not a GRC or HIPAA company. Not OpenAPI-as-source-of-truth. Not “we cut rework by 50%.” Not a toy app you deploy. The Docusaurus viewer under `legacy/` is archived — do not resurrect it.

We will not invent dogfood stats (“interrupted 2 of 11 changes”) until a real product run produces them.

## This repository

| Path | What it is |
|---|---|
| `specplane/` | Kit — schema, applicable sections, foundation boilerplates |
| `specs/` | Kernel product — SpecPlane specifying its CLI. **Do not copy into other apps.** |
| `tools/specplane/` | Local CLI + MCP |
| `.agents/skills/` and `.cursor/skills/` | Same skills (keep identical) |
| `docs/golden-journey.md` | Intended human+agent loop |
| `docs/try.md` | Five-minute try on `messy_auth` |
| `legacy/` | Archived viewer — not the product path |

Default schema **v9.1.0** (Capability, System, Container, Component, plus Foundations). Agent loading: [`AGENTS.md`](./AGENTS.md). You do not need that ontology to try the loop.

## License

Apache 2.0 — see [LICENSE](LICENSE).
