# Viewer activity

Class: **evolve.** Not built. Live viewer text stays until this is accepted.

The tab is named **Activity**. It sits beside Live, Changes, and Gaps. Those three stay the spec. Activity is how SpecPlane was used on this machine.

The window is the last 30 days of the local command log. The page shows counts: command name, how many exited 0, how many did not, and the allowlisted caller. Copy summary copies those sentences. Nothing is posted.

A nonzero command followed later by one that exited 0 is printed as that sequence. It is not called a catch, a correction, or an override.

The copy omits installation, session, and run ids. The foundation sentence is unchanged: this is not hosted telemetry.

Accepted shape of the page:

```text
SpecPlane on this machine — last 30 days
retrieve 19 · 19 ok
check_sync 8 · 5 ok · 3 nonzero
run 6 · 6 ok
caller · cursor_skill 28 · human_cli 5
check_sync nonzero, then later ok · 1
```

That last line is the sequence. It does not say the agent fixed the spec.
