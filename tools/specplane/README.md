# SpecPlane toolkit

Generic validator and drift gate for v9.1.0 specs. Copy `tools/specplane/` into a product repo alongside `specplane/` and `specs/`.

Requires Python 3.10+ and [PyYAML](https://pypi.org/project/PyYAML/):

```bash
pip install -r tools/specplane/requirements.txt
```

## Validate

Checks filename/`meta.id`, folder layout, semver, changelog, `introduced_in`, deprecation fields, `implements`/`uses` existence, bidirectional links, classification, rollout flags, analytics emitters, and diagram refs (applicable section 08).

```bash
python3 tools/specplane/validate.py --spec-root specs
# or, with specplane.config.json in the project root:
python3 tools/specplane/validate.py
```

Exit `1` on errors. `--strict-warnings` also fails on warnings.

Copy [`specplane.config.json.example`](specplane.config.json.example) to the product repo as `specplane.config.json`.

## Drift

When `specs/` exists, staged/unstaged code changes without spec YAML updates are a blocker. This is a process gate, not a semantic spec-vs-source prover.

```bash
python3 tools/specplane/drift.py --scope changed
```

Record `Spec-Impact: none` in the commit/PR if the code change truly has no spec impact, then skip or waive the gate locally.

## Tests (this repo)

```bash
python3 tools/specplane/test_validate.py
python3 tools/specplane/validate.py --spec-root tools/specplane/testdata/valid/specs
```
