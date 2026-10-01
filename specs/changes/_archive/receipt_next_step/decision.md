# Receipt next step

Class: **evolve.** The live line states what was established. This change adds the next step on that same line when the command stopped short.

Accepted wording:

- Uncovered: name the ids. Put them on an open change, then check_sync again.
- Declared sensors: they were not executed. Run `specplane run --change <slug>`.
- Phase 1: Phase 1 is valid. No component is linked yet, so an empty impact list is a warning.
- Retrieve with an open change: that change is still open. Keep working in that folder, or accept it so retrieve shows one live graph.
- Run pass: the checks do not certify the spec. The next human step is to accept the change, or keep editing.
- Validate with errors: fix the errors and validate again. Zero errors stay silent.

A blast that already names impact still has no receipt. An unbound run already names the sensor to bind.
