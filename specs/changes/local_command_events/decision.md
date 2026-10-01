# Local command events

Retrieved `foundation.observability_standards` first. Its live purpose is stdout, exit code, and join-keyed findings, not hosted telemetry. It also says there is no opt-in product telemetry in the first slice.

Class: **learn.** The live sentences stay until accept. The experiment is a local log.

## What this slice does

- The CLI, not the skill text, writes the event. A skill is visible only when it sets `SPECPLANE_CALLER` to an allowlisted label.
- Default on, local only. `telemetry disable` turns it off. `SPECPLANE_TELEMETRY=0` forces off for that process. Nothing is uploaded.
- One JSON line per command: name, exit code, `ok` or `nonzero`, duration, version, installation id, allowlisted caller. Optional `run_id` and `session_id` only when they match a short token.
- A failed write does not change the exit code.
- `telemetry show` prints the local file. `upload: never`.

## What this slice does not do

Hosted ingest, shadow evaluation, an intervention rate, a new foundation, or a claim that a nonzero exit stopped an agent from doing something awful. Those need a later accept. Reading a skill file is not an event.
