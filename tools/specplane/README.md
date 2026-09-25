# SpecPlane toolkit

Optional local commands for v9.1.0 specs. Copy `tools/specplane/` into a product repo alongside `specplane/` and `specs/` if you want the agent (or you) to run checks in a session.

Requires Python 3.10+ and PyYAML.

```bash
uvx --from git+https://github.com/gauravbaruah/SpecPlane.git@main specplane init --dest /path/to/product
# or from a checkout: pip install -e .   then specplane …
# or: python3 tools/specplane/cli.py …
```

Five-minute try: [`docs/try.md`](../../docs/try.md) (`examples/tiny-saas`). Intended loop: [`docs/golden-journey.md`](../../docs/golden-journey.md).

**Works with your coding agent.** Skills call this kernel today. Local MCP is available for retrieve, blast, check_sync, and list_gaps. Humans should not have to type those commands.

## Kernel CLI

Simple commands. Agents call them. No model in the loop.

```bash
specplane init --dest /path/to/product
specplane validate --spec-root specs
specplane retrieve <id> --spec-root specs
specplane blast <id> --spec-root specs
specplane check_sync --spec-root specs --changed-ids component.foo
specplane check_sync --spec-root specs --change <slug> --changed-ids component.foo
specplane list_gaps --spec-root specs
python3 tools/specplane/mcp_stdio.py
```

`python3 tools/specplane/cli.py …` is the same CLI if you did not `pip install -e .`.

| Command | Job | Exit 1 when |
|---|---|---|
| `init` | Copy kit + skills + CLI; empty `specs/` folders; append AGENTS.md. Never copies kernel `specs/`. | Dest is kit root, or `specplane/` exists without `--force` |
| `validate` | Structural YAML, names, bidirectional links. Skips `specs/changes/`. | Errors |
| `retrieve <id>` | One live slice, `replaced` leftovers, open change folders | Unknown id |
| `blast <id>` | Affects tree. Component deps recurse. **Foundations are terminal** (listed, not exploded via `used_by`). | Unknown id |
| `check_sync` | Declared coverage vs open change `promise_ids` (pass `--change` after implement). Linked empty blast fails. Phase 1 (no join edges) is advisory. Does **not** parse app source or verify behavior. | Uncovered linked id, empty blast on a linked id, unknown id, or unknown `--change` |
| `list_gaps` | Kernel-generic queue: Phase 1 thin, open changes, replaced leftovers, missing sensors. Advisory. | Spec root missing |

`check_sync --changed-ids` is explicit. If omitted, spec YAML in git diff **plus untracked** `specs/**/*.yaml` (not `specs/changes/`) are mapped to ids. After implement, pass `--change <slug>` so a broad open change cannot satisfy coverage. A coverage pass is declared coverage, not behavioral agreement.

MCP stdio (`mcp_stdio.py`) exposes **retrieve, blast, check_sync, list_gaps** — same kernel functions. `check_sync` accepts `change` and `changed_ids` like the CLI. Validate is CLI-only (shell out).

`python3 tools/specplane/validate.py` still works as the validate-only entry point.

## Drift

Looks at git path names in the current change set. If `specs/` exists and app code changed with no spec YAML in that set, it prints a blocker. If only specs changed, it prints a warning. It does not compare contracts to source.

```bash
python3 tools/specplane/drift.py --scope changed
```

Use this in an agent or local terminal as a reminder. Do not treat this as a required pre-commit hook.

## Tests (this SpecPlane repository only)

The GitHub Action in this repo runs these commands against fixture trees. That workflow is for maintaining the toolkit, not a template to copy into a product.

```bash
python3 tools/specplane/test_validate.py
python3 tools/specplane/test_kernel.py
python3 tools/specplane/test_init.py
python3 tools/specplane/test_mcp.py
python3 tools/specplane/validate.py --spec-root tools/specplane/testdata/valid/specs
python3 tools/specplane/cli.py validate --spec-root tools/specplane/testdata/golden/messy_auth/specs
```
