## Amendment — implement the current Viewer 2 design

Advisor addendum, 2026-09-25. Where this section conflicts with the older presentation bullets below (capability page as purpose + contract + failure + constraint + success, or one Mermaid plus an optional blast overlay), **this section wins**. Kernel boundaries in the header stay.

H-E remains authoritative for:

- kernel/tool boundaries
- local/free/offline scope
- read-only behavior
- no YAML walking
- no reimplementation of `impact`
- no Cloud/GitHub App/Stripe/comments
- epistemic honesty
- deterministic graph/projector behavior
- use of existing `retrieve`, `impact`, `list_gaps`, and `check_sync`

The approved Viewer 2 designs are the implementation reference for presentation and interaction. Do not simplify Viewer 2 back into the older prototype where doing so conflicts with those designs. Visual source: `design-docs/design-references/SpecPlane viewer design (5).zip`, canvas `Viewer v2.dc.html`.

### 1. Preserve the three top-level lenses

Top-level navigation remains **Live · Changes · Gaps**.

Do not add System / Product / Quality / Governance / Ownership to the navbar. Do not add Architecture, Journeys, Components, QA, Compliance, Security, Ownership, or other stakeholder homes.

### 2. Selected ID is the primary interaction object

Within Live, the default index may be capabilities, but a selected SpecPlane ID is the fundamental viewer object.

A rich capability page should follow the approved Viewer 2 design. Its job is to help a human understand: what this thing is, what it promises, how that promise is realized, what is changing, how it relates to the rest of the system, how users and information move through it, how success or correctness is judged, and what remains unknown.

Thin records show less. Rich records show more. Do not manufacture empty sections.

### 3. Preserve the rich capability hierarchy

Implement the Viewer 2 hierarchy. Where the payload supports them, preserve: identity / bit / review state; purpose / promise; active change; visual projection workspace; PM Definition; Promise → realization; Engineering Realization; open questions / gaps; source / provenance.

PM and Engineering are progressive layers of the same capability, not modes or persona views. Engineering material rolled up from realizing components must retain provenance. `component.billing_api · acceptance_criteria` must not visually become a criterion declared directly by `capability.billing`.

### 4. Implement the approved visual projection switcher

Where the payload supports them, projections may include **Map · Blast · Layers · Journey · Diagrams · Data**. Only show projections that have meaningful content. Do not show empty tabs. Do not stack all diagrams vertically. One projection is active at a time. They answer different structural questions about the same selected object.

GB 2026-09-25: Layers stays. Sequence is not its own projection. Diagrams is the overarching place for the diagrams a record holds, and a sequence is one of those diagrams.

| Projection | Question it answers |
|---|---|
| Map | Contextual neighborhood, realization, and dependencies around the selected id |
| Blast | Explainable affected subgraph from kernel `impact` |
| Layers | The same neighborhood placed on the 5C axis around the selected id |
| Journey | User, business, or system flow when represented. Keep branching, recovery, endings, missing steps, and epistemic distinctions the payload supports |
| Diagrams | Declared diagrams the record holds or needs, including sequence diagrams and other Mermaid. The list names each diagram’s type and cycles through them. Participants that resolve to ids are navigable. Do not silently reconcile a disagreement between a declared diagram and the modeled graph or flow. Surface it |
| Data | Data, entity, or schema relationships when represented. A referenced-but-unmodeled entity stays unknown / not represented |

### 5. Visual provenance is first-class

Keep these visually distinct:

- **Declared** — explicitly in the specification
- **Derived** — deterministically generated from the SpecPlane graph
- **Inferred** — recovered or proposed from implementation or analysis
- **Not represented / unknown** — the model is incomplete here

A `?` means current understanding is incomplete. It does not mean broken, invalid, unsafe, or erroneous.

### 6. Blast has two axes

The primary switcher answers which representation of the selected object is on screen (Map / Blast / Layers / Journey / Diagrams / Data). Sequence is a diagram type inside Diagrams.

When Blast is active, a secondary control answers which concern is interrogating that same affected subgraph: **System · Product · Quality · Governance · Ownership**. Those controls are visually subordinate to the projection switcher. Use the approved Blast frames for placement. They are not navbar items or separate pages.

### 7. One impact model, multiple perspectives

The kernel already provides the affected subgraph and projectors. Do not implement five blast walkers.

```text
selected ID / change → impact resolver → affected subgraph → System / Product / Quality / Governance / Ownership
```

Switching perspective highlights, dims, or annotates the same graph. It does not replace it with five unrelated pictures.

### 8. Perspective semantics

- **System** — affected capabilities, systems, containers, components, foundations, and dependencies. Keep direct/transitive and declared/inferred distinctions.
- **Product** — affected promises, journeys/flows, requirements, constraints, success criteria, targets, metrics, and analytics relationships where represented.
- **Quality** — affected acceptance criteria, validation/test strategy, journeys/failure paths, contracts, sensors, evidence, and verification gaps where represented. Quality is a concern, not a human QA role.
- **Governance** — governed concerns the model actually represents. Do not claim “No compliance impact.” Prefer “No governance relationship identified in the current model.”
- **Ownership** — owners or teams where represented or deterministically supplied. No RACI. Keep ownership provenance. Missing ownership is “Ownership not represented,” not “No owner required.”

### 9. “Why affected?” is required

Selecting an affected node explains why it is in the subgraph, using the kernel path, reason, and provenance. Do not infer causality from visual proximity.

The Blast **picture** is hop columns from `impact.affected[].distance`: Selected · 1 hop · direct · 2 hops · Further (`distance >= 3`, expand in place). That layout is in scope. It is not a “model cannot say yet” item. Do not draw a second invented path. The remaining cannot-say list is in `decision.md`.

### 10. Change remains a first-class story

A design-time change must stay useful before code exists. The same change accumulates, rendering only what exists: why → promises / product intent → journeys / constraints → impact → PM criteria → engineering realization → acceptance / validation → implementation delta → evidence → unresolved drift. Not four review products. Not a Jira lifecycle. The viewer supports both “understand this thing” and “understand this proposed change.”

### 11. Source and provenance remain inspectable

The viewer is not the source of truth. Where available, expose source spec/path, relationship provenance, component/source record, declared diagram source, change source, and inferred origin where the kernel actually supports it. Raw YAML is not the primary experience.

### 12. Do not add AI to fill missing semantics

Viewer v1 stays deterministic and offline. If a design needs information the kernel payload does not provide, do not call an LLM, infer it in the frontend, walk YAML, build a parallel graph, or fabricate it. Record the mismatch as a kernel/payload gap and report: the desired interaction, the missing kernel information, and the smallest payload or kernel change required.

### 13. Use the finished designs

Implement the approved frames for the rich capability, projection switching, diagram handling, and multidimensional Blast. Do not redesign them from this prose. Stop at a missing-semantics boundary and report it.

### Completion test

A human can open a real SpecPlane project and, without reading YAML:

1. understand what a selected capability promises
2. distinguish PM definition from engineering realization while seeing their relationship
3. navigate the relevant visual projections
4. understand an in-flight change
5. inspect its affected subgraph
6. switch System / Product / Quality / Governance / Ownership where supported
7. select an affected object and understand why it is affected
8. distinguish declared, derived, inferred, and unknown
9. recognize where understanding is incomplete
10. inspect source/provenance when needed

Invariant: **one graph, one impact model, multiple projections and perspectives.**
