# Local usage report

Class: **evolve.** Retrieved `capability.specplane_telemetry_share` and `foundation.observability_standards`. The live law is a local log, upload never, and a viewer reminder. There is no command that sends anything.

## Decided

Agreed with the advisor's boundary, and with holding the send until strangers use the alpha.

- The person-facing command is `usage`. `telemetry` remains an alias so an old line still runs. New events record `usage_*`.
- `usage report` prints counts for this machine over the last 30 days and stops. The object is schema, version, period, command counts, caller counts, success, and failure.
- The report drops installation id, project id, paths, timestamps, and spec names. It does not invent days active, upgrades, or a command named extract.
- Nothing is sent. There is no `[y/N]` and no endpoint in this change.
- `SPECPLANE_TELEMETRY` and `telemetry.json` keep their names so an existing off switch still works.
- The seven-day GitHub notice and the star request stay feedback. They are not this report.

## Not in this change

`usage share`, a receiving endpoint, and a product email address wait until strangers are using the alpha.
