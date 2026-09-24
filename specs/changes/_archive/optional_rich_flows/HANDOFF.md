# Handoff — optional_rich_flows (kit landed, not promoted)

For a development agent after GB accepts or for leftover kernel work.

## Already done (this change)

- v9.1.0 reference + applicable 01, 04, 06, 10, 11: `flows` string **or** optional mapping; `open_questions` string **or** `{id, question, raised_from, status}`; component `user_flows.flow_ref`
- Skills: `.cursor/skills/specplane-flows/` and `.agents/skills/specplane-flows/` (keep identical)
- Author skills point at it; `AGENTS.md` + applicable README load table
- `initkit.py` consuming AGENTS lists `specplane-flows`
- Change folder: `specs/changes/optional_rich_flows/`
- POST: `validate` on `specs` and testdata/valid is clean. `check_sync --change optional_rich_flows --changed-ids capability.specplane_list_gaps,capability.specplane_init,component.cli_init` — coverage pass, sensors declared, **behavior unverified**

Do **not** promote live 5C kernel YAML for this. There is no new kernel capability.

## Do next (builder) — done 2026-09-24

1. **Promote** — GB accepted. Folder archived. No live 5C `meta.version` bump.
2. **Copy-the-kit drift** — `examples/tiny-saas/specplane` is a symlink to the kit. Already the same flows block.
3. **Validate hardening** — `specs/changes/flow_mapping_requires_id/`. Mapping flows require a non-empty `id`. `goal` stays optional. Not promoted into live capability YAML.
4. **list_gaps later** — still not this change.
5. **Dogfood** — `specs/changes/init_journey/`. One journey on `capability.specplane_init`. Not promoted.
6. **Init tests** — `test_init.py` was not edited, so no new skill-name assertion.

## Do not

- Pause `--change` / retrieve / blast
- Require journey+lifecycle+information on every file
- Add a second `open_questions` key
- Mint Intent/Journey/Lifecycle spec types
