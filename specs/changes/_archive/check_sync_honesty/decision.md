# check_sync_honesty

Kind: **fix**. Opened 2026-09-17.

Q115 (untracked specs in the default changed-set) and Q116 (Phase 1 advisory, not fail) land together. Q115 alone would make `check_sync` fail every new Phase 1 capability. v1 still does not parse application source.
