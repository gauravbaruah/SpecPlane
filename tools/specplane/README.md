# SpecPlane toolkit

Optional local commands for v9.1.0 specs. Copy `tools/specplane/` into a product repo alongside `specplane/` and `specs/` if you want the agent (or you) to run checks in a session.

`init` copies the kit into a **product** repo. It does not write Git hooks or CI/CD.

Agents call retrieve / blast / check_sync. Humans should not have to. Intended loop: [`docs/golden-journey.md`](../../docs/golden-journey.md).

Requires Python 3.10+ and PyYAML:

```bash
pip install -r tools/specplane/requirements.txt
```

## Kernel CLI

Simple commands. Agents call them. No model in the loop.

```bash
python3 tools/specplane/cli.py init --dest /path/to/product
python3 tools/specplane/cli.py validate --spec-root specs
python3 tools/specplane/cli.py retrieve <id> --spec-root specs
python3 tools/specplane/cli.py blast <id> --spec-root specs
python3 tools/specplane/cli.py check_sync --spec-root specs --changed-ids component.foo
```

| Command | Job | Exit 1 when |
|---|---|---|
| `init` | Copy kit + skills + CLI; empty `specs/` folders; append AGENTS.md. Never copies kernel `specs/`. | Dest is kit root, or `specplane/` exists without `--force` |
| `validate` | Structural YAML, names, bidirectional links. Skips `specs/changes/`. | Errors |
| `retrieve <id>` | One live slice, `replaced` leftovers, open change folders | Unknown id |
| `blast <id>` | Affects tree. Component deps recurse. **Foundations are terminal** (listed, not exploded via `used_by`). | Unknown id |
| `check_sync` | Changed ids vs open change `promise_ids`. Empty blast fails. Does **not** parse app source. | Uncovered id, empty blast, or unknown id |

`check_sync --changed-ids` is explicit. If omitted, spec YAML files in `git diff` are mapped to ids.

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
python3 tools/specplane/validate.py --spec-root tools/specplane/testdata/valid/specs
python3 tools/specplane/cli.py validate --spec-root tools/specplane/testdata/golden/messy_auth/specs
```
