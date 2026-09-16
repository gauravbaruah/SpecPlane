---
section: 03-shared-meta
canonical: ../specplane_schema_prompt_v9.1.0.md
---

# Applicable: Shared meta block, changelog, versioning, and review_state

Load this file for the task in the [loading contract](README.md). Do not load the full master prompt unless you are changing the schema itself or the user asks for the complete reference.

Canonical source: `../specplane_schema_prompt_v9.1.0.md` (same content, one file).

---

## 📐 Complete Schema Structure

### Shared Meta Block (all spec types)

All specs begin with the same `meta` block and `changelog`. Per-level differences are in the callout table below.

```yaml
meta:
  id: ""              # Required: must match filename without extension
                      # e.g., "capability.authentication", "foundation.design_system"
  purpose: ""         # Required: one sentence describing what this spec defines
  level: ""           # Required: capability | foundation | system | container | component
  owner: ""           # Team or person responsible
  tags: []
  last_updated: "YYYY-MM-DD"
  status: ""          # See per-level values below
  version: ""         # Semver MAJOR.MINOR.PATCH — see versioning rules (Validation Rule 9)
  review_state: ""    # See per-level values below
  introduced_in: ""   # Semver at which this spec was first created (e.g., "1.0.0")
                      # Set once on creation; never changed. Enables CI to compute "spec age"
                      # and surface how far behind consumers are relative to current version.
  deprecated_in: ""   # Semver at which this spec was deprecated (e.g., "3.0.0")
                      # Required when status: "deprecated". Together with introduced_in,
                      # CI can enforce "deprecated for N major versions — migration required."
  replaced_by: ""     # Only when status: "deprecated" — meta.id of the spec that supersedes this one
                      # e.g., "component.auth_service_v2" or "foundation.security_baseline_v2"
  migration_notes: "" # Only when status: "deprecated" or changelog has breaking: true
                      # Plain-text standing instruction for consumers arriving at this spec cold
                      # e.g., "Replace uses: [foundation.design_system] with uses: [foundation.design_system_v2]; update all color tokens to semantic aliases"

changelog:
  - date: "YYYY-MM-DD"
    author: ""
    summary: ""       # e.g., "Added Token refresh flow; tightened PKCE constraint"
    breaking: false   # true if this change alters public contracts, responsibilities, or interfaces
```

**Per-level differences:**

| Field | capability | foundation | system / container / component |
|---|---|---|---|
| `status` | `planned\|in_progress\|launched\|deprecated` | `draft\|active\|deprecated\|archived` | `draft\|active\|deprecated\|archived` |
| `review_state` | `unreviewed\|pm_approved\|eng_approved\|legal_reviewed\|shipped` | `unreviewed\|approved\|deprecated` | `unreviewed\|pm_approved\|eng_approved\|legal_reviewed\|shipped` |
| `type` | — (not used) | — (not used) | `component\|widget\|service\|agent\|tool\|workflow\|tool_registry\|state_store\|evaluator\|container\|system` |
| `domain` | — (not used) | — (not used) | `frontend\|backend\|mobile\|infrastructure\|ai\|data\|ai_native` |

**`version` semantics per level:**
- **capability:** MAJOR = breaking change to responsibilities, flows, or constraints
- **foundation:** MAJOR = renamed field, removed rule, or changed convention
- **component/container:** MAJOR = breaking interface change (renamed/removed input, output, or API contract)
- All levels: MINOR = additive; PATCH = correction or clarification

**`review_state` semantics:**
- `unreviewed` → freshly created, not yet reviewed
- `pm_approved` → PM has signed off on scope and business value
- `eng_approved` → Tech Lead has confirmed feasibility and architecture fit
- `legal_reviewed` → Legal/Compliance has reviewed (required when constraints include legal or security)
- `shipped` → Live in production; spec reflects actual behaviour
- `approved` *(foundation only)* → Reviewed and accepted as the active standard
