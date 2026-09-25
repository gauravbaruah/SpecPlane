# how_well_runner

Q140 is already answered (L49). This session did not override a locked default.

Bind a success.yaml claim to a check the user already owns: `run.argv` (a list of strings, no shell) and/or `run.unittest` (or `test:` / `run.test`). SpecPlane invokes that bind and records the exit. It does not write or choose the test.

English `must:` is the claim. No bind → `not_run`. The sentence is never executed.

`evaluator:` is a join. No `run:` → `not_run`. No dataset, scorer, or sim. Do not measure capability `success_metrics`. Do not parse `test_strategy`.

`check_sync` stays L1: declared coverage, each must `not_executed`, behavior unverified. `run` is a separate verb. SpecPlane is not the product’s test runner or CI.

Locked defaults that stand: verb `run`; `--change` required; exit 1 on an unknown or archived change, any `fail`, or any `error`; exit 0 when every runnable bind passed, including when every row is `not_run`; cwd is the repo root (`--repo` or the process cwd); inherit env; timeout 120s per sensor; `shell=False`; MCP catalog is retrieve, blast, check_sync, list_gaps, run; no backfill of `run:` onto the A folders; no promote until accept.

Live `capability.specplane_run` and `component.cli_run` wait for promote. Until then those ids are not in the live graph.

At promote, keep the join in the same change: `capability.specplane_run` `realized_by` `component.cli_run` and `component.mcp_stdio`; `component.cli_run` `implements` `capability.specplane_run`; `component.mcp_stdio` also implements it and `depends_on` `component.cli_run`; `container.specplane_tools` contains `component.cli_run`.
