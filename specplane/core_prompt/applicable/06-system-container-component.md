---
section: 06-system-container-component
canonical: ../specplane_schema_prompt_v9.1.0.md
---

# Applicable: System, container, and component specs: implements, uses, planning, implementation

Load this file for the task in the [loading contract](README.md). Do not load the full master prompt unless you are changing the schema itself or the user asks for the complete reference.

Canonical source: `../specplane_schema_prompt_v9.1.0.md` (same content, one file).

---

# ============================================
# SYSTEM / CONTAINER / COMPONENT SPEC
# ============================================

# (meta + changelog — see Shared Meta Block above; add type and domain fields per the table)

# ── VALID level + type COMBINATIONS ────────────────────────────────
# level: "capability"   → no type or domain field
# level: "foundation"   → no type or domain field
# level: "system"       → type: "system"
# level: "container"    → type: "container"
# level: "component"    → type: one of:
#
#   Non-AI types (no ai_config block):
#     component     Generic logical unit. Use when the piece doesn't fit widget or service —
#                   e.g., a state manager, a route guard, a data transformer.
#     widget        A self-contained UI element rendered in the frontend.
#                   Use when domain is "frontend" and the unit has its own visual contract.
#     service       A backend unit with its own lifecycle, API surface, or data ownership.
#                   Use when the unit is independently deployable or has clear API boundaries.
#
#   AI-native types (require ai_config block):
#     agent         → requires ai_config (role, tools, memory, handoffs)
#     tool          → requires ai_config (computation_type, output_contract, call_sites)
#     workflow      → requires ai_config (pattern, nodes, edges, state_schema)
#     tool_registry → requires ai_config (provides_discovery, mcp_compatible)
#     state_store   → requires ai_config (persistence, access_pattern)
#     evaluator     → requires ai_config (eval_type, target, scoring_method, threshold)
# ───────────────────────────────────────────────────────────────────

# ── NEW in v9.0.0 ──────────────────────────────────────────────────
# Declare which capabilities this container or component implements.
# Added by engineering when realized_by is populated in the capability spec.
# A component may implement more than one capability.
# Bidirectional: adding a capability ID here REQUIRES adding this component's ID to realized_by.components in the capability spec.
implements:
  - ""    # e.g., "capability.authentication"
          # e.g., "capability.onboarding"

# Declare which foundations this container or component builds on.
# Used for traceability: find all components affected by a foundation change.
# Bidirectional: adding a foundation ID here REQUIRES adding this component's ID to used_by.components in the foundation spec.
uses:
  - ""    # e.g., "foundation.design_system"
          # e.g., "foundation.api_conventions"
          # e.g., "foundation.accessibility"

# ============================================
# REFS - Central Resource Registry
# ============================================
# For refs used in diagrams ({{refs.<id>.<field>}}): url or path must be non-empty
# so the reference is resolvable. External resources use url; local files use path.
refs:
  - id: ""
    type: "design|ticket|doc|image|video|dataset|api|prompt|spec|incident|postmortem|other"
    # prompt     → system prompts, BAML functions, output schemas
    # spec       → links to another SpecPlane spec file (including capability specs)
    # incident   → links to a production incident that informed or changed this spec
    # postmortem → links to a post-mortem action item that resulted in a spec change
    title: ""
    url: ""
    path: ""
    owner: ""
    version: ""
    status: "active|deprecated|archived"
    last_updated: "YYYY-MM-DD"
    access: "public|internal|restricted"
    tags: []
    notes: ""
    related_refs: []
    width: 0
    height: 0
    start_time: "0:00"
    duration: "0:00"

# ============================================
# C4 ARCHITECTURE (Level-Specific)
# ============================================

# ─────────────────────────────────────────
# When level="system"
# ─────────────────────────────────────────
system_context:
  actors: []
  external_systems: []
  system_boundaries: []
  capabilities: []    # ← NEW: capability meta.ids this system enables
                      # e.g., ["capability.authentication", "capability.data_analytics"]

relationships:
  contains: []
  integrates_with: []

# ─────────────────────────────────────────
# When level="container"
# ─────────────────────────────────────────
container_architecture:
  type: ""            # Recognized types: "agentic_backend" | "data_model" | "evaluations"
  technology_stack: []
  deployment_unit: ""
  data_stores: []
  communication: []

relationships:
  contains: []
  depends_on: []
  used_by: []
  integrates_with: []

# ─────────────────────────────────────────
# When level="component"
# ─────────────────────────────────────────
# Full planning + implementation sections below

# ============================================
# PHASE 1: PLANNING (PM Focus)
# ============================================
planning:
  user_flows:
    actions: []
    success: []
    errors: []

  analytics:
    # ── ANALYTICS vs OBSERVABILITY — where does an event belong? ───────
    # analytics   → business intent; answers PM questions; goes to Mixpanel, Amplitude, warehouse
    #               WHO did WHAT and did the product goal succeed?
    #               e.g., login_attempted, checkout_started, feature_adopted
    # observability → system health; answers engineering questions; goes to Datadog, Grafana, PagerDuty
    #               IS THE SYSTEM WORKING? latency, error rate, saturation
    #               e.g., auth_latency_ms, db_query_duration_ms, error_rate
    #
    # An event can be BOTH. login_attempted is an analytics event (PM tracks success rate)
    # AND can emit a trace span (engineer tracks latency). Put it in analytics if the PM
    # owns the question; put a corresponding metric/trace in observability if engineering owns it.
    # Do NOT duplicate the same event definition in both sections — reference, don't repeat.
    # ────────────────────────────────────────────────────────────────────
    #
    # When using foundation.analytics_conventions: single-source-of-truth applies — each event
    # emitted exactly once by the owning component. Events here match capability.analytics_events.
    success_metric: ""      # Link to capability success_metrics.primary this component contributes to
    target: ""
    default_destinations: []
    events:
      - name: ""            # Match capability.analytics_events[].name when implementing that capability
        when: ""
        properties: {}
        destinations: []

  integrations:
    - name: ""
      purpose: ""
      type: "sdk|api|service"
      version: ""
      provider: ""
      docs_url: ""

# ============================================
# PHASE 2: IMPLEMENTATION (Design + Engineering Focus)
# ============================================
implementation:
  interface:
    capabilities: []
    inputs: []
    outputs: []
    side_effects: []

  contracts:
    apis: []
    events: []
    states: []
    data_models: {}

  dependencies:
    internal: []    # component meta.ids this component depends on
                    # Bidirectional: adding a component ID here REQUIRES adding this component's ID
                    # to depended_on_by.components in the target component's spec.
    external: []    # Named external services, SDKs, or APIs (not SpecPlane specs)

  depended_on_by:
    components: []  # component meta.ids that list this component in their dependencies.internal
    containers: []  # container meta.ids that list this component in their relationships.depends_on
    # Bidirectional: adding an ID here REQUIRES that spec to list this component in its
    # dependencies.internal (for components) or relationships.depends_on (for containers).
    # Used by CI to answer: "If this spec changes, what else breaks?"

  observability:
    # ── OBSERVABILITY scope ──────────────────────────────────────────────
    # Engineering-owned signals: latency, error rates, saturation, system events.
    # If it answers "is the system working?" it lives here.
    # If it answers "did the user achieve their goal?" it lives in planning.analytics.
    # Use correlation.join_key to link a technical trace to its analytics counterpart
    # (e.g., attach request_id to both the trace span and the analytics event).
    # ────────────────────────────────────────────────────────────────────
    metrics: []
    logs: []
    traces: []
    slis: []
    slos: []
    alerting:
      critical: []
      warning: []
    business_impact:
      primary_metric: ""    # The one PM metric this component most affects (link to analytics)
      dashboard_ref: ""     # Link to the product dashboard that surfaces this metric
      success_criteria: ""  # When is this component "healthy" in business terms?
    correlation:
      join_key: ""  # Shared key that joins traces to analytics events (e.g., "request_id")
      note: ""      # e.g., "Attach request_id to both auth_flow trace and login_attempted event"

  technical_constraints:
    performance:
      response_time: ""
      throughput: ""
      availability: ""
      scalability: ""
      concurrent_users: ""
    security:
      authentication: ""
      authorization: ""
      data_protection: ""
      data_classification: "public|internal|confidential|regulated"  # Must match or be stricter than the parent capability's data_classification
      compliance: ""        # Free-text note (e.g., "GDPR, SOC 2 Type II"). Machine-readable compliance fields live in compliance packs.
      threats: []
      mitigations: []
      data_retention: ""    # Retention period or policy name (e.g., "90 days", "per GDPR Article 5(1)(e)")
    technical:
      compatibility: ""
      accessibility: ""
      internationalization: ""

  validation:
    acceptance_criteria: []
    edge_cases: []
    assumptions: []
    readiness: "ready|blocked|unknown"
    open_questions: []
    test_strategy:
      unit: ""          # Key behaviors to cover (e.g., ">90% on business logic, all error branches")
                        # Presence implies required — CI treats non-empty as "run unit tests"
      integration: ""   # Key integration paths (e.g., "auth flow with token_service and session_store")
                        # Presence implies required — CI treats non-empty as "run integration tests"
      e2e: ""           # Critical user journeys; link to Playwright/Cypress (web) or Maestro (Flutter/mobile) spec files
                        # Presence implies required — CI treats non-empty as "run E2E tests"
      performance: false  # Set true for latency-sensitive or high-throughput components
                          # Cannot be inferred from prose — this is the explicit load/perf test gate
      # Security test requirement is inferred from data_classification — no separate flag needed:
      # data_classification: "confidential" or "regulated" → CI requires security testing
      # Note: contract_testing, chaos_testing, accessibility_testing live in the QA Pack extension.

  rollout:
    strategy: "immediate|blue_green|canary|feature_flag|dark_launch"
    # immediate   — deploy all-at-once; fast but no blast-radius control
    # blue_green  — full traffic switches after parallel env validates; zero-downtime swap
    # canary      — incremental traffic shift; requires SLO monitoring to auto-advance/rollback
    # feature_flag — ship to prod dark; flag gates exposure; decouples deploy from release
    # dark_launch  — same as feature_flag but traffic mirrors to new path without user-visible effect
    feature_flag: ""   # Required when strategy: "feature_flag" or "dark_launch"
                       # Must be the flag key as it appears in your flag management system
                       # (LaunchDarkly, Unleash, Statsig, etc.)
    rollback_trigger: ""  # Condition that triggers automated rollback
                          # Link to an observability SLO for machine-readable enforcement
                          # e.g., "error_rate > 1% sustained for 5min" or "p99_latency > 2s"
    # Note: per-environment config, traffic-split percentages, and flag variants
    # belong in the DevOps Pack extension — this captures intent and strategy only.
