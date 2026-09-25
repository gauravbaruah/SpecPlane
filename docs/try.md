# Try SpecPlane in five minutes

Synthetic sandbox: [`examples/tiny-saas`](../examples/tiny-saas/). Auth, billing, notifications, one open billing change. Live promise: **reset links expire in 60 minutes**. Leave `testdata/golden/messy_auth` for kernel tests.

## 1. Clone and open the example

```bash
git clone https://github.com/gauravbaruah/SpecPlane.git
cd SpecPlane
```

Open **`examples/tiny-saas`** as the workspace (File → Open Folder). Skills and the kit are already linked there.

## 2. Ask Cursor (or Claude Code / Codex)

> Reset links should expire in 15 minutes instead of 60.

You should not type `retrieve` or `blast`. The agent should **retrieve** `capability.authentication`, **classify evolve**, **blast** `component.password_reset`, open a change folder (leave `add_dunning` alone), implement `src/auth.py`, then **check_sync**, then **run --change** if that folder binds a check. `run` does not create the test.

Intended chat shape: [`golden-journey.md`](./golden-journey.md). Do not paste the master schema prompt into chat.

| Agent | What to open |
|---|---|
| Cursor | `examples/tiny-saas` |
| Claude Code | `examples/tiny-saas` (`CLAUDE.md` → `AGENTS.md`) |
| Codex | `examples/tiny-saas` |

## 3. Optional: run the kernel yourself

From `examples/tiny-saas`, after `pip install -e ../..` at the SpecPlane root (or `uvx --from ../.. specplane …`):

```bash
specplane retrieve capability.authentication
specplane blast component.password_reset
specplane check_sync --changed-ids capability.billing
```

## 4. Your product

```bash
cd /path/to/your-app
uvx --from git+https://github.com/gauravbaruah/SpecPlane.git@main specplane init
```

Details: [`use-in-your-project.md`](./use-in-your-project.md). Do not copy this repo’s `specs/` (those YAML files specify SpecPlane’s own CLI).

Local MCP is optional. Skills already call the kernel. Same six tools: retrieve, blast, impact, check_sync, list_gaps, run. Validate stays CLI-only. `reconcile` is CLI-only: optional declared file maps, including greenfield with no infer. `run` joins a bound check; it is not a test runner. `impact` explains one affected subgraph; it does not replace `blast`.
