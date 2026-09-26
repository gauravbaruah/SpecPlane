# SpecPlane toolkit

Optional local commands for v9.1.0 specs. Copy `tools/specplane/` into a product repo alongside `specplane/` and `specs/` if you want the agent (or you) to run checks in a session.

Requires Python 3.10+ and PyYAML.

```bash
uvx --from git+https://github.com/gauravbaruah/SpecPlane.git@main specplane init --dest /path/to/product
# or from a checkout: pip install -e .   then specplane …
# or: python3 tools/specplane/cli.py …
```

Five-minute try: [`docs/try.md`](../../docs/try.md) (`examples/tiny-saas`). Intended loop: [`docs/golden-journey.md`](../../docs/golden-journey.md).

**Works with your coding agent.** Skills call this kernel today. Local MCP is available for retrieve, blast, impact, check_sync, list_gaps, and run. Humans should not have to type those commands.

## Kernel CLI

Simple commands. Agents call them. No model in the loop.

```bash
specplane init --dest /path/to/product
specplane validate --spec-root specs
specplane retrieve <id> --spec-root specs
specplane blast <id> --spec-root specs
specplane impact <id> --spec-root specs
specplane check_sync --spec-root specs --changed-ids component.foo
specplane check_sync --spec-root specs --change <slug> --changed-ids component.foo
specplane reconcile --spec-root specs
specplane list_gaps --spec-root specs
specplane run --spec-root specs --change <slug>
specplane promote --ids capability.a,capability.b --spec-root specs
specplane view --spec-root specs
python3 tools/specplane/mcp_stdio.py
```

Optional editor wiring (Cursor `~/.cursor/mcp.json` or Claude Desktop `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "specplane": {
      "command": "python3",
      "args": ["/absolute/path/to/SpecPlane/tools/specplane/mcp_stdio.py"]
    }
  }
}
```

`python3` must be able to import PyYAML. There is no `specplane mcp` verb yet.

`python3 tools/specplane/cli.py …` is the same CLI if you did not `pip install -e .`.

| Command | Job | Exit 1 when |
|---|---|---|
| `init` | Copy kit + skills + CLI; empty `specs/` folders; append AGENTS.md. Never copies kernel `specs/`. | Dest is kit root, or `specplane/` exists without `--force` |
| `validate` | Structural YAML, names, bidirectional links. Skips `specs/changes/`. | Errors |
| `retrieve <id>` | One live slice, `replaced` leftovers, open change folders | Unknown id |
| `blast <id>` | Affects tree. Component deps recurse. **Foundations are terminal** (listed, not exploded via `used_by`). | Unknown id |
| `impact <id>` | One affected subgraph for a spec id or an open change folder, plus system, product, quality, governance, and ownership projections. Same join-key membership as `blast` for a spec id. Does not read a git diff. Absence of a field stays "not represented". | Unknown id |
| `check_sync` | Declared coverage vs open change `promise_ids` (pass `--change` after implement). Linked empty blast fails. Phase 1 (no join edges) is advisory. Does **not** parse app source or verify behavior. Default changed-set also includes a component id when a changed file matches `implementation.realization.paths`. | Uncovered linked id, empty blast on a linked id, unknown id, or unknown `--change`. A missing path or an unmapped app file does not fail coverage. |
| `reconcile` | Declared `implementation.realization.paths` vs the tree and git-changed files. Reports missing, unmapped_changed, mapped_changed. Optional maps. Greenfield can declare them without infer. Does **not** parse source, write paths, or pick spec vs code. | Spec root missing. Missing paths and unmapped app files stay advisory (exit 0). |
| `list_gaps` | Kernel-generic queue: Phase 1 thin, open changes, replaced leftovers, missing sensors, unpromoted inferred ids. Advisory. | Spec root missing |
| `run --change <slug>` | Join + invoke of a check already bound on that change (`run.argv` as a list, no shell, and/or `run.unittest` / `test:`). English `must:` is not a command (`not_run`). `evaluator:` with no bind is `not_run`. | Unknown or archived change, any sensor `fail`, or any sensor `error`. Exit 0 when every runnable bind passed, including when every row is `not_run`. |
| `promote --ids a,b` | Drop `inferred` on those ids and append a changelog row. The coding agent writes the inferred YAML via the `specplane-infer` skill. This command does not read application source. | No ids, unknown id, or an id that is not inferred. Writes nothing in those cases. |
| `view` | Human readout of retrieve, impact, list_gaps, and check_sync. Generates `.specplane/view/` and serves `127.0.0.1`. `--open` also launches the browser. `--out` chooses the directory and still serves. Read-only. No API key. | Spec root missing |

`check_sync --changed-ids` is explicit. If omitted, spec YAML in git diff **plus untracked** `specs/**/*.yaml` (not `specs/changes/`) are mapped to ids, and a changed file that matches a declared `implementation.realization.paths` entry adds that component id. Unmapped changed app files print as advisory and do not fail coverage. After implement, pass `--change <slug>` so a broad open change cannot satisfy coverage. A coverage pass is declared coverage, not behavioral agreement.

`reconcile` is the named file-to-promise check. Maps are optional declared joins. SpecPlane does not write your code. A directory prefix ends with `/`; any other path is an exact file. This works for greenfield with no infer step. Infer cites are not maps.

MCP stdio (`mcp_stdio.py`) exposes **retrieve, blast, impact, check_sync, list_gaps, run** — same kernel functions. `impact` takes an id or open change folder and does not require a git diff. `check_sync` accepts `change` and `changed_ids` like the CLI. `run` requires `change`. Validate, promote, and reconcile are CLI-only. There is no infer, specify, or implement tool. `run` does not replace pytest, Playwright, an eval harness, or CI. Brownfield mapping is the `specplane-infer` skill, not a kernel scan.

`python3 tools/specplane/validate.py` still works as the validate-only entry point.

## Drift

Looks at git path names in the current change set. If `specs/` exists and app code changed with no spec YAML in that set, it prints a blocker. If only specs changed, it prints a warning. It does not compare contracts to source. `reconcile` is the declared path check; this script does not replace it and does not grep file bodies.

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
python3 tools/specplane/test_view.py
python3 tools/specplane/validate.py --spec-root tools/specplane/testdata/valid/specs
python3 tools/specplane/cli.py validate --spec-root tools/specplane/testdata/golden/messy_auth/specs
```
