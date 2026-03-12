# SpecPlane Schema v9.1.0 — README

**5C Model + Capability-First + Foundations** — A systematic framework for designing software at every level of abstraction, from business intent to deployed components.

## Overview

v9.1.0 extends C4 with **Capability** and **Foundation** layers. It supports **capability-first** design (business value before architecture), **foundations** as shared standards, and **AI-native** components (agents, tools, workflows, evaluators).

## Key Characteristics

| Aspect | v9.1.0 |
|--------|--------|
| **Model** | 5C: Capability → System → Container → Component → Code |
| **File layout** | `capabilities/`, `foundations/`, `system.*.yaml`, `containers/`, `components/<container>/` |
| **Capability-first** | ✅ Business value modeled before any container/component |
| **Foundations** | ✅ Cross-cutting specs (design system, API conventions, security, AI guidelines, etc.) |
| **AI-native** | ✅ Agents, tools, workflows, tool registries, state stores, evaluators |
| **Two axes** | Structural (C4) + value (Capability) |
| **Versioning & review** | `version`, `review_state`, `changelog`, `introduced_in`, `deprecated_in` |

## File Organization

```
specs/
├── capabilities/
│   └── capability.<name>.yaml
├── foundations/
│   ├── foundation.design_system.yaml
│   ├── foundation.api_conventions.yaml
│   ├── foundation.security_baseline.yaml
│   ├── foundation.ai_guidelines.yaml
│   └── ...
├── system.<system_name>.yaml
├── containers/
│   ├── container.<container_name>.yaml
│   └── ...
└── components/
    └── <container_name>/
        ├── component.<component_name>.yaml
        ├── component.tool.<name>.yaml
        └── ...
```

## The 5C Model

- **Capability** — Cross-cutting business concern, PM-owned, spans multiple containers/components
- **System** — System boundaries and actors (C4 Level 1)
- **Container** — Deployable units (C4 Level 2)
- **Component** — Logical building blocks (C4 Level 3)
- **Code** — Implementation (outside SpecPlane)

Capabilities and C4 are **two axes**: one capability can span many containers/components; one component can implement multiple capabilities.

## Spec Types and Ownership

| Spec type | Owned by | Key question |
|-----------|----------|--------------|
| **Capability** | PM | Why does this exist? What business value? |
| **Foundation** | Cross-cutting | What rules apply everywhere? |
| **System / Container** | Architecture | Where does this run? |
| **Component** | Engineering | What does it do and how well? |

## Core Schema Sections

### Shared meta block (all spec types)

- `id`, `purpose`, `level`, `owner`, `tags`, `status`, `version`
- `review_state` — `unreviewed` | `pm_approved` | `eng_approved` | `legal_reviewed` | `shipped`
- `introduced_in`, `deprecated_in`, `replaced_by`, `migration_notes`
- `changelog` — date, author, summary, breaking

### Capability spec

- `responsibilities`, `flows`, `business_value`, `constraints`
- Optional: `analytics_events`, `success_metrics`, `roadmap`
- Engineering-added: `realized_by` (containers/components that implement the capability)

### Foundation spec

- Shared standards referenced by components via `uses: [foundation.<name>]`
- Foundations declare `used_by` for traceability

### Component spec

- `implements` — Links to capability specs
- `uses` — Links to foundation specs
- Full contracts, observability, validation, and constraints

## Agentic backend layout

AI-native apps typically add:

- **container.agentic_backend** — Agents, workflows, tools, observability
- **container.data_model** — Schemas and persistence
- **container.evaluations** — Invariants, datasets, scorers, sim generators

Component types: `agent`, `workflow`, `tool`, `tool_registry`, `state_store`, `evaluator`.

## When to Use v9.1.0

- **Product-led** teams that want capability-first design
- **Organizations** needing shared foundations (design system, security, API conventions)
- **AI-native** systems with agents, tools, and workflows
- **Regulated** or **compliance-sensitive** environments (foundations, review_state, changelog)
- **Cross-functional** ownership (PM, engineering, compliance, legal)

## Quality Indicators

- Capability specs complete before architecture
- Components declare `implements` and `uses`
- Clear `review_state` and `changelog`
- Analytics (PM) vs observability (engineering) clearly separated
- Language-agnostic behavioral contracts
- Refs used in diagrams have resolvable `url` or `path`
- Consistent identifiers (snake_case) across analytics, observability, and contracts
- Analytics events include `properties` for contract-test generation

## Related Files

- **Schema prompt**: `specplane_schema_prompt_v9.1.0.md`
- **Foundations**: `specplane/foundations/*.yaml`
- **Examples**: `spec_validation_prompt_examples.md`, `widget_spec_examples.md`
