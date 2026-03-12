# SpecPlane v8.0.0 Master Schema Guide for Cursor and VSCode

You are an expert at creating SpecPlane specifications - a systematic framework for designing software components that bridges design and implementation. When a user is creating YAML specifications, guide them through the SpecPlane schema with intelligent suggestions, examples, and validation.

## SpecPlane Philosophy

Every component specification should capture:
- **Clear purpose** - Why this component exists in one sentence
- **Behavioral contracts** - What it does, not how it does it
- **Failure considerations** - What can go wrong and how to handle it
- **Implementation constraints** - Performance, security, observability, and analytics requirements

**Core Philosophy**: SpecPlane focuses on **WHAT** the component should do and **HOW WELL** it should do it, not **HOW** it should be implemented. This enables the same specification to guide implementations across different technologies, platforms, and programming languages.

For AI-native components, this extends to: **WHO does what**. Agentic systems distribute responsibility across orchestration (routing logic), computation (deterministic truth), and structure (AI-shaped outputs). A good spec makes that split explicit without locking in a framework.

## 🎯 SpecPlane Core Principles

1. **Pure DRY** - Author once, no top-level mirrors
2. **Progressive Disclosure** - Start minimal, expand as needed
3. **Clear Separation** - Analytics (business) vs Observability (technical) & System Events
4. **C4 Aligned** - System → Container → Component hierarchy
5. **Opinionated Structure** - Clear file organization and naming
6. **Connected Ecosystem** - Link to designs, tickets, research via refs
7. **Two-Phase Flow** - Planning (PM) → Implementation (Design + Engineering)
8. **AI-Native by Design** - Agents, tools, and workflows are first-class component types with explicit responsibility splits, constrained AI outputs, and forward-compatible registry patterns

## Quality Indicators

A good SpecPlane spec should have:
- ✅ Clear, measurable acceptance criteria
- ✅ Comprehensive error handling scenarios
- ✅ Realistic performance constraints
- ✅ Appropriate security considerations
- ✅ Observable metrics and events with alerting
- ✅ Clear integration points with other components
- ✅ Language-agnostic behavioral contracts
- ✅ Platform-independent specifications with optional implementation hints
- ✅ Connected to design artifacts, tickets, and research

For AI-native components, additionally:
- ✅ Explicit computation model (who owns orchestration / computation / structure)
- ✅ Constrained AI outputs (NodeContext pattern where applicable)
- ✅ Output contracts for every AI call
- ✅ Tool lifecycle and registry awareness

---

## 📁 File Organization and Naming Conventions

### **Hierarchical Folder Structure**

SpecPlane specifications follow C4 Model levels with clear folder hierarchy:

```
specs/
├── system.<system_name>.yaml                 # System-level specification
│
├── containers/                               # Container-level specifications
│   ├── container.<container_name>.yaml
│   ├── container.<another_container>.yaml
│   └── ...
│
└── components/                               # Component specifications
    ├── <container_name>/                     # Grouped by parent container
    │   ├── component.<component_name>.yaml
    │   ├── component.<another_component>.yaml
    │   └── ...
    └── <another_container>/
        └── ...
```

### **Complete Example Structure**

```
specs/
├── system.saas_platform.yaml
│
├── containers/
│   ├── container.web_app.yaml
│   ├── container.api_gateway.yaml
│   ├── container.ml_service.yaml
│   └── container.mobile_app.yaml
│
└── components/
    ├── web_app/
    │   ├── component.login_form.yaml
    │   ├── component.signup_form.yaml
    │   └── component.dashboard.yaml
    │
    ├── api_gateway/
    │   ├── component.authentication.yaml
    │   ├── component.user_management.yaml
    │   └── component.payment_processor.yaml
    │
    ├── ml_service/
    │   ├── component.recommendation_engine.yaml
    │   └── component.fraud_detection.yaml
    │
    └── mobile_app/
        ├── component.login_screen.yaml
        └── component.checkout_flow.yaml
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
    │   ├── component.<name>_state_service.yaml      # meta.type: "state_store"
    │   └── component.trace_recorder.yaml            # Standard component (observability)
    │
    ├── data_model/
    │   ├── component.<collection>_collection.yaml   # Data schemas and shapes
    │   └── component.<entity>_models.yaml
    │
    └── evaluations/
        ├── component.<name>_invariants.yaml         # meta.type: "evaluator" (eval_type: invariant)
        ├── component.<name>_dataset.yaml            # meta.type: "evaluator" (eval_type: dataset)
        └── component.<name>_scorer.yaml             # meta.type: "evaluator" (eval_type: scorer)
```

### **What Makes Something an Agentic Backend Container?**

An `agentic_backend` container is a separately deployable runtime that hosts AI agent logic:

✅ **Agentic Backend components:**
- An agent with a role, tools, and memory strategy
- A workflow/graph that orchestrates LLM calls and tool use
- A tool callable by agents (Python function, BAML function, API wrapper)
- A tool registry that manages tool discovery and validation
- A state store for agent memory and conversation context
- Observability infrastructure (trace recorder, debug app)

❌ **NOT Agentic Backend (these belong elsewhere):**
- The HTTP API that *calls* the agent → belongs in `api_gateway` or `api_backend`
- The data schemas the agent reads → belong in `data_model` container
- The eval harness that tests the agent → belongs in `evaluations` container
- A UI chat component → belongs in `web_app` or `mobile_app`

**Key Question for Agentic Backend**: "Does this component run inside the agent execution loop?"
- Yes → Agentic Backend
- No → Another container

### **Strict Naming Conventions**

**File Naming Pattern**: `<level>.<n>.yaml`

- **System files**: `system.<system_name>.yaml`
- **Container files**: `container.<container_name>.yaml`
- **Component files**: `component.<component_name>.yaml`
- **Tool files**: `component.tool.<tool_name>.yaml` (tools are components with a `tool.` infix)

**Naming Rules**:
- Use lowercase with underscores for multi-word names
- Names should be descriptive and match the `meta.id` field
- Avoid special characters except underscores
- Keep names concise but meaningful

### **ID Field Consistency**

The `meta.id` field must exactly match the filename (without extension):
- File: `container.api_gateway.yaml` → `meta.id: "container.api_gateway"`
- File: `component.login_form.yaml` → `meta.id: "component.login_form"`
- File: `component.tool.fetch_series.yaml` → `meta.id: "component.tool.fetch_series"`

---

## 📐 Complete Schema Structure

```yaml
# ============================================
# META (Always Required - 3 fields minimum)
# ============================================
# Progressive disclosure: Start with just id, purpose, level.
# Add owner, tags, status, etc. as the spec matures.
meta:
  id: ""           # Required: unique identifier (must match filename without .yaml)
  purpose: ""      # Required: one-sentence business value
  level: "system|container|component"  # Required: C4 level

  # Optional but recommended (add as spec matures)
  owner: ""        # Team or person responsible
  tags: []         # ["ui", "api", "ml", "auth", "payment"] - for search/filtering
  status: "draft|active|deprecated|archived"
  last_updated: "YYYY-MM-DD"
  version: ""      # Semantic version or iteration number (e.g., "1.2.0", "sprint-23")

  # Optional quick-routing cues (helpful for tooling/templates)
  type: "component|widget|service|agent|tool|workflow|tool_registry|state_store|evaluator|container|system"
  # New AI-native types:
  #   agent        → an LLM actor with a role, instructions, and tools
  #   tool         → a discrete callable function (used by agents or workflows)
  #   workflow     → orchestration: sequences/graphs of agent calls, tool calls, and logic
  #   tool_registry → catalog + validation layer for tools; forward-compatible with MCP
  #   state_store  → schema + persistence for agent memory and conversation context
  #   evaluator    → quality harness (invariants, datasets, scorers, sim generators)

  domain: "frontend|backend|mobile|infrastructure|ai|data|ai_native"
  # ai_native → components that live inside an agentic execution loop

# ============================================
# REFS - Central Resource Registry
# ============================================
# Link to designs, tickets, docs, research, images, videos, and prompts.
# Use {{refs.<id>.<field>}} to interpolate into diagrams and descriptions.
refs:
  - id: ""              # Unique reference identifier
    type: "design|ticket|doc|image|video|dataset|api|prompt|spec|other"
    # New type:
    #   prompt → system prompts, BAML functions, output schemas, instruction templates
    #   spec   → links to another SpecPlane spec file
    title: ""           # Human-readable title
    url: ""             # Web URL (for external resources)
    path: ""            # Local path relative to repo root (e.g., "./prompts/agent.baml")

    # Governance & lifecycle
    owner: ""
    version: ""
    status: "active|deprecated|archived"
    last_updated: "YYYY-MM-DD"
    access: "public|internal|restricted"

    # Organization
    tags: []
    notes: ""
    related_refs: []

    # Media-specific metadata (optional)
    width: 0            # For images
    height: 0           # For images
    start_time: "0:00"  # For audio/video clips
    duration: "0:00"    # For audio/video clips

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

relationships:
  contains: []
  integrates_with: []

# ─────────────────────────────────────────
# When level="container"
# ─────────────────────────────────────────
container_architecture:
  type: ""              # Optional recognized type: "agentic_backend" | "data_model" | "evaluations"
                        # Leave blank for standard containers (web_app, api_gateway, etc.)
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
    success_metric: ""
    target: ""
    default_destinations: []
    events:
      - name: ""
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
    internal: []
    external: []

  observability:
    metrics: []
    logs: []
    traces: []
    slis: []
    slos: []
    alerting:
      critical: []
      warning: []
    business_impact:
      primary_metric: ""
      dashboard_ref: ""
      success_criteria: ""
    correlation:
      join_key: ""
      note: ""

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
      compliance: ""
      threats: []
      mitigations: []
      data_retention: {}
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

# ============================================
# AI CONFIG (New in v8.0.0)
# ============================================
# Only include when meta.type is one of:
# agent | tool | workflow | tool_registry | state_store | evaluator
#
# Progressive disclosure: start with the minimal fields for your type,
# add more as the spec matures.
#
# ── FOR meta.type: "agent" ─────────────────────────────────────────
ai_config:
  role: ""              # Required: one sentence — what this agent is responsible for
  tools: []             # Component IDs (meta.id) of tools this agent can invoke
  memory:
    strategy: "stateless|turn_based|persistent"
    # stateless     → no memory between calls; each invocation is fresh
    # turn_based    → conversation history passed as context each turn
    # persistent    → external store (vector DB, database); survives sessions
    schema_ref: ""      # Component ID for state/model spec (when persistent)
  model:
    capability: "fast|balanced|capable"
    # fast     → optimized for latency and cost; classification, routing
    # balanced → general purpose; most tasks
    # capable  → max reasoning; complex multi-step analysis, planning
    context_window: ""  # Required context size (e.g., "32k", "200k")
  output_contract: ""   # Ref ID → BAML function, JSON schema, or Pydantic model
                        # If set, AI output must conform; code validates before use
  handoffs:
    - to: ""            # Component ID of target agent or workflow
      condition: ""     # When this handoff occurs
  human_in_loop:
    trigger: ""         # Condition that pauses for human review
    escalation: ""      # Where/how to escalate (queue, channel, component ID)

# ── FOR meta.type: "tool" ──────────────────────────────────────────
ai_config:
  computation_type: "compute|ai_structured|ai_classify|ai_extract|hybrid"
  # compute        → deterministic code (Python, SQL, API call); no LLM
  # ai_structured  → LLM with constrained output schema (BAML, function calling)
  # ai_classify    → LLM for intent/category classification
  # ai_extract     → LLM for structured extraction from unstructured input
  # hybrid         → deterministic code + AI in combination
  is_destructive: false         # Does this modify external state?
  authorization_required: ""    # Permission needed to invoke (leave blank if none)
  output_contract: ""           # Ref ID → output schema (required for ai_* types)
  returns_provenance: false     # Does result include provenance for downstream grounding?
  call_sites: []                # Component IDs (agents/workflows) that invoke this tool
  modes: []                     # If tool behaves differently per a key parameter (e.g., view_type)
  cost_hint: "cheap|medium|expensive"   # Guidance for planner budgeting
  timeout_ms: 0                         # Execution guard in milliseconds

# ── FOR meta.type: "workflow" ──────────────────────────────────────
ai_config:
  pattern: "sequential|parallel|router|directed_graph|loop"
  # sequential    → steps run in order
  # parallel      → steps run concurrently, results merged
  # router        → one of N paths chosen based on input
  # directed_graph → arbitrary graph with conditional edges (e.g., LangGraph)
  # loop          → iterative: agent acts, reflects, repeats until condition met

  # The three-way responsibility split — make this explicit
  computation_model:
    orchestration: ""   # What decides routing and sequencing
                        # Example: "LangGraph conditional edges"
    computation: ""     # What computes deterministic truth (no AI)
                        # Example: "Python — fetch, aggregate, statistical analysis"
    structure: ""       # What shapes and constrains AI outputs
                        # Example: "BAML — intent classification, output extraction"

  # State grouped by role (not exhaustive — name the groups, not every field)
  state_schema:
    identity: []        # Session/user/flow IDs
    input: []           # Per-turn inputs
    routing: []         # Fields that drive conditional edge decisions
    working: []         # Intermediate state produced and consumed across nodes
    output: []          # What goes back to the caller

  # Nodes — one entry per graph node
  nodes:
    - id: ""
      purpose: ""
      computation_type: "compute|ai_structured|ai_classify|ai_extract|hybrid|route"
      # route → pure routing logic; no computation or AI call
      inputs: []            # State fields this node reads
      outputs: []           # State fields this node writes
      output_contract: ""   # Ref ID for constrained output schema (if AI node)
      constrained_inputs: []
      # Fields passed to AI as an allowed-set (NodeContext pattern).
      # Python builds these before calling AI; AI selects only from listed values.
      # Example: ["allowed_tools", "allowed_chart_types"]

  # Routing
  edges:
    - from: ""
      to: ""
      condition: ""     # e.g., "state.fulfillable == false"

  entry_node: ""
  terminal_nodes: []    # Nodes that route to END
  trigger: "api_call|event|schedule|webhook"
  streaming: false      # Does it stream tokens/events back to caller?

# ── FOR meta.type: "tool_registry" ─────────────────────────────────
ai_config:
  provides_discovery: true    # Agents/workflows can query available tools
  provides_validation: true   # Validates proposed tool use before execution
                              # (shape compatibility, unit configuration, n thresholds)
  node_allowlists: true       # Curated per-node tool menus; AI sees only its allowed set
  mcp_compatible: false       # True when this registry could be exposed as an MCP server
                              # (tool definitions + discovery API already match MCP contract)

# ── FOR meta.type: "state_store" ───────────────────────────────────
ai_config:
  persistence: "in_memory|database|vector_store|cache"
  schema_ref: ""              # Component ID for data model spec
  access_pattern: "read_write|read_only|append_only"

# ── FOR meta.type: "evaluator" ─────────────────────────────────────
ai_config:
  eval_type: "invariant|dataset|scorer|sim_generator"
  # invariant     → behavioral rules that must always hold
  # dataset       → curated test cases with expected outputs
  # scorer        → metric computation and pass/fail thresholds
  # sim_generator → generates synthetic inputs for eval coverage
  target: ""              # Component ID being evaluated
  scoring_method: ""      # How quality is measured
  threshold: ""           # Pass/fail bar (e.g., ">90% pass rate", "score ≥ 0.8")

# ============================================
# OPTIONAL: IMPLEMENTATION HINTS
# ============================================
# Technology-specific guidance when truly needed.
# Keep minimal — SpecPlane is implementation-agnostic by design.
implementation_hints:
  web: {}
  mobile: {}
  api: {}
  desktop: {}
  ai:
    framework: ""         # e.g., "LangGraph", "CrewAI", "AutoGen", "custom loop"
    output_schema: ""     # e.g., "BAML", "Pydantic", "JSON Schema", "function calling"
    llm_provider: ""      # e.g., "Anthropic", "OpenAI", "Google"
    model_id: ""          # Specific model when required (e.g., "claude-sonnet-4-6")
    vector_store: ""      # e.g., "Pinecone", "pgvector", "Chroma"
    agent_memory: ""      # e.g., "Firestore", "Redis", "in-process"

# ============================================
# EVIDENCE & TRACEABILITY
# ============================================
evidence:
  user_research: ""
  technical_analysis: ""
  design_artifacts: ""

# ============================================
# DIAGRAMS (Shared Across All Phases)
# ============================================
diagrams:
  - type: "sequence|flowchart|state|class|architecture|user_journey|timeline|mindmap|system_context|container"
    title: ""
    description: ""
    mermaid: |
      # Mermaid diagram code here
```

---

## 🤖 NodeContext Pattern (AI-Native Best Practice)

The NodeContext pattern prevents AI from hallucinating invalid tool names, chart types, or other constrained values. Use it whenever an AI node must choose from a finite set of options.

**The pattern:**

```
1. Python builds an allowed-set from registry + current state
   (e.g., allowed_tools from registry.list_by_node(), allowed_chart_types from data shape)

2. Pass allowed-set to AI as input alongside the task

3. AI selects only from the provided menu — it never sees options it cannot legally choose

4. Python validates AI output against the allowed-set; reject or clamp if outside bounds
```

**In a spec, capture it with `constrained_inputs`:**

```yaml
nodes:
  - id: "PlanQuery"
    computation_type: "ai_structured"
    constrained_inputs:
      - "allowed_tools"        # from registry.list_by_node("PlanQuery")
      - "allowed_chart_types"  # from shape_naming, filtered by intent + data_shape
    output_contract: "baml_extract_plan"
```

**Why this matters:** Without constrained inputs, AI-generated tool names or chart types will occasionally be invalid, causing silent failures. The NodeContext pattern makes AI choices deterministic and debuggable.

---

## 📚 Diagram Type Catalog & Usage Guidance

### **When to Use Each Diagram Type**

| Diagram Type | Best For | Common Patterns |
|--------------|----------|-----------------|
| **sequence** | Request/response flows, actor interactions, API calls | Authentication flows, payment processing, agent-to-agent handoffs |
| **flowchart** | Decision trees, business logic, error handling | Input validation, retry logic, conditional routing, agent branching |
| **state** | Component lifecycle, state machines, mode transitions | Login states, order status, agent execution states |
| **class** | Component structure, data relationships, inheritance | Domain models, component hierarchy, tool registry structure |
| **architecture** | System topology, data flow, deployment structure | Microservices, agentic backend layout, data pipelines |
| **user_journey** | End-to-end UX flows, customer experience mapping | Onboarding, purchase flow, AI-assisted workflows |
| **timeline** | Process schedules, project phases, event sequences | Release timeline, migration plan, incident timeline |
| **mindmap** | Concept hierarchies, feature breakdown, brainstorming | Feature exploration, agent capability map, tool taxonomy |
| **system_context** | C4 Level 1: System boundaries, external actors/systems | System landscape, integration map |
| **container** | C4 Level 2: Technology choices, deployment units | Agentic backend + data_model + evaluations layout |

### **Diagram Best Practices**

✅ **Do:**
- **Prefer ≤3 diagrams per spec** - More diagrams = harder to maintain
- Reference external resources using `{{refs.id.field}}` for clickable links
- Add descriptive titles and descriptions
- Keep diagrams focused (one concern per diagram)

❌ **Don't:**
- Hardcode URLs directly in diagrams (use refs instead)
- Mix concerns (e.g., business logic + infrastructure in one diagram)
- Duplicate information across diagram types

---

## 🔗 Using References in Diagrams

### **Reference Interpolation Syntax**

```yaml
refs:
  - id: "figma_login"
    type: "design"
    title: "Login Screen Mockup V2"
    url: "https://figma.com/file/xyz"
    owner: "UX Team"
    version: "2.1"
    tags: ["auth", "mobile"]
    access: "internal"
    status: "active"

  - id: "system_prompt_v3"
    type: "prompt"
    title: "Agent System Prompt v3"
    path: "./prompts/agent_v3.baml"
    version: "3.0.0"
    status: "active"
    tags: ["agent", "baml"]

diagrams:
  - type: "sequence"
    title: "User Login Flow"
    description: "Authentication sequence with design references"
    mermaid: |
      sequenceDiagram
          participant U as User
          participant App as Mobile App
          participant API as Auth API

          Note over U,App: Design: {{refs.figma_login.title}}
          U->>App: Enter credentials
          App->>API: POST /login
          API-->>App: JWT token
          App-->>U: Navigate to dashboard

          click App "{{refs.figma_login.url}}" "View Figma Design"
```

### **Reference Type Detection Patterns**

When users paste URLs, auto-detect type:
- `figma.com` → `type: "design"`
- `atlassian.net|jira.com` → `type: "ticket"`
- `docs.google.com` → `type: "doc"`
- `.png|.jpg|.svg|.webp` → `type: "image"`
- `.mp4|.mov|.webm` → `type: "video"`
- `github.com/.../issues` → `type: "ticket"`
- `linear.app` → `type: "ticket"`
- `.baml|.prompt|system_prompt` → `type: "prompt"`
- Other `.yaml` SpecPlane files → `type: "spec"`

---

## 📋 Complete Example: Login Component (Standard)

```yaml
meta:
  id: "component.login_form"
  purpose: "Enable users to authenticate with email/password or OAuth providers"
  level: "component"
  owner: "Auth Team"
  tags: ["auth", "security", "frontend"]
  status: "active"
  last_updated: "2025-01-20"
  version: "2.1.0"
  type: "widget"
  domain: "frontend"

refs:
  - id: "figma_login"
    type: "design"
    title: "Login Form Design V2.1"
    url: "https://figma.com/file/abc123"
    owner: "UX Team"
    version: "2.1"
    status: "active"
    tags: ["auth", "ui"]
    access: "internal"

planning:
  user_flows:
    actions:
      - "User enters email and password"
      - "User clicks login button"
      - "User selects OAuth provider (Google, Apple)"
    success:
      - "User sees dashboard within 2 seconds"
      - "Session persists across browser restarts (if remember me checked)"
    errors:
      - "Invalid credentials → clear error message with retry option"
      - "Account locked → show unlock instructions and support contact"
      - "Network timeout → show retry with exponential backoff"

  analytics:
    success_metric: "successful_login_rate"
    target: ">95% of login attempts succeed within 3 attempts"
    default_destinations: ["mixpanel", "amplitude"]
    events:
      - name: "login_attempted"
        when: "User clicks login button"
        properties:
          method: "email|google|apple"
          remember_me: "boolean"
      - name: "login_succeeded"
        when: "Authentication successful"
        properties:
          method: "email|google|apple"
          duration_ms: "number"

implementation:
  interface:
    capabilities:
      - "validate_email_format"
      - "authenticate_user"
      - "handle_oauth_callback"
      - "manage_session_state"
    inputs:
      - "email: string"
      - "password: string"
      - "remember_me: boolean"
    outputs:
      - "auth_token: string"
      - "user_id: string"
      - "session_expires_at: timestamp"
    side_effects:
      - "Creates user session in backend"
      - "Stores auth token in secure storage"
      - "Emits auth_state_changed event"

  contracts:
    apis:
      - endpoint: "/api/auth/login"
        method: "POST"
        request:
          email: "string"
          password: "string"
          remember_me: "boolean"
        response:
          token: "string"
          user_id: "string"
          expires_at: "timestamp"
        errors:
          - code: 401
            reason: "invalid_credentials"
          - code: 423
            reason: "account_locked"
          - code: 429
            reason: "rate_limit_exceeded"

    states:
      - name: "form_state"
        transitions:
          - "idle → validating (on submit)"
          - "validating → authenticating (if valid)"
          - "authenticating → authenticated (on success)"
          - "authenticating → error (on failure)"
          - "error → idle (on retry)"

  dependencies:
    internal:
      - "component.error_toast"
      - "component.loading_spinner"
    external:
      - "Auth0 Authentication API"

  observability:
    slis:
      - "login_success_rate"
      - "login_latency_p95"
    slos:
      - "login_success_rate ≥ 99.5%"
      - "login_latency_p95 < 500ms"
    alerting:
      critical:
        - "login_success_rate < 95% for 5 minutes → Page on-call"
      warning:
        - "login_latency_p95 > 1s for 10 minutes → Notify #auth-team"

  technical_constraints:
    performance:
      response_time: "< 200ms p95"
      availability: "99.9% uptime"
    security:
      authentication: "OAuth 2.0 + PKCE, bcrypt for passwords"
      compliance: "GDPR, SOC 2 Type II"
      threats:
        - "credential_stuffing"
        - "brute_force_attacks"
      mitigations:
        - "Rate limiting: 5 attempts per 15 minutes per IP"
        - "Account lockout after 10 failures"

  validation:
    acceptance_criteria:
      - "Valid credentials → dashboard within 2s"
      - "Invalid credentials → clear error message"
      - "6th attempt blocked by rate limiting"
    readiness: "ready"

diagrams:
  - type: "sequence"
    title: "Successful Email Login Flow"
    mermaid: |
      sequenceDiagram
        actor U as User
        participant W as Web App
        participant A as Auth API

        Note over U,W: Design: {{refs.figma_login.title}}
        U->>W: Enter email/password
        W->>W: Validate format
        W->>A: POST /auth/login
        A-->>W: 200 OK {token, user_id}
        W-->>U: Redirect to dashboard
        click W "{{refs.figma_login.url}}" "View Design"
```

---

## 📋 Complete Example: AI Workflow (Agentic Backend)

A minimal but complete spec for a directed-graph workflow component.

```yaml
meta:
  id: "component.analysis_workflow"
  purpose: "Orchestrate intent classification, data fetch, analysis, and explanation for user analytics queries"
  level: "component"
  owner: "Backend Team"
  tags: ["agent", "workflow", "langgraph", "analytics"]
  status: "draft"
  last_updated: "2026-01-15"
  version: "0.1.0"
  type: "workflow"
  domain: "ai_native"

refs:
  - id: "system_prompt_classify"
    type: "prompt"
    title: "Intent Classification BAML Function"
    path: "./prompts/classify_intent.baml"
    version: "1.0.0"
    status: "active"

  - id: "tool_registry_spec"
    type: "spec"
    title: "Analytics Tools Registry"
    path: "./component.tool.analytics_registry.yaml"
    status: "draft"

planning:
  user_flows:
    actions:
      - "User submits a natural language analytics question"
      - "System classifies intent and checks feasibility"
      - "System fetches and analyzes relevant data"
      - "System returns chart + insights + follow-up suggestions"
    success:
      - "User sees a relevant chart with grounded insights within 3s"
      - "Follow-up suggestions match the analysis context"
    errors:
      - "Unfulfillable request → honest explanation + suggestions, no chart"
      - "Insufficient data → empty state with guidance to log more"
      - "Tool timeout → graceful fallback with partial result"

implementation:
  interface:
    capabilities:
      - "classify_user_intent"
      - "assess_request_feasibility"
      - "plan_and_execute_analysis"
      - "build_chart_spec"
      - "generate_grounded_explanation"
    inputs:
      - "question: string"
      - "user_id: string"
      - "flow_id: string"
      - "conversation_context: string (recent history)"
    outputs:
      - "chart_id: string | null"
      - "chart_type: string | null"
      - "dataset: object | null"
      - "insights: string[]"
      - "explanation: string"
      - "follow_ups: string[]"
      - "fulfillable: boolean"

  dependencies:
    internal:
      - "component.tool.analytics_registry"
      - "component.tool.fetch_series"
      - "component.agent_state_service"
    external:
      - "LangGraph (orchestration)"
      - "BAML (structured AI outputs)"

  observability:
    metrics:
      - "workflow_execution_duration_ms"
      - "node_execution_duration_by_node"
      - "fulfillable_rate"
      - "sufficiency_pass_rate"
    slos:
      - "workflow_p95_latency < 3000ms"
      - "fulfillable_rate > 80%"
    alerting:
      critical:
        - "workflow_error_rate > 5% for 5 minutes"
      warning:
        - "workflow_p95_latency > 5s for 10 minutes"

  validation:
    acceptance_criteria:
      - "Valid query → chart + insights returned within 3s"
      - "Unfulfillable query → explanation only, no fetch attempted"
      - "Insufficient data → empty state with suggestion"
      - "AI never selects a tool not in its allowed-set"
    edge_cases:
      - "Empty flow (no data primitives) → friendly message, no analysis"
      - "Timeout in fetch tool → graceful fallback, no silent failure"
    readiness: "draft"

ai_config:
  pattern: "directed_graph"

  computation_model:
    orchestration: "LangGraph conditional edges"
    computation: "Python — fetch, aggregate, statistical analysis"
    structure: "BAML — intent classification, plan extraction, output shaping"

  state_schema:
    identity: ["user_id", "flow_id", "conversation_id"]
    input: ["question", "time_range", "chart_preference", "conversation_context"]
    routing: ["request_type", "fulfillable", "sufficient"]
    working: ["intent", "plan", "backend_data", "statistical_results"]
    output: ["chart_id", "chart_type", "dataset", "insights", "explanation", "follow_ups"]

  nodes:
    - id: "ClassifyIntent"
      purpose: "Classify user question into intent type and extract selected items"
      computation_type: "ai_classify"
      inputs: ["question", "conversation_context", "flow_primitives"]
      outputs: ["intent", "request_type", "selected_items"]
      output_contract: "system_prompt_classify"

    - id: "CheckFeasibility"
      purpose: "Decide if request is structurally fulfillable without fetching data"
      computation_type: "ai_structured"
      inputs: ["intent", "question", "flow_primitives"]
      outputs: ["fulfillable", "reason", "suggested_alternatives"]

    - id: "PlanQuery"
      purpose: "Determine what to fetch and how; select tools from allowed set"
      computation_type: "ai_structured"
      inputs: ["intent", "flow_primitives", "time_range"]
      outputs: ["plan"]
      constrained_inputs: ["allowed_tools", "allowed_chart_types"]

    - id: "FetchData"
      purpose: "Execute fetch tool; return normalized payload + provenance"
      computation_type: "compute"
      inputs: ["plan", "user_id", "flow_id"]
      outputs: ["backend_data"]

    - id: "SufficiencyCheck"
      purpose: "Check if fetched data meets minimum thresholds for analysis"
      computation_type: "hybrid"
      inputs: ["backend_data", "plan"]
      outputs: ["sufficient", "sufficiency_detail"]
      constrained_inputs: ["allowed_chart_types"]

    - id: "Analyze"
      purpose: "Run Python statistical analysis on fetched data"
      computation_type: "compute"
      inputs: ["backend_data", "plan"]
      outputs: ["statistical_results"]

    - id: "BuildChartSpec"
      purpose: "Produce chart dataset + spec from analysis results"
      computation_type: "hybrid"
      inputs: ["backend_data", "statistical_results", "plan"]
      outputs: ["chart_id", "chart_type", "dataset", "spec"]

    - id: "Explain"
      purpose: "Generate grounded insights and follow-up suggestions; interpretation only"
      computation_type: "ai_generate"
      inputs: ["dataset", "statistical_results", "provenance"]
      outputs: ["insights", "explanation", "follow_ups"]

    - id: "ExplainUnfulfillable"
      purpose: "Return honest explanation when request cannot be fulfilled; no chart"
      computation_type: "ai_generate"
      inputs: ["reason", "suggested_alternatives", "question"]
      outputs: ["explanation", "follow_ups"]

    - id: "ExplainInsufficient"
      purpose: "Return explanation and empty state when data thresholds not met"
      computation_type: "hybrid"
      inputs: ["sufficiency_detail", "plan", "question"]
      outputs: ["explanation", "follow_ups", "chart_type"]

  edges:
    - from: "ClassifyIntent"
      to: "ExplainFollowUp"
      condition: "request_type == follow_up_explanation"
    - from: "ClassifyIntent"
      to: "CheckFeasibility"
      condition: "request_type == new_chart or follow_up_refine_chart"
    - from: "CheckFeasibility"
      to: "PlanQuery"
      condition: "fulfillable == true"
    - from: "CheckFeasibility"
      to: "ExplainUnfulfillable"
      condition: "fulfillable == false"
    - from: "PlanQuery"
      to: "FetchData"
      condition: "default"
    - from: "SufficiencyCheck"
      to: "Analyze"
      condition: "sufficient == true"
    - from: "SufficiencyCheck"
      to: "ExplainInsufficient"
      condition: "sufficient == false"
    - from: "BuildChartSpec"
      to: "Explain"
      condition: "default"

  entry_node: "ClassifyIntent"
  terminal_nodes: ["Explain", "ExplainUnfulfillable", "ExplainInsufficient", "ExplainFollowUp"]
  trigger: "api_call"
  streaming: false

implementation_hints:
  ai:
    framework: "LangGraph"
    output_schema: "BAML"
    llm_provider: "Anthropic"
    model_id: "claude-sonnet-4-6"
```

---

## 📋 Complete Example: Tool Registry (Agentic Backend)

A minimal spec for a tool registry component.

```yaml
meta:
  id: "component.tool.analytics_registry"
  purpose: "Source of truth for tool availability and constraints; provides per-node allowlists so AI never sees tools it cannot legally choose"
  level: "component"
  owner: "Backend Team"
  tags: ["tool", "registry", "analytics", "pattern"]
  status: "draft"
  last_updated: "2026-01-15"
  version: "0.1.0"
  type: "tool_registry"
  domain: "ai_native"

planning:
  user_flows:
    actions: []   # No direct user interaction — internal infrastructure

  # Describe the integration context instead
  # when_used: Called by workflow nodes before every AI call that selects tools

implementation:
  interface:
    capabilities:
      - "register_tool"
      - "discover_tools_by_node"
      - "validate_proposed_tool_use"
      - "query_tools_by_context"
    inputs:
      - "node_name: string (for list_by_node)"
      - "intent: string (for query)"
      - "data_shape: string (for query and validate)"
      - "proposed_step: object (for validate)"
    outputs:
      - "allowed_tools: string[] (for node allowlist)"
      - "validation_result: {valid: boolean, reason: string}"

  dependencies:
    internal:
      - "component.tool.fetch_series"
    external:
      - "Python"

  validation:
    acceptance_criteria:
      - "list_by_node returns only tools in that node's curated allowlist"
      - "validate rejects tool whose data_shape requirement is not met"
      - "deprecated tools excluded from list_by_node when migration_mode=false"
      - "AI never receives a tool name not in allowed_tools"
    readiness: "draft"

ai_config:
  provides_discovery: true
  provides_validation: true
  node_allowlists: true
  mcp_compatible: true    # Tool definitions + discovery API match MCP contract
                          # Future: expose as MCP server with HTTP transport
```

---

## 🔧 Tooling & Validation

### **File Validation Rules**

1. **Filename matches meta.id**
   ```bash
   # ✅ Valid
   File: component.tool.fetch_series.yaml
   meta.id: "component.tool.fetch_series"

   # ❌ Invalid
   File: component.tool.fetch_series.yaml
   meta.id: "fetch_series"
   ```

2. **File location matches level**
   ```bash
   # ✅ Valid
   specs/system.saas_platform.yaml
   specs/containers/container.agentic_backend.yaml
   specs/components/agentic_backend/component.tool.fetch_series.yaml

   # ❌ Invalid
   specs/component.tool.fetch_series.yaml   # Should be in components/<container>/
   ```

3. **Relationships reference existing specs**
   ```yaml
   # ✅ Valid
   relationships:
     contains:
       - "component.tool.fetch_series"  # File exists

   # ❌ Invalid
   relationships:
     contains:
       - "fetch_series"            # Missing level prefix
   ```

4. **ai_config only on AI-native types**
   ```yaml
   # ✅ Valid
   meta:
     type: "workflow"
   ai_config:
     pattern: "directed_graph"

   # ❌ Invalid
   meta:
     type: "widget"
   ai_config:           # ai_config not applicable to standard component types
     ...
   ```

5. **output_contract references a valid prompt ref**
   ```yaml
   # ✅ Valid
   refs:
     - id: "baml_classify"
       type: "prompt"
       path: "./prompts/classify.baml"

   nodes:
     - id: "ClassifyIntent"
       output_contract: "baml_classify"   # matches refs.id

   # ❌ Invalid
   nodes:
     - id: "ClassifyIntent"
       output_contract: "classify.baml"   # not a refs.id
   ```

---

## 💡 Interactive Guidance Commands

### When user asks for help:

**Structure & Organization:**
- "Review this spec" → Provide completeness checklist
- "Organize file structure" → Guide through folder hierarchy and naming
- "Fix naming convention" → Correct file naming and meta.id consistency
- "Validate file organization" → Check naming, folder structure, and ID consistency

**C4 Architecture:**
- "Create system context" → Guide through C4 Level 1
- "Design container architecture" → Help with C4 Level 2
- "Should this be a container?" → Explain deployment unit criteria
- "Set up agentic backend" → Walk through 3-container layout (agentic_backend, data_model, evaluations)

**Planning & Design:**
- "Add user flows" → Guide through actions, success, and error scenarios
- "Define analytics events" → Help structure product analytics tracking
- "Add integrations" → Document third-party SDKs and services

**Implementation:**
- "Add monitoring" → Suggest relevant metrics, logs, traces, SLOs
- "Add security" → Include appropriate security constraints and threat mitigations
- "Make it more testable" → Suggest measurable acceptance criteria

**AI-Native Components:**
- "Add an agent" → Guide through role, tools, memory, output_contract
- "Add a workflow" → Walk through computation_model, nodes, edges, state_schema
- "Add a tool" → Guide through computation_type, output_contract, call_sites
- "Add a tool registry" → Explain the registry pattern, mcp_compatible flag
- "Set up the NodeContext pattern" → Guide through constrained_inputs on nodes
- "Define the computation model" → Help articulate orchestration / computation / structure split
- "Add output contracts" → Guide through prompt refs and output_contract fields
- "Plan evals" → Walk through evaluations container with invariant, dataset, scorer types
- "What type should this be?" → Diagnose agent vs tool vs workflow vs tool_registry
- "Is this MCP-compatible?" → Assess registry against MCP contract requirements

**Visualization:**
- "Add sequence diagram" → Guide through interaction flow patterns
- "Show state transitions" → Suggest state diagram
- "Document decision logic" → Create flowchart for business rules
- "Visualize agent graph" → Create flowchart or architecture diagram of workflow nodes and edges

**Resources & Traceability:**
- "Add design references" → Help create refs for Figma, Sketch files
- "Link project tickets" → Guide through Jira, ClickUp, GitHub issue refs
- "Add prompt references" → Create refs for BAML files, system prompts, output schemas
- "Link to another spec" → Add a refs entry with type: "spec"
- "Add evidence" → Link to user research, technical analysis, design artifacts

---

## 🎓 Best Practices Summary

### **SpecPlane Philosophy in Action**

✅ **DO:**
- Start with minimal meta (id, purpose, level)
- Progressively add sections as needed
- Use refs to link to external resources (including prompts and other specs)
- Separate business analytics from technical observability
- Write implementation-agnostic specs with optional hints
- For AI-native components: make the computation model split explicit
- Use the NodeContext pattern for any AI node that selects from a finite set
- Set `output_contract` on every AI node; validate before use
- Mark tool registries with `mcp_compatible` when the API matches MCP contract

❌ **DON'T:**
- Copy-paste boilerplate without customizing
- Duplicate information across sections
- Hardcode URLs in diagrams (use refs)
- Mix business and technical concerns
- Over-specify implementation details
- For AI-native: let AI choose from unbounded option sets
- For AI-native: conflate orchestration, computation, and structure responsibilities
- Skip `output_contract` on AI nodes — unconstrained outputs cause silent failures

### **Quality Checklist**

Before marking a spec as `status: "active"`:

**All specs:**
- [ ] Meta fields complete (id, purpose, level, owner)
- [ ] File naming and location correct
- [ ] Refs organized with proper lifecycle status
- [ ] Behavioral contracts defined
- [ ] Observability instrumented (metrics, SLOs, alerting)
- [ ] Security constraints documented
- [ ] Acceptance criteria measurable
- [ ] Edge cases considered
- [ ] Assumptions listed
- [ ] Relationships to other specs defined

**AI-native specs (when meta.type is agent/tool/workflow/tool_registry/evaluator):**
- [ ] `ai_config` section present with type-appropriate fields
- [ ] `computation_model` split defined (orchestration / computation / structure)
- [ ] Every AI node has an `output_contract` ref
- [ ] Nodes that select from finite sets use `constrained_inputs` (NodeContext pattern)
- [ ] Tool `computation_type` is accurate (compute vs ai_structured vs hybrid)
- [ ] Tool registries have `mcp_compatible` flag set
- [ ] `implementation_hints.ai` populated with framework, output_schema, model
- [ ] Evals container referenced in dependencies or relationships

---

**Remember**: SpecPlane specs should be **implementation-agnostic** but **detailed enough** to guide development across any technology stack. Focus on **WHAT** the component should do and **HOW WELL** it should do it, not **HOW** it should be implemented.

For AI-native components, also focus on **WHO does what**: make the orchestration / computation / structure split explicit, constrain AI outputs, and treat tool registries as first-class infrastructure — they are the foundation of reliable, debuggable agentic systems.
