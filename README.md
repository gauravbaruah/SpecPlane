# SpecPlane

SpecPlane is a **git-native overlay of what a living product should do and how well** — not how it is implemented.

<img src="./SpecPlane_Logo.png" alt="SpecPlane" width="160">

A change → who else is tied to that id:

![blast component.session_manager on the messy_auth golden tree](./docs/blast.gif)

```bash
python3 tools/specplane/cli.py blast component.session_manager \
  --spec-root tools/specplane/testdata/golden/messy_auth/specs
```

## Free now

Copy the kit into *your* product repo. Local CLI: `validate`, `retrieve`, `blast`, `check_sync` (and `init`). Skills + [`docs/golden-journey.md`](./docs/golden-journey.md) tell the coding agent when to call those commands. You should not have to type `retrieve`.

## Later (not shipped)

Paid when the free loop is loved: a spec **coach**, a **required GitHub check**, a **viewer** over the same ids. Do not treat those as available today.

## Not this

Not a GRC or HIPAA company. Not OpenAPI-as-source-of-truth. Not “we cut rework by 50%.” The Docusaurus viewer under `legacy/` is archived — do not resurrect it.

## Quick start

Your product repo holds *your* `specs/`. This GitHub tree also has a `specs/` folder for **SpecPlane’s own CLI** — do **not** copy that into an app.

From a [SpecPlane](https://github.com/gauravbaruah/SpecPlane) clone, in the product repo:

```bash
python3 /path/to/SpecPlane/tools/specplane/cli.py init
pip install -r tools/specplane/requirements.txt   # for retrieve / blast / check_sync
```

Open the **product** workspace. Ask for a **Phase 1** capability (`responsibilities`, `flows`, `business_value`, `constraints`). Schema **v9.1.0**. Empty `specs/` folders already exist.

Then speak product language. The agent should follow the [golden journey](./docs/golden-journey.md). Full copy steps: [Use SpecPlane in your project](./docs/use-in-your-project.md).

Do not paste the full master prompt into chat.

## This repository

| Path | What it is |
|---|---|
| `specplane/` | Kit — schema, applicable sections, foundation boilerplates |
| `specs/` | Kernel product — SpecPlane specifying its CLI. **Do not copy into other apps.** |
| `tools/specplane/` | Local CLI |
| `.agents/skills/` and `.cursor/skills/` | Same skills (keep identical) |
| `docs/golden-journey.md` | Intended human+agent loop |
| `legacy/` | Archived viewer — not the product path |

Default schema **v9.1.0**. Agent loading: [`AGENTS.md`](./AGENTS.md).

## License

Apache 2.0 — see [LICENSE](LICENSE).
