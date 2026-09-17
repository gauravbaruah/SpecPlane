---
section: 02-file-layout
canonical: ../specplane_schema_prompt_v9.1.0.md
---

# Applicable: File organization, naming, and what counts as a capability

Load this file for the task in the [loading contract](README.md). Do not load the full master prompt unless you are changing the schema itself or the user asks for the complete reference.

Canonical source: `../specplane_schema_prompt_v9.1.0.md` (same content, one file).

---

## 📁 File Organization and Naming Conventions

### **Hierarchical Folder Structure**

```
specs/
├── capabilities/                             # Capability-level specifications
│   ├── capability.<capability_name>.yaml
│   └── ...
│
├── foundations/                              # Foundation-level specifications (NEW)
│   ├── foundation.<foundation_name>.yaml
│   └── ...
│
├── system.<system_name>.yaml                 # System-level specification
│
├── containers/                               # Container-level specifications
│   ├── container.<container_name>.yaml
│   └── ...
│
├── components/                               # Component specifications
│   ├── <container_name>/
│   │   ├── component.<component_name>.yaml
│   │   └── ...
│   └── <another_container>/
│       └── ...
│
└── changes/                                  # In-flight write path (not 5C)
    └── <change_id>/
        ├── proposal.yaml
        ├── delta.yaml
        ├── success.yaml
        └── decision.md                       # only if a human must choose
```

`validate` skips path parts named `changes`. Live capabilities stay small; in-flight narrative lives on the change object. Promote into live YAML after the human accepts, then archive under `specs/changes/_archive/`.

### **Complete Example Structure**

```
specs/
├── capabilities/
│   ├── capability.authentication.yaml
│   ├── capability.data_analytics.yaml
│   └── capability.onboarding.yaml
│
├── foundations/
│   ├── foundation.design_system.yaml          # Design & UI
│   ├── foundation.component_library.yaml
│   ├── foundation.iconography.yaml
│   ├── foundation.motion.yaml
│   ├── foundation.api_conventions.yaml        # API & Data
│   ├── foundation.data_model_conventions.yaml
│   ├── foundation.event_schema.yaml
│   ├── foundation.error_handling.yaml         # Cross-cutting Technical
│   ├── foundation.logging_conventions.yaml
│   ├── foundation.security_baseline.yaml
│   ├── foundation.performance_budget.yaml
│   ├── foundation.accessibility.yaml          # Compliance & UX
│   ├── foundation.internationalization.yaml
│   ├── foundation.privacy_consent.yaml
│   ├── foundation.ai_guidelines.yaml          # AI-Native
│   ├── foundation.model_governance.yaml
│   ├── foundation.eval_standards.yaml
│   ├── foundation.analytics_conventions.yaml  # Analytics & Observability
│   └── foundation.observability_standards.yaml
│
├── system.saas_platform.yaml
│
├── containers/
│   ├── container.web_app.yaml
│   ├── container.api_gateway.yaml
│   ├── container.agentic_backend.yaml
│   ├── container.data_model.yaml
│   └── container.evaluations.yaml
│
└── components/
    ├── web_app/
    │   ├── component.login_form.yaml
    │   ├── component.consent_capture.yaml
    │   └── component.dashboard.yaml
    ├── api_gateway/
    │   ├── component.auth_api.yaml
    │   ├── component.token_service.yaml
    │   └── component.session_store.yaml
    └── agentic_backend/
        ├── component.analysis_workflow.yaml
        └── component.tool.fetch_series.yaml
```

### **Agentic Backend Layout**

AI-native applications typically use three peer containers alongside the main application containers:

```
specs/
├── containers/
│   ├── container.agentic_backend.yaml      # Agent runtime: agents, workflows, tools, observability
│   ├── container.data_model.yaml           # Schemas and persistence definitions
│   └── container.evaluations.yaml          # Eval harness: invariants, datasets, scorers
│
└── components/
    ├── agentic_backend/
    │   ├── component.<name>_agent.yaml              # meta.type: "agent"
    │   ├── component.<name>_workflow.yaml           # meta.type: "workflow"
    │   ├── component.tool.<name>.yaml               # meta.type: "tool"
    │   ├── component.tool.<name>_registry.yaml      # meta.type: "tool_registry"
    │   └── component.<name>_state_service.yaml      # meta.type: "state_store"
    ├── data_model/
    │   └── component.<collection>_collection.yaml
    └── evaluations/
        ├── component.<name>_invariants.yaml         # meta.type: "evaluator" (eval_type: invariant)
        ├── component.<name>_dataset.yaml            # meta.type: "evaluator" (eval_type: dataset)
        ├── component.<name>_scorer.yaml             # meta.type: "evaluator" (eval_type: scorer)
        └── component.<name>_sim_generator.yaml      # meta.type: "evaluator" (eval_type: sim_generator)
```

### **What Makes Something a Capability?**

A capability is a **cross-cutting business concern** — it spans multiple containers or components, is owned by the product team, and represents a product-level commitment to users or stakeholders.

✅ **Capabilities:**
- Authentication (spans frontend + backend + external auth provider)
- Data analytics (spans agentic backend + data model + API)
- Onboarding (spans web app + email service + API)
- Payments (spans frontend + payments API + webhooks)
- Notifications (spans push, email, in-app across containers)

❌ **NOT Capabilities (these are components or containers):**
- Login form — this is a *component* that *implements* the authentication capability
- Auth API — this is a *component* inside the api_gateway container
- The database — this is a *container* (data_model)

**Key Question**: "Is this something the product promises to users, spanning multiple parts of the system?"
- Yes → Capability
- No → Container or Component

### **Naming Convention**

`<level>.<name>.yaml` — `meta.id` must exactly match the filename without extension.

| Spec type | Filename pattern |
|---|---|
| Capability | `capability.<name>.yaml` |
| Foundation | `foundation.<name>.yaml` |
| System | `system.<name>.yaml` |
| Container | `container.<name>.yaml` |
| Component | `component.<name>.yaml` |
| Tool | `component.tool.<name>.yaml` |

See Validation Rules 1–2 for enforcement examples.
