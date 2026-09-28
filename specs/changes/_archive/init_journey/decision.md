# init_journey — decisions

GB 2026-09-28.

## Partial copy

If init fails after copying some files, it does not try to roll back. It says what went wrong, then: delete `specplane/`, the `specplane-*` skills and rules, `tools/specplane/`, and `specplane.config.json`, and run init again. Leave `specs/` alone.

## --force

`--force` replaces the kit copy. It does not keep a previous kit file the new copy no longer has. It does not delete or empty `specs/`. It does not remove a SpecPlane block already in `AGENTS.md`.

Generated `.specplane/view/` is output. `--force` deletes that directory so the next `specplane view` builds from the replaced kit. Init does not start the viewer.

## Removal

There is no uninstall command. Removing the kit is the same delete list as a failed init. `specs/` stays. Termination of the product overlay is outside this capability.
