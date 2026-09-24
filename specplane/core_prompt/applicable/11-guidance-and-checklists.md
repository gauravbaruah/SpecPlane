---
section: 11-guidance-and-checklists
canonical: ../specplane_schema_prompt_v9.1.0.md
---

# Applicable: Interactive guidance commands, do/don't, quality checklists

Load this file for the task in the [loading contract](README.md). Do not load the full master prompt unless you are changing the schema itself or the user asks for the complete reference.

Canonical source: `../specplane_schema_prompt_v9.1.0.md` (same content, one file).

---

## 💡 Interactive Guidance Commands

### When user asks for help:

**Foundations:**
- "Add a foundation" → Identify category (Design/API/Technical/Compliance/AI/Analytics), copy boilerplate from specplane/foundations/, fill in values
- "Which foundation applies here?" → Match component needs to the 19 foundation types
- "Link a component to a foundation" → Add foundation ID to component's `uses` field and component ID to foundation's `used_by`
- "What's affected by this foundation change?" → Look up `used_by` to find all impacted containers and components
- "Add a design system" → Guide through foundation.design_system tokens (colors, typography, spacing)
- "Set up AI foundations" → Walk through ai_guidelines + model_governance + eval_standards as a trio
- "What foundations does a new project need?" → Recommend universal set: design_system, api_conventions, error_handling, accessibility, analytics_conventions

**Capabilities:**
- "Add a capability" → Guide through responsibilities, flows, business_value, constraints (Phase 1)
- "Map a capability to architecture" → Help populate realized_by with containers and components
- "Add success metrics to a capability" → Guide through primary metric and targets (Phase 2)
- "Build a capability roadmap" → Help populate roadmap.depends_on and enables
- "What should be a capability vs a component?" → Explain cross-cutting vs single-unit distinction
- "Show capability dependencies" → Draw the capability graph with depends_on / enables
- "Which components serve this capability?" → Trace realized_by → component specs
- "Why does this component exist?" → Look up implements to find the parent capability

**Structure & Organization:**
- "Review this spec" → Provide completeness checklist
- "Organize file structure" → Guide through folder hierarchy and naming
- "Fix naming convention" → Correct file naming and meta.id consistency
- "Set up agentic backend" → Walk through 3-container layout
- "Bump the version" → Determine MAJOR/MINOR/PATCH based on what changed; add changelog entry
- "Mark this spec as approved" → Guide through review_state progression for the spec's level
- "What changed in this spec?" → Summarise changelog entries in plain English
- "Is this a breaking change?" → Analyse contracts/APIs/interfaces; recommend breaking: true/false
- "Deprecate this spec" → Set status: "deprecated", populate replaced_by with the successor meta.id, write migration_notes for consumers
- "What replaced X?" → Look up replaced_by on deprecated spec; surface migration_notes
- "How old is this spec?" → Compute version delta between introduced_in and current version; flag if spec has been deprecated for more than one MAJOR version without consumer migration
- "What breaks if this spec changes?" → Read depended_on_by.components and depended_on_by.containers; trace to their capabilities via implements
- "Audit bidirectional links" → Check all four pairs: implements↔realized_by, uses↔used_by, dependencies.internal↔depended_on_by.components, relationships.depends_on↔depended_on_by.containers; flag any one-sided entries
- "Set data classification" → Guide through public|internal|confidential|regulated; remind that regulated triggers compliance pack validation and that all implementing components must match or exceed the capability's classification
- "Does this need a compliance pack?" → Check data_classification on capability and component specs; if "regulated", recommend loading the appropriate pack (GDPR, HIPAA, SOC2, PCI-DSS)

**Analytics & Traceability:**
- "Add analytics events" → Guide through capability.analytics_events (name, when, properties, emitted_by); ensure emitted_by matches a component in realized_by
- "Who emits this event?" → Check capability.analytics_events[].emitted_by; verify that component lists the event in planning.analytics.events
- "Roll up events to success metrics" → Populate success_metrics.derived_from with event names from analytics_events; ensure each event feeds at least one metric
- "Audit analytics traceability" → Verify single-source-of-truth (each event emitted by exactly one component); check roll-up (derived_from references existing events); flag orphan events or metrics

**Rollout & Release:**
- "Plan rollout for X" → Guide through strategy enum; ask if a feature flag is needed; link rollback_trigger to an existing SLO in observability
- "Add a feature flag" → Set strategy: "feature_flag", prompt for flag key name, warn if flag not yet created in flag management system
- "What's the rollback condition?" → Derive from observability.slos if defined; otherwise prompt for error_rate or latency threshold
- "Is this a breaking change for consumers?" → Check depended_on_by, then recommend canary or feature_flag strategy over immediate rollout

**C4 Architecture:**
- "Create system context" → Guide through C4 Level 1 including capabilities[]
- "Design container architecture" → Help with C4 Level 2
- "Should this be a container?" → Explain deployment unit criteria

**AI-Native Components:**
- "Add an agent" → Guide through role, tools, memory, output_contract
- "Add a workflow" → Walk through computation_model, nodes, edges, state_schema
- "Add a tool" → Guide through computation_type, output_contract, call_sites
- "Add a tool registry" → Explain the registry pattern, mcp_compatible flag
- "Set up the NodeContext pattern" → Guide through constrained_inputs on nodes
- "Define the computation model" → Help articulate orchestration / computation / structure split

**Planning & Design:**
- "Add user flows" → Capability: named index or optional mapping (journey / lifecycle / information). Component: actions, success, errors; optional `flow_ref`. Use specplane-flows to enhance; do not invent unanswered behavior.
- "Define analytics events" → Help structure product analytics tracking
- "Add monitoring" → Suggest metrics, SLOs, alerting
- "Is X analytics or observability?" → Apply the decision rule: PM dashboard question → analytics; engineer on-call question → observability; can be both with correlation.join_key linking them
- "Link analytics to observability" → Guide through correlation.join_key and business_impact fields
- "Add test strategy" → Guide through unit/integration/e2e intent; link to test files
- "What should I test here?" → Recommend test_strategy content based on contracts and edge_cases

**Visualization:**
- "Add sequence diagram" → Guide through interaction flow patterns
- "Visualize capability" → Create cross-system sequence or user journey for a capability
- "Show capability map" → Create mindmap or architecture diagram of all capabilities and their relationships
- "Add C4 diagrams" → Create system context (with capability overlay) or container diagram

**Resources & Traceability:**
- "Add design references" → Help create refs for Figma, Sketch files
- "Link project tickets" → Guide through Jira, ClickUp, GitHub issue refs
- "Add prompt references" → Create refs for BAML files, system prompts, output schemas
- "Link to another spec" → Add a refs entry with type: "spec"

---

## 🎓 Best Practices Summary

### **SpecPlane Philosophy in Action**

✅ **DO:**
- Start capabilities in Phase 1 — a spec with responsibilities, flows, business_value, and constraints is complete and useful
- Let engineering add `realized_by` when implementation is planned — don't block PM work on this
- Use `implements` on every component and container so the capability → architecture trace is bidirectional
- Put the cross-system sequence diagram in the capability spec, not in a container or component
- Use refs to link capabilities to tickets, research, and legal documents
- Keep the roadmap fields human-filled — capabilities express intent, not automation triggers

❌ **DON'T:**
- Create a capability for something that fits entirely inside one container (that's a component)
- Put `realized_by` in Phase 1 — it belongs to engineering, not early PM thinking
- Duplicate the cross-system flow diagram in every component (put it once in the capability spec)
- Confuse capability `flows` with component `user_flows` — capability flows are the value-axis pieces (string index or optional journey/lifecycle/information mapping); component flows are realization slivers (`actions` / `success` / `errors`, optional `flow_ref`)
- Mix business and technical concerns — constraints in the capability spec are *what*, not *how*

### **Quality Checklist**

Before marking a **capability** spec as `status: "launched"`:
- [ ] `meta` complete (id, purpose, level, owner, status, version)
- [ ] `meta.introduced_in` set to the version when this spec was first created
- [ ] `meta.review_state` is `pm_approved` at minimum; `legal_reviewed` if legal/security constraints present
- [ ] `responsibilities` clearly list what this capability owns end-to-end
- [ ] `flows` named (not just "login" but the full set: sign-up, refresh, logout, reset). Rich mappings are optional; not every file needs journey + lifecycle + information. A mapping requires a non-empty `id`.
- [ ] `business_value` has user_outcome AND objective
- [ ] `constraints` cover legal, security, and UX
- [ ] `success_metrics` has a primary metric (Phase 2)
- [ ] When product analytics matter: `analytics_events` defined, `derived_from` populated, `uses` includes foundation.analytics_conventions (Phase 2)
- [ ] `roadmap.depends_on` and `enables` populated (Phase 2)
- [ ] `realized_by` populated (Phase 3, engineering-added)
- [ ] `changelog` has at least one entry
- [ ] End-to-end sequence diagram in `diagrams`
- [ ] Refs link to relevant tickets and legal docs

Before marking a **foundation** spec as `status: "active"`:
- [ ] `meta` complete (id, purpose, level, owner, status, version)
- [ ] `meta.introduced_in` set to the version when this spec was first created
- [ ] `meta.review_state` is `approved`
- [ ] `provides` clearly lists what this foundation gives to consumers
- [ ] `used_by` populated (containers and components that reference this)
- [ ] Foundation-specific content fields filled in (not just placeholders)
- [ ] `extends` set if this foundation builds on another
- [ ] `changelog` has at least one entry
- [ ] Refs link to relevant external standards, tickets, or design documents

Before marking a **component or container** as `status: "active"`:
- [ ] `implements` field present with capability ID(s)
- [ ] `uses` field present with foundation ID(s) where applicable
- [ ] `meta` complete (id, purpose, level, owner, version)
- [ ] `meta.introduced_in` set to the version when this spec was first created
- [ ] `meta.review_state` is `eng_approved` at minimum
- [ ] File naming and location correct
- [ ] Behavioral contracts defined
- [ ] Observability instrumented (metrics, SLOs, alerting)
- [ ] Security constraints documented
- [ ] Acceptance criteria measurable
- [ ] `validation.test_strategy` filled in (unit, integration, e2e intent)
- [ ] Edge cases considered
- [ ] Assumptions listed
- [ ] `changelog` has at least one entry
- [ ] Relationships to other specs defined
- [ ] All bidirectional links verified: implements↔realized_by, uses↔used_by, dependencies.internal↔depended_on_by
- [ ] `rollout.strategy` set (not blank); `feature_flag` populated if strategy is `feature_flag` or `dark_launch`
- [ ] `rollout.rollback_trigger` links to an SLO or has an explicit condition

For **AI-native specs** (when meta.type is agent/tool/workflow/tool_registry/evaluator):
- [ ] `ai_config` section present with type-appropriate fields
- [ ] `computation_model` split defined (orchestration / computation / structure)
- [ ] Every AI node has an `output_contract` ref
- [ ] Nodes that select from finite sets use `constrained_inputs` (NodeContext pattern)
- [ ] Tool `computation_type` is accurate (compute vs ai_structured vs hybrid)
- [ ] Tool registries have `mcp_compatible` flag set
- [ ] `implementation_hints.ai` populated with framework, output_schema, model

---

**Remember**: SpecPlane specs should be **implementation-agnostic** but **detailed enough** to guide development across any technology stack.

Capability specs are **PM-first**: a capability spec is complete and useful from Phase 1 alone — before any architecture is decided. Engineering adds structure; PM adds value. SpecPlane holds both.

For AI-native components, make the **orchestration / computation / structure** split explicit, constrain AI outputs, and treat tool registries as first-class infrastructure.

The full traceability chain:
```
Capability → System → Container → Component → Observability → Analytics
    ↕               ↕                  ↕
review_state    changelog          test_strategy
(who approved)  (what changed)     (how it's verified)
```
That chain closes the PM ↔ Engineering ↔ QA ↔ Audit loop.
