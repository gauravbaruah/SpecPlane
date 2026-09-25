# code_maps

Locked with handoff D. GB did not override a default.

- Q111 B: declared `implementation.realization.paths`. The kernel does not grep and does not parse source bodies.
- D does not depend on infer. Cites are not maps. Do not copy `refs[].path` into `realization.paths`.
- Who writes paths: a human or an agent, explicitly. The kernel never rewrites the list to match the tree.
- A path ending in `/` matches that directory. Any other path is an exact file.
- A missing declared path is reported as `missing`. The entry stays. `check_sync` coverage does not fail for it.
- An unmapped changed app file is advisory. It is not silent, and it is not fail-closed.
- A mapped changed file contributes that component id to the `check_sync` default changed-set. `--changed-ids` overrides that set.
- No MCP `reconcile` tool. CLI only.
- Auto-write is forbidden.
- Greenfield can declare maps with no infer step.

## Promote (when accepted)

Apply these to live YAML, bump `meta.version` and changelog on each edited live file, then archive this folder.

- `component.cli_check_sync`: drop the open question "Optional realization.paths file map — later". Record optional maps, unmapped app files as advisory, and that a missing path does not fail coverage. Still do not parse source.
- `capability.specplane_check_sync`: the default changed-set is spec YAML plus declared path matches. Coverage is still declared coverage, not behavioral agreement. Do not print "verified."
- `component.mcp_stdio`: catalog stays retrieve, blast, check_sync, list_gaps, run. No reconcile tool.

Layout joins left for that promote, so this slice does not edit unrelated live files: `container.specplane_tools` contains / implements, `system.specplane_kernel` capabilities, and foundation `used_by` if `component.cli_reconcile` later lists `uses`.
