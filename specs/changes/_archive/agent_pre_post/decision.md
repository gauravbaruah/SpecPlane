# PRE gate

Question: retrieve on every paste, or only when a promise might move?

- **A** — retrieve before any write; “no spec impact” only after retrieve
- **B** — retrieve when a promise might move; typos / 4px / rename skip retrieve; if unsure, retrieve

**Chose B** (2026-09-18). Stay out of the way. Ceremony follows semantic consequence.

Asking the human is the coding agent following the skill. The kernel does not watch the chat. Codex (or any other agent) surfaces leftover/uncovered ids only if it actually runs retrieve / blast / list_gaps / check_sync.
