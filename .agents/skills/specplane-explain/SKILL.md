---
name: specplane-explain
description: Explain how something works from the specification, the open change, the implementation, and the evidence, kept apart. Use when the user asks how something works, why the code does this, or what the spec says versus the change. Do not use to author a spec or to implement a product change.
---

# SpecPlane Explain

Answer how something works. Keep four sources apart. Do not merge them into one story.

1. Run `context` on the spec id or the file the user named.

```bash
SPECPLANE_CALLER=cursor_skill python3 tools/specplane/cli.py context <target> --spec-root specs
```

Add `--change <slug>` when one open change is the task. Prefer `specplane` if it is on PATH.

2. If the command says the file is unmapped, stop. Do not invent a component. Do not parse the file into a spec. Quote the `SpecPlane ·` line.

3. Read implementation files only when `context` names a `realization.paths` entry for that component. Do not scan the repository for a match the command did not name.

4. Answer with four headings, in this order:

- **Specification** — the live text `context` printed (purpose, responsibilities, constraints).
- **Change** — the open change summaries. That is the implementation context. Canonical synchronization is pending until accept. If there is no open change, say so.
- **Implementation** — what the named files do. If none are declared, say none are declared.
- **Evidence** — each sensor's evidence and status. `UNVERIFIED` means no bound check passed. `VERIFIED` means a bound command passed. It does not mean the implementation satisfies the spec. `FAILED` means a bound command failed.

If the four disagree, say that in three sentences, one per disagreement. Do not pick a winner.

If a command prints a line that starts with `SpecPlane ·`, quote it unchanged. Do not invent a receipt. Do not add `--by` flags. Do not assign owners. Do not write `realized_by`. Components the graph does not name stay unmarked.

A readiness warning means implementation is underway and no implementation relationships are declared. Phase 1 stays valid. Do not add `realized_by` to clear the warning.
