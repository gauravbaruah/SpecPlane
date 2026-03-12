# SpecPlane Schema v6.1.0 — README

**Progressive Disclosure Edition** — A systematic framework for designing software components that bridges design and implementation.

## Overview

v6.1.0 uses the **C4 model** (System → Container → Component) with a clear split between **Planning** (PM-owned) and **Implementation** (Design + Engineering). Start minimal and expand as the spec matures.

## Key Characteristics

| Aspect | v6.1.0 |
|--------|--------|
| **Model** | C4 (3 levels: system, container, component) |
| **File layout** | `system.*.yaml`, `containers/`, `components/<container>/` |
| **Progressive disclosure** | ✅ Start with `id`, `purpose`, `level`; add fields as needed |
| **Planning vs implementation** | ✅ Explicit two-phase flow |
| **Analytics vs observability** | ✅ Clear separation (business vs technical) |
| **Capabilities** | ❌ Not in scope |
| **Foundations** | ❌ Not in scope |

## File Organization

```
specs/
├── system.<system_name>.yaml
├── containers/
│   ├── container.<container_name>.yaml
│   └── ...
└── components/
    └── <container_name>/
        ├── component.<component_name>.yaml
        └── ...
```

## Core Schema Sections

### Meta (required)

- `id` — Must match filename without extension
- `purpose` — One-sentence business value
- `level` — `system` | `container` | `component`
- Optional: `owner`, `tags`, `status`, `type`, `domain`

### C4 Architecture (level-specific)

- **System**: `system_context`, `relationships.contains` (containers)
- **Container**: `container_architecture`, `relationships` (contains, depends_on, used_by)
- **Component**: Full planning + implementation sections

### Phase 1: Planning (PM focus)

- `user_flows` — Actions, success, errors
- `analytics` — Success metric, target, product events (Mixpanel/Amplitude)
- `integrations` — Third-party SDKs, APIs, services

### Phase 2: Implementation (Design + Engineering)

- `interface` — Capabilities, inputs, outputs, side effects
- `contracts` — APIs, events, states, data models
- `dependencies` — Internal (SpecPlane IDs) and external
- `observability` — Metrics, logs, traces, SLIs/SLOs, alerting
- `constraints` — Performance, security, technical
- `validation` — Acceptance criteria, edge cases, assumptions

### Refs

Central resource registry for designs, tickets, docs, images, videos. Use `{{refs.<id>.<field>}}` in diagrams.

## When to Use v6.1.0

- **Teams** using C4 and no capability/foundation layer
- **Projects** where planning (PM) and implementation (engineering) are clearly separated
- **Workflows** that want progressive disclosure and minimal starting footprint
- **Non–AI-heavy** systems (no first-class agents, tools, or workflows)

## Quality Indicators

- Clear, measurable acceptance criteria
- Comprehensive error handling scenarios
- Realistic performance constraints
- Observable metrics and events with alerting
- Language-agnostic behavioral contracts
- Connected to design artifacts and tickets via `refs`

## Related Files

- **Schema prompt**: `specplane_schema_prompt_v6.1.0_progressive_disclosure.md`
- **Examples**: `spec_validation_prompt_examples.md`, `widget_spec_examples.md`
