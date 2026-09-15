# SpecPlane toolkit

Optional local commands for v9.1.0 specs. Copy `tools/specplane/` into a product repo alongside `specplane/` and `specs/` if you want the agent (or you) to run checks in a session.

They are **not** an installer. Do not wire them into Git hooks or CI/CD for a product repo yet. SpecPlane does not ship a setup program that can do that safely.

Requires Python 3.10+ and PyYAML:

```bash
pip install -r tools/specplane/requirements.txt
```

## Validate

Reads YAML under `specs/` and reports structural problems (filename/`meta.id`, folders, semver, changelog, link existence and bidirectional pairs, and related v9.1.0 rules). It does not judge product quality or whether code implements the spec.

```bash
python3 tools/specplane/validate.py --spec-root specs
python3 tools/specplane/validate.py
```

Exit `1` on errors. `--strict-warnings` also fails on warnings.

Copy [`specplane.config.json.example`](specplane.config.json.example) to the product repo as `specplane.config.json` if you want a default spec root.

## Drift

Looks at git path names in the current change set. If `specs/` exists and app code changed with no spec YAML in that set, it prints a blocker. If only specs changed, it prints a warning. It does not compare contracts to source.

```bash
python3 tools/specplane/drift.py --scope changed
```

Use this in an agent or local terminal as a reminder. Do not treat it as a required pre-commit hook.

## Tests (this SpecPlane repository only)

The GitHub Action in this repo runs these commands against fixture trees. That workflow is for maintaining the toolkit, not a template to copy into a product.

```bash
python3 tools/specplane/test_validate.py
python3 tools/specplane/validate.py --spec-root tools/specplane/testdata/valid/specs
```
