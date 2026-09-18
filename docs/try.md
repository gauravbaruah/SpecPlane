# Try SpecPlane in five minutes

One clone. This repo. No copying into a second app.

SpecPlane is an overlay of **intent**, not a sample SaaS. The sandbox is the `messy_auth` golden tree (auth, sessions, an open change). There is no `examples/tiny-saas/src/` — a fake backend would rot and imply this repo ships product code.

## 1. Install the kernel CLI

```bash
git clone https://github.com/gauravbaruah/SpecPlane.git
cd SpecPlane
pip install -e .
```

`python3 tools/specplane/cli.py` still works if you skip the editable install. There is no `npx specplane` / PyPI `uvx specplane init` yet: `init` copies kit files from a checkout, and we will not advertise a one-liner that cannot copy them.

## 2. Ask normally (retrieve)

```bash
specplane retrieve capability.authentication \
  --spec-root tools/specplane/testdata/golden/messy_auth/specs
```

You should see the live promise (identity + session), leftover `capability.auth_v1`, and open change `add_passkeys`. The live constraint is **session timeout 30 minutes**.

## 3. See impact (blast)

```bash
specplane blast component.session_manager \
  --spec-root tools/specplane/testdata/golden/messy_auth/specs
```

Likely affected: `capability.authentication`, `component.login_api`, `component.session_manager`, `component.token_store`. Foundation `security_baseline` is listed, not exploded.

## 4. Ship safely (check_sync + list_gaps)

```bash
specplane check_sync \
  --spec-root tools/specplane/testdata/golden/messy_auth/specs \
  --changed-ids capability.authentication

specplane list_gaps \
  --spec-root tools/specplane/testdata/golden/messy_auth/specs
```

`check_sync` passes here because `add_passkeys` already covers that capability. A **new** product change (30 → 15 minutes) needs its own change folder; `check_sync` then expects that folder to cover the ids you touch.

## 5. Say it to your coding agent

Do **not** run this evolve against SpecPlane’s own `specs/` (kernel CLI product). Make a throwaway overlay so you cannot hurt this repo:

```bash
specplane init --dest /tmp/auth-try
rm -rf /tmp/auth-try/specs
cp -R tools/specplane/testdata/golden/messy_auth/specs /tmp/auth-try/specs
```

Open **`/tmp/auth-try`** as the workspace (Cursor, Claude Code, or Codex). Same sentence in all of them:

> Sessions should expire in 15 minutes instead of 30.

You should not type `retrieve` or `blast`. The agent should classify this as an **evolve**, open `specs/changes/` in that throwaway tree, blast, ask only if a decision is actually unresolved, then reconcile with `check_sync`.

| Agent | What to open | Extra |
|---|---|---|
| **Cursor** | `/tmp/auth-try` | Skills already copied by `init`. Optional MCP below. |
| **Claude Code** | `/tmp/auth-try` | `CLAUDE.md` → `AGENTS.md`. |
| **Codex** | `/tmp/auth-try` | Skills under `.agents/skills/`. MCP optional; skills are enough. |

Intended chat shape: [`golden-journey.md`](./golden-journey.md).

Do **not** paste the master schema prompt into chat.

### Optional: local MCP

Skills already call the kernel. MCP is for tool-native agents. Same four functions: `retrieve`, `blast`, `check_sync`, `list_gaps`. Validate stays CLI-only.

Cursor (`~/.cursor/mcp.json` or project `.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "specplane": {
      "command": "python3",
      "args": ["tools/specplane/mcp_stdio.py"]
    }
  }
}
```

From `/tmp/auth-try` after init, point the MCP `command` at that copy’s `tools/specplane/mcp_stdio.py`. `spec_root` should be the throwaway `specs/`.

## Then your product

When you want overlay on **your** app: [`use-in-your-project.md`](./use-in-your-project.md). That is `init` into the product repo — still from a SpecPlane checkout. Do not copy this repo’s `specs/` (those YAML files specify SpecPlane’s own CLI).
