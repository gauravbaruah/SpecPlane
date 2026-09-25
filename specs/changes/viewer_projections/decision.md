# viewer_projections — decisions

GB 2026-09-25. Boring infrastructure. The viewer is a projection of the existing SpecPlane installation, not a second application ecosystem.

Layout, install, serve, and Mermaid stay locked below. Chrome: navbar and honesty stay; the projection set is the Viewer v2 override later in this file.

## Classify

- **learn** on new `capability.specplane_viewer` (human socket, not a sixth compute kernel). Does not exist live yet.
- **evolve** on `capability.specplane_init` / `component.cli_init` when we implement: `init` copies the viewer generator with the CLI. `--kit-only` still skips both.

## Install and paths

| Thing | Path | Committed? |
|---|---|---|
| Generator | `tools/specplane/view.py` | yes |
| Templates / static / vendor | `tools/specplane/viewer/` | yes (including pinned Mermaid) |
| Default generated pages | `.specplane/view/` | **no** — gitignore |
| YAML overlay | `specs/` | yes — never write generated HTML here |

- Same kit / wheel / `init` mechanism as the kernel. Grow `CLI_FILES` and `packaging/bundle_kit.py` to include `view.py` and the `viewer/` tree.
- `--kit-only` does not copy the viewer.
- No npm. No separate viewer package. No `apps/viewer`. No `tools/specplane/_view/` (that muddies generator vs output).
- Do not resurrect `legacy/specplane_viewer` or Docusaurus.

## Commands

```text
specplane view                 generate into .specplane/view/, serve 127.0.0.1, print URL
specplane view --open          same, and launch the browser
specplane view --out DIR       generate into DIR; still serve unless we later add --static
specplane view --spec-root R   same as other kernel commands
```

- Default is **serve**, not export-only. `--open` means also launch the browser.
- Server: stdlib / lightweight, **local-only**, ephemeral. Bind `127.0.0.1` (not `0.0.0.0`).
- `--out` chooses the output directory. It is not “skip the server.”
- If we need an artifact without serving, add `specplane view --static` or `specplane export viewer` later. Do not overload `--open` or `--out` for that.

## Mermaid

- **Vendor** a pinned Mermaid build under `tools/specplane/viewer/vendor/` — Mermaid **10.9.3** (`mermaid.min.js`). The page does not load it from a CDN. Diagrams stay off the switcher until the kernel returns diagram source.
- No CDN. Offline / no-account / no-key is a Community property.
- Rendering must not change because a CDN moved.
- A flowchart or sequence is drawn in the column at its layout size. The page scrolls. A picture wider than the column scrolls inside the column. It does not capture the wheel to zoom, and it does not run to the screen edge. Map and Blast keep pan and zoom.

## Data (do not slurp)

Call `retrieve`, `impact`, `list_gaps`, `check_sync`. `blast` is coverage buckets only. Do not reimplement impact projectors.

## Chrome override — Viewer v2 (GB 2026-09-25)

Provisional. Viewer v2 is the working design (`design-docs/design-references/SpecPlane viewer design (5).zip`, canvas `Viewer v2.dc.html`). Build toward those frames. They are the surface GB would actually use. Runtime may omit or reshape a block when the payload has no field for it. That is expected, and it is not a reason to shrink the design back to the earlier wireframe.

Unlocked. Full text: `viewer2-amendment.md` in this folder (also in `design-docs/handoffs/H-E-viewer.md`, which is gitignored).

- The projection control may offer **Map, Blast, Layers, Journey, Diagrams, and Data** when the record has that data. One slot: the selected projection replaces the picture. A projection with nothing to draw is omitted. Sequence is a diagram type inside Diagrams, not its own tab. Diagrams is where a record shows the diagrams it holds.
- Blast may be read five ways (System, Product, Quality, Governance, Ownership) on that same drawing. The perspective control is subordinate to the projection switcher. Nodes stay put. Empty speech is “not represented,” “No governance relationship identified in the current model,” or “Ownership not represented,” depending on the reading.

Still in force:

- Navbar is Live, Changes, Gaps, plus the open id, bit, and `review_state`.
- Those five readings stay inside Blast. They are not navbar homes.
- Inferred never looks live. Sensor sentences are not links. No Share, Upgrade, persona switch, API key, or YAML edit.
- The path on a selected affected id comes from `impact.affected[].path`. The viewer does not walk the graph itself.

## Blast hop columns (real — not “cannot say yet”)

The Viewer 2 hop strip is a **projection of `impact.affected`**. Do not omit it, and do not invent a second chain in the browser.

| Column | Kernel field |
|---|---|
| Selected | `distance === 0` |
| 1 hop · direct | `distance === 1` (`direct` is true) |
| 2 hops | `distance === 2` |
| Further | `distance >= 3`, collapsed until expand. Copy: `+N more ids at 3+ hops — select to expand` |

On a card, print `relationship` + via (last `path` step’s `from`), then `direct` / `N hops` / `terminal · not expanding` (foundation or incoming `uses`), then `epistemic_state`. Why-panel stays `path`.

**No longer blank (do not hide behind “The model cannot say yet”):**

- Hop-by-hop reason → `impact.affected[].path`
- Owner / CODEOWNERS → Ownership perspective (`meta.owner` or derived CODEOWNERS)
- Diagram picture → declared `type` / `title` / `description` / `mermaid`

**Still cannot say — omit, do not invent:**

- `about` / `flow_ref` matching a flowchart to `flows.stages`
- Who handles a journey stage
- Evidence behind `review_state`
- The check bound to a sensor
- Which stage a change touches (no lifecycle enum)
- A missing field is omitted. No empty card just to keep the page symmetrical.

## Chrome (navbar and honesty)

Navbar: Live, Changes, Gaps, current id + bit + `review_state`.  
Not in the navbar: personas, architecture home, System/Product/Quality/Governance/Ownership.

Perspectives: inside Blast only. Empty speech: “not represented,” never “no security impact” / “no QA required.”

GenUI / Astra: **not v1**. No API key.

Read-only. No YAML edit. PR markdown remains the free review path. Threads / share / GH App are H-F.

## Display table

| Stays visible | Collapsed until asked |
|---|---|
| Purpose, bit, review_state | Full responsibilities / changelog |
| Open changes for this id | Foundations list |
| One projection (Map, Blast, Layers, Journey, Diagrams, or Data — whichever this payload has). Sequence is inside Diagrams | The other projections, via the control |
| Coverage / sensors band on a change | How-well `success_metrics` targets |

Clickable: spec ids, change slugs, `refs[].url`.  
Not clickable: `must:` / sensor prose, diagram edge labels, inferred-as-live styling, changelog body.

## OSS vs paid

Local viewer is Community forever. No Share / Upgrade chrome. Paid hosted index is H-F.
