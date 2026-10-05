# Try SpecPlane in five minutes

You say the change in product language. The agent retrieves, blasts, and implements. You look at blast in `specplane view`.

The consumer obtain path is `pip install specplane` (or `uv tool install specplane`). This page stays the clone.

Synthetic sandbox: [`examples/tiny-saas`](../examples/tiny-saas/). Auth, billing, notifications, one open billing change. Live promise: **reset links expire in 60 minutes**. Leave `testdata/golden/messy_auth` for kernel tests.

## 1. Clone and open the example

```bash
git clone https://github.com/gauravbaruah/SpecPlane.git
cd SpecPlane
pip install -e .
```

Python 3.10+. `pip install pyyaml` does not install a `specplane` command. `python3 tools/specplane/cli.py` needs PyYAML importable and is still not `specplane` on PATH.

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

From `examples/tiny-saas`, after the install in section 1:

```bash
specplane retrieve capability.authentication
specplane blast component.password_reset
specplane check_sync --changed-ids capability.billing
```

Other install shapes are under [Advanced](#advanced).

## 4. The catch

`retrieve capability.authentication` prints the live sentence: **Password reset links expire in 60 minutes**. It does not print the whole file, and it does not read `src/auth.py`.

A one-line TTL is not a one-file idea. `blast` and `impact` of `capability.authentication` name `capability.notifications`, `capability.billing`, `component.notifier`, and `foundation.security_baseline`.

**Invisible.** With no `implementation.realization.paths` on `component.password_reset`, and without `check_sync --changed-ids`, editing `60` to `15` in `src/auth.py` never enters the default changed-set. The kernel does not parse that file.

**Caught as coverage.** This example declares `src/auth.py` on `component.password_reset`. A change to that file (or an explicit `--changed-ids component.password_reset`) puts the component in the changed-set. The only open change is `add_dunning`, which covers billing, not auth. `check_sync` then fails coverage. That is declared coverage, not proof the code matches the sentence, and not a GitHub check blocking a commit.

Maps stay optional on every other product. This demo declares one path so the try path can show the join.

## 5. What the change puts at risk

From `examples/tiny-saas`, after the install above:

```bash
specplane view
```

The server prints a `http://127.0.0.1` URL. Open it, then open Blast for `capability.authentication`:

```text
#id/capability.authentication?proj=blast
```

![Blast of capability.authentication: what a 60→15 change puts at risk](./view-blast.png)

Changes → `add_dunning`. Leave it; 60→15 is a new folder.

![Open change add_dunning. Reset-link expiry stays 60 minutes.](./view-change.png)

That picture is the question: **what does a 60→15 change put at risk?** Farther hops stay collapsed until you expand them. `blast` of that id names `capability.notifications`, `capability.billing`, `component.notifier`, `component.password_reset`, `component.billing_api`, and `foundation.security_baseline`. It is the affected subgraph, not a tour of the architecture. It does not block a pull request.

## 6. Your product

```bash
cd /path/to/your-app
uvx --from git+https://github.com/gauravbaruah/SpecPlane.git@main specplane init
```

Details: [`use-in-your-project.md`](./use-in-your-project.md). Do not copy this repo’s `specs/` (those YAML files specify SpecPlane’s own CLI).

Local MCP is optional. After install, `specplane mcp` starts the same stdio server. Skills already call the kernel. Same six tools: retrieve, blast, impact, check_sync, list_gaps, run. Validate stays CLI-only. `reconcile` is CLI-only: optional declared file maps, including greenfield with no infer. `run` joins a bound check; it is not a test runner. `impact` explains one affected subgraph; it does not replace `blast`.

Copy-paste Cursor / Claude Desktop / Claude Code snippets: [README — Optional: local MCP](../README.md#optional-local-mcp).

## Advanced

`python3 tools/specplane/cli.py` is the same CLI when `specplane` is not on PATH. From a SpecPlane checkout, `uvx --from ../.. specplane …` also works inside `examples/tiny-saas` after `pip install -e ../..`. A hand copy of the toolkit is in [`use-in-your-project.md`](./use-in-your-project.md). `pip install specplane` and `uv tool install specplane` install the pre-release `0.1.0a1`.
