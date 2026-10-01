# promote_accepted_overlays

GB accepted the live overlays (PR #31). The gate failed because those files
moved after the original folders were already in `_archive`.

This folder covers the same ids so default `check_sync` and `run --change`
can see an open change. Archive after merge.

2026-10-01. Pull request #32 also changed component.cli_blast,
component.cli_retrieve, component.cli_run, and component.cli_validate.
Those ids are named here so the gate can see one open change. Archive
after that pull request merges.

Accepted 2026-10-01. Pull request #32 is merged. This folder is archived.
