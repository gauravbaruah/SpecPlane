# Optional CI

`specplane init` does not write this file. Paste it into a product repo if a pull request should run the kernel when no agent does.

The job calls the existing commands. It does not add a verb, and it does not turn the check into a required GitHub check. That stays a branch-protection choice.

On each pull request the script:

1. `validate` on `specs/`.
2. `check_sync` with its default changed-set: changed spec YAML, plus a component whose `implementation.realization.paths` match a changed file. It does not parse application source. An unmapped app file stays advisory. No covering open change fails the job. This runs even when the diff has no `specs/changes/<slug>/` folder.
3. When the diff does contain `specs/changes/<slug>/` (not `_archive`), also `check_sync --change <slug>` and `run --change <slug>`. `run` invokes binds on that folder only. `check_sync` still does not execute sensors.

`--apply-diff` soft-resets that CI checkout to the merge base so the default changed-set sees the pull-request diff. Do not run it in a checkout you want to keep.

```yaml
name: specplane-gate
on:
  pull_request:
permissions:
  contents: read
jobs:
  gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r tools/specplane/requirements.txt
      - run: pip install -e .
      - name: validate, check_sync, run
        run: >-
          python3 tools/specplane/ci_gate.py
          --base "origin/${{ github.base_ref }}"
          --spec-root specs
          --apply-diff
```

Copy `tools/specplane/ci_gate.py` with the workflow. Init does not copy either.
