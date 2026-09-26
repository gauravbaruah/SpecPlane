# readme_onramp

No blocking product decision for the README fix.

Part 2 from the independent-agent critique is recorded as L62 / Q181–Q184. Not implemented in this change:

1. `specplane mcp` — schedule. Thin wrapper only. Same catalog.
2. `specplane change promote <slug>` — later. Do not overload `promote --ids`. Human accept stays.
3. Actionable `check_sync` next-step speech — schedule. Speech only. Do not stamp live.
4. Init-written hooks / `check_sync --strict` — reject. Live init already refuses Actions and hooks. Optional copy-paste CI later, not a new flag that does not exist.
