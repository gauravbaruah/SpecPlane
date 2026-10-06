# Change folders

In-flight write path for the kernel (`kind: learn | fix | evolve`). Not 5C specs.

After the human says ship it: `specplane promote <slug>` applies the delta to live YAML and moves the folder to `specs/changes/_archive/<id>/`. `retrieve` / `list_gaps` skip `_archive` as open work. Completion is before merge.

