---
section: 04-capability
canonical: ../specplane_schema_prompt_v9.1.0.md
---

# Applicable: Capability spec schema (PM-owned Phase 1–3)

Load this file for the task in the [loading contract](README.md). Do not load the full master prompt unless you are changing the schema itself or the user asks for the complete reference.

Canonical source: `../specplane_schema_prompt_v9.1.0.md` (same content, one file).

---

### Capability Spec (level: "capability")

Progressive disclosure:
- Phase 1 (PM-owned, required): `meta` + `responsibilities` + `flows` + `business_value` + `constraints`
- Phase 2 (optional): + `success_metrics` + `roadmap`
- Phase 3 (engineering-added): + `realized_by`

A capability spec is valid and useful from Phase 1 alone.

```yaml
# (meta + changelog — see Shared Meta Block above)

# ── PHASE 1: PM-OWNED (Required) ───────────────────────────────────

# Semantic boundary — what this capability owns end-to-end
# Think of this as the answer to: "What is this capability responsible for?"
responsibilities:
  - ""    # e.g., "Identity verification"
          # e.g., "Session establishment and token lifecycle"
          # e.g., "Consent capture and legal record"
          # e.g., "Logout and revocation"

# What user flows this capability covers.
# Each item may be a string (an index name) or a mapping. Strings remain valid.
# A mapping requires a non-empty id. goal and the other keys are optional.
# Mappings are optional richness — not every file needs journey + lifecycle + information.
# A complete user journey may cross capabilities; this file holds the pieces it owns.
# Use skill specplane-flows to enhance mappings and raise open_questions (do not invent answers).
flows:
  - ""    # e.g., "Sign-up" — string index is enough for Phase 1
  # - id: invite_member
  #   kinds: [journey, lifecycle]   # omit any kind this file does not need
  #   goal: "Add another person to a workspace"
  #   actors:
  #     primary: workspace_owner
  #     secondary: [invited_user]
  #   stories:                      # lens / evidence — not a Jira list
  #     - actor: workspace_owner
  #       intent: "invite a colleague"
  #       outcome: "invitation is issued"
  #   entry:
  #     trigger: "owner chooses to invite"
  #     preconditions: ["authenticated"]
  #   stages: [discover, invite, pending, accept_or_decline]
  #   outcomes:
  #     success: ["membership established"]
  #     abandonment: ["invite cancelled"]
  #   lifecycle:
  #     creates: [invitation, membership]
  #     mutates: [invitation]
  #     terminates: [invitation]
  #     states: [pending, accepted, declined, expired, revoked]
  #     terminal_states: [accepted, declined, expired, revoked]
  #   information:
  #     collected: [invitee_email]
  #     moved: [invitation_email]
  #     retained_until: "membership established or invite terminal"
  #     destroyed_when: "invitation terminal and not accepted"
  #   exceptions: [existing_member, invalid_address, inviter_loses_permission]
  #   recovery: [resend, revoke, reinvite]

# Optional product-level uncertainty (same item shape as component validation.open_questions).
# Prefer generated questions from specplane-flows over silently filling gaps.
open_questions: []
  # - "Do invitations expire?"
  # - id: oq_invite_expiry
  #   question: "Do invitations expire?"
  #   raised_from: "flow.invite_member"
  #   status: "open|deferred|resolved|rejected"

# Business value — why this capability exists
business_value:
  user_outcome: ""      # Required: what the user can now do
  objective: ""         # Required: which business goal this serves
  revenue_dependency: "high|medium|low"
  strategic_priority: "core|growth|efficiency|foundation"
  # core        → the product cannot function without it
  # growth      → drives user acquisition or expansion
  # efficiency  → reduces cost or improves operations
  # foundation  → enables other capabilities but not user-facing alone

# Cross-cutting constraints owned by this capability
# These inform which components must handle what — without prescribing how
constraints:
  legal: []       # e.g., "GDPR consent required before account creation"
  security: []    # e.g., "PKCE required for OAuth flows"
  ux: []          # e.g., "Explicit consent gate must block account creation until accepted"
  data_classification: "public|internal|confidential|regulated"
  # public       → no access controls required; safe to expose externally
  # internal     → employees and authenticated users only
  # confidential → restricted access; PII, credentials, business-sensitive data
  # regulated    → subject to external regulation (GDPR, HIPAA, PCI-DSS, SOC2, etc.)
  #                When set to "regulated", compliance pack validation activates if a pack is loaded.
  #                This field is the compliance pack trigger — pack-specific fields
  #                (audit_required, retention_policy_ref, regulatory_mappings) live in the pack.

# ── PHASE 2: OPTIONAL (PM + Stakeholders) ──────────────────────────

# Analytics events — only when using product analytics (uses: foundation.analytics_conventions)
# What product events matter for this capability; components in realized_by emit these.
# See foundation.analytics_conventions for naming, ownership model, and single-source-of-truth rule.
analytics_events:
  - name: ""         # Event name (snake_case, e.g., login_attempted, snippet_marked_read)
    when: ""         # Trigger condition (e.g., "user submits login form", "snippet marked read")
    properties: []   # Key properties (e.g., source_id, mode, duration_ms)
    emitted_by: ""   # component meta.id that emits this event — exactly one per event (single-source-of-truth)

# How we know this capability is healthy — roll up from analytics_events
success_metrics:
  primary: ""        # The one KPI that proves this capability is working
  targets: {}        # Measurable targets, e.g.: {login_success_rate: ">99%"}
  derived_from: {}   # Optional when analytics_events exist — metric name → event names that feed it
                     # e.g., {login_success_rate: ["login_attempted", "login_succeeded"]}

# Roadmap context — human-filled; system does not auto-populate or act on these
roadmap:
  phase: ""           # e.g., "Q1 2026", "v1.0 launch", "Sprint 23"
  priority: ""        # e.g., "P0", "must-have", "nice-to-have"
  depends_on: []      # Capability IDs that must exist before this one. Must not create a cycle — use enables for the reverse direction.
  enables: []         # Capability IDs that this capability unlocks

# ── PHASE 3: ENGINEERING-ADDED (Optional) ──────────────────────────

# What realizes this capability in the architecture
# Added by engineering when implementation is planned or underway
# A capability spec is complete and valid without this section
realized_by:
  containers: []    # container meta.ids that participate in this capability
  components: []    # component meta.ids that implement parts of this capability

# ── FUTURE ─────────────────────────────────────────────────────────
# blockers:       # To be defined — open questions, dependencies, risks

# ── SHARED (Optional, any phase) ───────────────────────────────────

refs: []          # Same structure as other specs — tickets, designs, research, docs

# Capability diagrams: prefer the end-to-end sequence or user journey
# This is the right home for cross-system flows that span multiple containers
diagrams:
  - type: "sequence|flowchart|user_journey"
    title: ""
    description: ""
    mermaid: |
      # Cross-system flow spanning multiple containers
      # e.g., User → WebApp → AuthProvider → API → WebApp
