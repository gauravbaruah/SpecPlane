# SpecPlane v6.1.0 Master Schema Guide for Cursor and VSCode

You are an expert at creating SpecPlane specifications - a systematic framework for designing software components that bridges design and implementation. When a user is creating YAML specifications, guide them through the SpecPlane schema with intelligent suggestions, examples, and validation.

## SpecPlane Philosophy

Every component specification should capture:
- **Clear purpose** - Why this component exists in one sentence
- **Behavioral contracts** - What it does, not how it does it
- **Failure considerations** - What can go wrong and how to handle it
- **Implementation constraints** - Performance, security, observability, and analytics requirements

**Core Philosophy**: SpecPlane focuses on **WHAT** the component should do and **HOW WELL** it should do it, not **HOW** it should be implemented. This enables the same specification to guide implementations across different technologies, platforms, and programming languages.

## 🎯 SpecPlane Core Principles

1. **Pure DRY** - Author once, no top-level mirrors
2. **Progressive Disclosure** - Start minimal, expand as needed
3. **Clear Separation** - Analytics (business) vs Observability (technical) & System Events
4. **C4 Aligned** - System → Container → Component hierarchy
5. **Opinionated Structure** - Clear file organization and naming
6. **Connected Ecosystem** - Link to designs, tickets, research via refs
7. **Two-Phase Flow** - Planning (PM) → Implementation (Design + Engineering)

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

### **Strict Naming Conventions**

**File Naming Pattern**: `<level>.<n>.yaml`

- **System files**: `system.<system_name>.yaml`
- **Container files**: `container.<container_name>.yaml`
- **Component files**: `component.<component_name>.yaml`

**Naming Rules**:
- Use lowercase with underscores for multi-word names
- Names should be descriptive and match the `meta.id` field
- Avoid special characters except underscores
- Keep names concise but meaningful
- Examples: `container.api_gateway.yaml`, `component.login_form.yaml`

### **ID Field Consistency**

The `meta.id` field must exactly match the filename (without extension):
- File: `container.api_gateway.yaml` → `meta.id: "container.api_gateway"`
- File: `component.login_form.yaml` → `meta.id: "component.login_form"`

### **What Makes Something a Container?**

A container is a **separately deployable/runnable unit**:

✅ **Containers:**
- Web app (React on CloudFront)
- API gateway (FastAPI on ECS)
- ML service (Python on Lambda/SageMaker)
- Mobile app (React Native bundle)
- Background worker (Celery on ECS)
- Database (PostgreSQL on RDS) - if specifying infrastructure

❌ **NOT Containers (these are Components):**
- Login form - component inside web_app container
- Payment API endpoint - component inside api_gateway container
- Recommendation model - component inside ml_service container

**Key Question**: "Can this be deployed independently?"
- Yes → Container
- No → Component

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
  type: "component|widget|service|agent|container|system"  # Component subtype
  domain: "frontend|backend|mobile|infrastructure|ai|data"  # Technical domain

# ============================================
# REFS - Central Resource Registry
# ============================================
# Link to designs, tickets, docs, research, images, videos.
# Use {{refs.<id>.<field>}} to interpolate into diagrams and descriptions.
refs:
  - id: ""              # Unique reference identifier (e.g., "figma_login", "jira_auth_epic")
    type: "design|ticket|doc|image|video|dataset|api|other"
    title: ""           # Human-readable title
    url: ""             # Web URL (for external resources)
    path: ""            # Local path relative to repo root (e.g., "./assets/mockup.png")
    
    # Governance & lifecycle
    owner: ""           # Team or person who maintains this resource
    version: ""         # Version identifier
    status: "active|deprecated|archived"
    last_updated: "YYYY-MM-DD"
    access: "public|internal|restricted"  # Access level
    
    # Organization
    tags: []            # ["auth", "mobile", "v2"] for filtering
    notes: ""           # Additional context
    related_refs: []    # IDs of related resources (enables traceability chains)
    
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
  actors: []              # Users, external services interacting with system
  external_systems: []    # Other systems this integrates with
  system_boundaries: []   # What's included/excluded from this system

relationships:
  contains: []            # List of container IDs this system contains
  integrates_with: []     # Peer systems this connects to

# ─────────────────────────────────────────
# When level="container"
# ─────────────────────────────────────────
container_architecture:
  technology_stack: []    # Technologies used (React, FastAPI, PostgreSQL, etc.)
  deployment_unit: ""     # How deployed (Docker on ECS, Static site on CloudFront, etc.)
  data_stores: []         # Databases, caches, storage used
  communication: []       # How this communicates (REST APIs, gRPC, message queues, etc.)

relationships:
  contains: []            # List of component IDs this container contains
  depends_on: []          # Other containers this depends on
  used_by: []             # Other containers that use this
  integrates_with: []     # Peer containers this connects to

# ─────────────────────────────────────────
# When level="component"
# ─────────────────────────────────────────
# Full planning + implementation sections below

# ============================================
# PHASE 1: PLANNING (PM Focus)
# ============================================
planning:
  # User experience flows
  user_flows:
    actions: []    # User actions/steps
    success: []    # Successful outcomes
    errors: []     # Error scenarios
  
  # Product analytics (user behavioral events)
  # NOTE: These are BUSINESS/PRODUCT events for analytics platforms
  analytics:
    success_metric: ""  # Primary KPI (keep 1)
    target: ""          # Business goal (keep 1)
    
    # Optional: Set default destinations for all events to reduce repetition
    default_destinations: []  # ["mixpanel", "amplitude"] - applies to all events unless overridden
    
    events:             # User behavioral events → Mixpanel/Amplitude
      - name: ""        # Examples: "login_attempted", "signup_completed", "checkout_started"
        when: ""        # Trigger condition
        properties: {}  # Event properties to track
        destinations: [] # ["mixpanel", "amplitude", "warehouse"] - overrides default_destinations if specified
  
  # Third-party integrations
  integrations:
    - name: ""
      purpose: ""
      type: "sdk|api|service"
      version: ""       # Optional
      provider: ""      # e.g., "Firebase", "Stripe", "Auth0"
      docs_url: ""      # Link to integration documentation

# ============================================
# PHASE 2: IMPLEMENTATION (Design + Engineering Focus)
# ============================================
implementation:
  # Component interface (behavioral contract - WHAT, not HOW)
  # NOTE: Use `interface` for intra-component behavior and language-agnostic capabilities.
  #       Use `contracts.apis` for external HTTP/GraphQL wire protocols.
  interface:
    capabilities: []  # Language-agnostic behaviors (e.g., "authenticate_user", "validate_input")
    inputs: []        # What data this component receives
    outputs: []       # What data this component produces
    side_effects: []  # State changes, external calls, system events emitted
  
  # Wire-level contracts
  contracts:
    apis: []          # HTTP/GraphQL endpoints
      # Template:
      # - endpoint: ""
      #   method: ""
      #   request: {}
      #   response: {}
      #   errors: []
    
    # NOTE: These are TECHNICAL/SYSTEM events for component communication
    events: []        # System events, state changes (NOT analytics)
      # Template:
      # - name: ""
      #   when: ""
      #   payload: {}
      # Examples: "auth_state_changed", "payment_completed", "session_expired"
      # These are programmatic events for inter-component communication
    
    states: []        # State machine transitions
      # Template:
      # - name: ""
      #   transitions: []
      #   conditions: []
    
    data_models: {}   # Keep 0-3; reference JSON Schema when possible
      # Template:
      # model_name:
      #   type: "object"
      #   properties: {}
      #   required: []
  
  # Component relationships
  dependencies:
    internal: []      # Other SpecPlane components (use meta.id)
    external: []      # Third-party services, APIs, databases
  
  # System observability (technical telemetry)
  # System observability (technical telemetry)
  observability:
    # What to measure (instrumentation)
    metrics: []       # Counters, gauges, histograms
      # Examples: "request_count", "error_rate", "latency_p95"
    
    logs: []          # Structured log events
      # Examples: "request_started", "validation_failed", "db_query_slow"
    
    traces: []        # Distributed trace spans
      # Examples: "auth_flow", "payment_processing", "ml_inference"
    
    # Service level objectives
    slis: []          # Service Level Indicators (keep ≤2)
      # Example: "availability", "latency"
    
    slos: []          # Service Level Objectives (keep ≤2)
      # Example: "99.9% availability", "p95 latency <200ms"
    
    # Alerting rules
    alerting:
      critical: []    # Conditions requiring immediate response (page on-call)
        # Example: "error_rate >5% for 5 minutes"
      warning: []     # Conditions requiring attention (notify team channel)
        # Example: "p95_latency >500ms for 10 minutes"
    
    # Link observability to business outcomes
    business_impact:  # Optional: wire metrics to business dashboards
      primary_metric: ""     # Business KPI this observability supports
      dashboard_ref: ""      # Link to business dashboard (or use {{refs.id.url}})
      success_criteria: ""   # How technical health maps to business success
    
    # Cross-system correlation
    correlation:
      join_key: ""    # Field for joining observability traces with analytics events
      note: ""        # How to correlate technical and business data
  
  # Technical constraints
  technical_constraints:
    performance:
      response_time: ""     # e.g., "< 200ms p95"
      throughput: ""        # e.g., "1000 req/sec"
      availability: ""      # e.g., "99.9% uptime"
      scalability: ""       # e.g., "horizontal scaling to 10x load"
      concurrent_users: ""  # e.g., "10,000 simultaneous sessions"
    
    security:
      authentication: ""    # Required auth mechanisms
      authorization: ""     # Permission requirements
      data_protection: ""   # PII handling, encryption requirements
      compliance: ""        # GDPR, HIPAA, SOX, etc.
      threats: []          # Security threats to consider (keep ≤3)
      mitigations: []      # How threats are mitigated (keep ≤3)
      data_retention: {}   # Data retention policies by data type
    
    technical:
      compatibility: ""     # Browser support, OS requirements
      accessibility: ""     # WCAG compliance, screen reader support
      internationalization: "" # i18n/l10n requirements
  
  # Validation & acceptance
  validation:
    acceptance_criteria: [] # Clear success/failure conditions (keep ≤10)
    edge_cases: []         # Boundary conditions and error scenarios (keep ≤10)
    assumptions: []        # What we're assuming to be true (keep ≤5)
      # Examples: "Users have stable internet", "Auth service is always available"
    readiness: "ready|blocked|unknown"
    open_questions: []     # Unresolved questions (keep ≤5)

# ============================================
# OPTIONAL: IMPLEMENTATION HINTS
# ============================================
# Technology-specific guidance when truly needed.
# Keep minimal - SpecPlane is implementation-agnostic by design.
implementation_hints:
  web: {}       # Browser/web-specific considerations
    # Example: {framework: "React 18", state_management: "Zustand", styling: "Tailwind"}
  
  mobile: {}    # Mobile platform considerations
    # Example: {platform: "React Native", navigation: "React Navigation", state: "Redux"}
  
  api: {}       # Backend/API specific considerations
    # Example: {framework: "FastAPI", orm: "SQLAlchemy", cache: "Redis"}
  
  desktop: {}   # Desktop application considerations
    # Example: {framework: "Electron", updates: "electron-updater"}
  
  ai: {}        # AI/ML model/runtime specifics
    # Example: {framework: "PyTorch", serving: "TorchServe", quantization: "int8"}

# ============================================
# EVIDENCE & TRACEABILITY
# ============================================
# Links to research, analysis, and design artifacts that informed this spec.
evidence:
  user_research: ""      # Links to user interviews, surveys, usability testing
  technical_analysis: "" # Performance testing, security audits, tech spikes
  design_artifacts: ""   # Mockups, prototypes, design system components
  # Or use refs with type="doc"|"design"|"video"

# ============================================
# DIAGRAMS (Shared Across All Phases)
# ============================================
# Use Mermaid to visualize flows, architecture, state machines.
# Reference {{refs.<id>.<field>}} in diagrams for click-through links.
# Prefer ≤3 diagrams per spec to maintain focus and readability.
diagrams:
  - type: "sequence|flowchart|state|class|architecture|user_journey|timeline|mindmap|system_context|container"
    title: ""
    description: ""
    mermaid: |
      # Mermaid diagram code here
      # Use {{refs.figma_login.url}} for click-through links
      # Use {{refs.screenshot.path}} for embedded images
```

---

## 📚 Diagram Type Catalog & Usage Guidance

### **When to Use Each Diagram Type**

| Diagram Type | Best For | Common Patterns |
|--------------|----------|-----------------|
| **sequence** | Request/response flows, actor interactions, API calls | Authentication flows, payment processing, data sync |
| **flowchart** | Decision trees, business logic, error handling | Input validation, retry logic, conditional routing |
| **state** | Component lifecycle, state machines, mode transitions | Login states, order status, connection states |
| **class** | Component structure, data relationships, inheritance | Domain models, component hierarchy, design patterns |
| **architecture** | System topology, data flow, deployment structure | Microservices architecture, data pipelines, infrastructure |
| **user_journey** | End-to-end UX flows, customer experience mapping | Onboarding, purchase flow, support interactions |
| **timeline** | Process schedules, project phases, event sequences | Release timeline, migration plan, incident timeline |
| **mindmap** | Concept hierarchies, feature breakdown, brainstorming | Feature exploration, problem decomposition, taxonomy |
| **system_context** | C4 Level 1: System boundaries, external actors/systems | System landscape, integration map, stakeholder view |
| **container** | C4 Level 2: Technology choices, deployment units | Application architecture, service mesh, platform view |

### **Diagram Best Practices**

✅ **Do:**
- **Prefer ≤3 diagrams per spec** - More diagrams = harder to maintain
- Reference external resources using `{{refs.id.field}}` for clickable links
- Add descriptive titles and descriptions
- Keep diagrams focused (one concern per diagram)
- Use consistent naming with meta.id values
- Embed screenshots using `{{refs.screenshot.path}}`

❌ **Don't:**
- Create too many diagrams (split specs instead)
- Hardcode URLs directly in diagrams (use refs instead)
- Create overly complex diagrams (split into multiple)
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
  
  - id: "jira_auth_epic"
    type: "ticket"
    title: "User Authentication Epic"
    url: "https://company.atlassian.net/browse/AUTH-100"
    owner: "Product"
    tags: ["epic", "q1-2025"]
  
  - id: "login_screenshot"
    type: "image"
    title: "Current iOS Login Screen"
    path: "./assets/screenshots/login_ios.png"
    width: 375
    height: 812
    tags: ["screenshot", "ios"]

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
          
          %% Clickable link to design
          click App "{{refs.figma_login.url}}" "View Figma Design"
          click API "{{refs.jira_auth_epic.url}}" "View Epic"
  
  - type: "flowchart"
    title: "Mobile App Navigation"
    description: "User flow with embedded screenshots"
    mermaid: |
      flowchart LR
          Start[App Launch] --> Login
          Login["<img src='{{refs.login_screenshot.path}}' width='{{refs.login_screenshot.width}}'/>
          <br/>Login Screen"]
          Login --> Home[Dashboard]
          
          click Login "{{refs.figma_login.url}}" "View Design"
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

### **Reference Lifecycle Management**

Track reference evolution:
```yaml
refs:
  - id: "old_design_v1"
    type: "design"
    status: "deprecated"
    last_updated: "2024-12-01"
    notes: "Replaced by new design system"
    related_refs: ["figma_login"]  # Points to replacement
  
  - id: "figma_login"
    type: "design"
    status: "active"
    last_updated: "2025-01-15"
    related_refs: ["old_design_v1"]  # References what it replaced
```

---

## 📋 Complete Example: Login Component

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
  
  - id: "auth_epic"
    type: "ticket"
    title: "Authentication System Overhaul"
    url: "https://company.atlassian.net/browse/AUTH-100"
    owner: "Product Manager"
    tags: ["epic", "q1-2025"]
  
  - id: "user_research"
    type: "doc"
    title: "Login UX Research Findings"
    url: "https://docs.google.com/document/d/xyz"
    owner: "UX Research"
    tags: ["research", "auth"]

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
    
    default_destinations: ["mixpanel", "amplitude"]  # Apply to all events by default
    
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
      
      - name: "login_failed"
        when: "Authentication fails"
        properties:
          method: "email|google|apple"
          reason: "invalid_credentials|account_locked|network_error"
          attempt_number: "number"
        destinations: ["mixpanel", "amplitude", "warehouse"]  # Override: also send to data warehouse
  
  integrations:
    - name: "Auth0"
      purpose: "OAuth authentication and user management"
      type: "sdk"
      version: "21.0.0"
      provider: "Auth0"
      docs_url: "https://auth0.com/docs/quickstart/spa/react"
    
    - name: "Google Sign-In"
      purpose: "Google OAuth integration"
      type: "sdk"
      version: "1.5.0"
      provider: "Google"
      docs_url: "https://developers.google.com/identity/sign-in/web"

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
      - "oauth_provider: 'google'|'apple'"
    
    outputs:
      - "auth_token: string"
      - "user_id: string"
      - "session_expires_at: timestamp"
    
    side_effects:
      - "Creates user session in backend"
      - "Stores auth token in secure storage"
      - "Emits system events (auth_state_changed)"
      - "Redirects to dashboard on success"
  
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
            message: "Email or password is incorrect"
          - code: 423
            reason: "account_locked"
            message: "Account locked. Check email for unlock instructions"
          - code: 429
            reason: "rate_limit_exceeded"
            message: "Too many attempts. Try again in 15 minutes"
    
    events:
      - name: "auth_state_changed"
        when: "User authentication state changes"
        payload:
          state: "authenticated|unauthenticated"
          user_id: "string|null"
    
    states:
      - name: "form_state"
        transitions:
          - "idle → validating (on submit)"
          - "validating → authenticating (if valid)"
          - "validating → error (if invalid)"
          - "authenticating → authenticated (on success)"
          - "authenticating → error (on failure)"
          - "error → idle (on retry)"
        conditions:
          - "Can submit only in idle state"
          - "Cannot modify inputs during authenticating"
  
  dependencies:
    internal:
      - "component.error_toast"  # For displaying errors
      - "component.loading_spinner"  # For loading states
    external:
      - "Auth0 Authentication API"
      - "Google OAuth 2.0"
      - "Apple Sign In"
  
  observability:
    metrics:
      - "login_attempts_total"
      - "login_failures_by_reason"
      - "auth_api_latency_histogram"
      - "rate_limit_hits"
      - "oauth_callback_duration"
    
    logs:
      - "auth_failure_with_context"
      - "rate_limit_triggered"
      - "session_token_generated"
      - "suspicious_login_attempt"
    
    traces:
      - "auth_flow_complete"
      - "oauth_callback_flow"
      - "session_creation"
    
    slis:
      - "login_success_rate: successful logins / total attempts"
      - "login_latency_p95: 95th percentile authentication time"
    
    slos:
      - "login_success_rate ≥ 99.5%"
      - "login_latency_p95 < 500ms"
    
    alerting:
      critical:
        - "login_success_rate < 95% for 5 minutes → Page on-call"
        - "auth_api_error_rate > 10% for 3 minutes → Page on-call"
      warning:
        - "login_latency_p95 > 1s for 10 minutes → Notify #auth-team"
        - "rate_limit_hits > 100/min → Notify #security-team"
    
    business_impact:
      primary_metric: "daily_active_users"
      dashboard_ref: "{{refs.growth_dashboard.url}}"
      success_criteria: "Login availability directly impacts DAU - 1% login failure = ~1% DAU drop"
    
    correlation:
      join_key: "request_id"
      note: "Attach request_id to both observability traces and analytics events for cross-analysis"
  
  technical_constraints:
    performance:
      response_time: "< 200ms p95 for credential validation"
      throughput: "1000 login requests/sec sustained"
      concurrent_users: "10,000 simultaneous sessions"
      availability: "99.9% uptime (8.7 hours downtime/year)"
    
    security:
      authentication: "OAuth 2.0 + PKCE for social login, bcrypt for passwords"
      authorization: "Session-based with secure httpOnly cookies"
      data_protection: "TLS 1.3 in transit, bcrypt work factor 12 for passwords"
      compliance: "GDPR compliant (consent tracking), SOC 2 Type II"
      threats:
        - "credential_stuffing"
        - "brute_force_attacks"
        - "session_hijacking"
      mitigations:
        - "Rate limiting: 5 attempts per 15 minutes per IP"
        - "CAPTCHA after 3 failed attempts"
        - "Account lockout after 10 failures (24h)"
      data_retention:
        failed_login_attempts: "90 days"
        session_tokens: "30 days after expiry"
        audit_logs: "7 years (compliance)"
    
    technical:
      compatibility: "Safari ≥15, Chrome ≥90, Firefox ≥88, Edge ≥90"
      accessibility: "WCAG 2.2 Level AA - keyboard navigation, screen reader support"
      internationalization: "Support error messages in 10 languages (en, es, fr, de, ja, zh, pt, it, ru, ar)"
  
  validation:
    acceptance_criteria:
      - "User with valid credentials sees dashboard within 2s"
      - "User with invalid credentials sees clear error message"
      - "Rate limiting prevents brute force (6th attempt blocked)"
      - "Locked account shows unlock instructions and support contact"
      - "OAuth login redirects correctly after authorization"
      - "Session persists across browser restarts when 'remember me' checked"
      - "Keyboard-only navigation works for entire flow"
      - "Screen reader announces form errors and success states"
    
    edge_cases:
      - "User changes password on another device during login"
      - "OAuth provider returns error or timeout"
      - "Network failure mid-authentication"
      - "Concurrent logins from multiple devices"
      - "Session expired during OAuth callback"
      - "Browser blocks third-party cookies"
      - "User clicks back button during OAuth flow"
    
    assumptions:
      - "Users have stable internet connection (retry logic handles transient failures)"
      - "Auth0 service has 99.9% uptime SLA"
      - "Users understand standard login UX patterns"
      - "Browser supports JavaScript and localStorage"
      - "Rate limiting is enforced at API gateway layer"
    
    readiness: "ready"
    
    open_questions:
      - "Should we implement exponential backoff for retry throttling?"
      - "What's the optimal session timeout duration (30 min vs 7 days)?"
      - "Do we support WebAuthn/passkeys in v2.1?"

implementation_hints:
  web:
    framework: "React 18 with TypeScript"
    state_management: "Zustand for form state, React Query for API calls"
    form_library: "React Hook Form with Zod validation"
    styling: "Tailwind CSS with HeadlessUI components"
    testing: "Vitest + React Testing Library"
  
  mobile:
    platform: "React Native"
    state: "Redux Toolkit"
    navigation: "React Navigation"
    auth_storage: "react-native-keychain (secure storage)"

evidence:
  user_research: "{{refs.user_research.url}}"
  technical_analysis: "Load testing showed 200ms p95 latency at 1000 req/s"
  design_artifacts: "{{refs.figma_login.url}}"

diagrams:
  - type: "sequence"
    title: "Successful Email Login Flow"
    description: "Happy path for email/password authentication"
    mermaid: |
      sequenceDiagram
        actor U as User
        participant W as Web App
        participant A as Auth API
        participant Auth0
        participant S as Session Service
        
        Note over U,W: Design: {{refs.figma_login.title}}
        U->>W: Enter email/password
        W->>W: Validate format
        W->>A: POST /auth/login
        A->>Auth0: Verify credentials
        Auth0-->>A: Credentials valid
        A->>S: Create session
        S-->>A: Session token
        A-->>W: 200 OK {token, user_id}
        W->>W: Store session
        W-->>U: Redirect to dashboard
        
        Note over W: Analytics: login_succeeded
        Note over A,S: Observability: auth_flow_complete trace
        
        click W "{{refs.figma_login.url}}" "View Design"
        click A "{{refs.auth_epic.url}}" "View Epic"
  
  - type: "flowchart"
    title: "Login Error Handling Decision Tree"
    description: "Logic for handling various authentication errors"
    mermaid: |
      flowchart TD
        Start[Login Attempt] --> ValidFormat{Valid Email?}
        ValidFormat -->|No| FormatErr[Show format error]
        ValidFormat -->|Yes| CheckCreds{Credentials Valid?}
        
        CheckCreds -->|No| IncrAttempts[Increment failed attempts]
        IncrAttempts --> CheckLimit{Attempts < 5?}
        CheckLimit -->|Yes| ShowInvalid[Show invalid credentials]
        CheckLimit -->|No| CheckCaptcha{Attempts < 10?}
        CheckCaptcha -->|Yes| ShowCaptcha[Show CAPTCHA challenge]
        CheckCaptcha -->|No| LockAccount[Lock account 24h]
        
        CheckCreds -->|Yes| CheckLocked{Account Locked?}
        CheckLocked -->|Yes| ShowLocked[Show unlock instructions]
        CheckLocked -->|No| CreateSession[Create session]
        CreateSession --> Success[Login successful]
        
        Success --> End[End]
        FormatErr --> End
        ShowInvalid --> End
        ShowCaptcha --> End
        LockAccount --> End
        ShowLocked --> End
  
  - type: "state"
    title: "Login Form State Machine"
    description: "State transitions for login component"
    mermaid: |
      stateDiagram-v2
        [*] --> Idle
        Idle --> Validating: Submit clicked
        Validating --> Authenticating: Format valid
        Validating --> Error: Format invalid
        Authenticating --> Authenticated: Auth success
        Authenticating --> Error: Auth failed
        Error --> Idle: Retry
        Authenticated --> [*]
        
        note right of Validating: Check email format
        note right of Authenticating: Call Auth API
        note right of Error: Show error toast
```

---

## 🔧 Tooling & Validation

### **File Validation Rules**

1. **Filename matches meta.id**
   ```bash
   # ✅ Valid
   File: component.login_form.yaml
   meta.id: "component.login_form"
   
   # ❌ Invalid
   File: component.login_form.yaml
   meta.id: "login_form"  # Missing level prefix
   ```

2. **File location matches level**
   ```bash
   # ✅ Valid
   specs/system.saas_platform.yaml              # System at root
   specs/containers/container.web_app.yaml       # Container in containers/
   specs/components/web_app/component.login.yaml # Component in components/<container>/
   
   # ❌ Invalid
   specs/component.login.yaml                    # Should be in components/<container>/
   ```

3. **Relationships reference existing specs**
   ```yaml
   # ✅ Valid
   relationships:
     contains:
       - "component.login_form"  # File exists: components/web_app/component.login_form.yaml
   
   # ❌ Invalid
   relationships:
     contains:
       - "login_form"            # Missing level prefix
       - "component.nonexistent" # File doesn't exist
   ```

4. **References have valid URLs or paths**
   ```yaml
   # ✅ Valid
   refs:
     - id: "figma_design"
       url: "https://figma.com/file/xyz"  # Valid HTTPS URL
     - id: "screenshot"
       path: "./assets/login.png"         # Valid relative path
   
   # ❌ Invalid
   refs:
     - id: "bad_ref"
       url: "figma.com/xyz"               # Missing protocol
     - id: "bad_path"
       path: "assets/login.png"           # Missing ./ prefix
   ```

---

## 💡 Interactive Guidance Commands

### When user asks for help:

**Structure & Organization:**
- "Review this spec" → Provide completeness checklist
- "Organize file structure" → Guide through folder hierarchy and naming
- "Fix naming convention" → Correct file naming and meta.id consistency
- "Validate file organization" → Check naming, folder structure, and ID consistency
- "Add hierarchical relationships" → Help define parent-child relationships

**C4 Architecture:**
- "Create system context" → Guide through C4 Level 1 system boundaries and actors
- "Design container architecture" → Help with C4 Level 2 technology and deployment decisions
- "Map system relationships" → Show dependencies and integration points
- "What makes this a container?" → Explain deployment unit criteria

**Planning & Design:**
- "Add user flows" → Guide through actions, success, and error scenarios
- "Define analytics events" → Help structure product analytics tracking
- "Add integrations" → Document third-party SDKs and services
- "Design interface" → Create behavioral contracts and capabilities
- "Add API contracts" → Define endpoints, requests, responses, errors

**Implementation:**
- "Add monitoring" → Suggest relevant metrics, logs, and traces
- "Add alerting" → Define critical and warning alert conditions
- "Add security" → Include appropriate security constraints and threat mitigations
- "Improve error handling" → Add common failure scenarios and edge cases
- "Make it more testable" → Suggest measurable acceptance criteria
- "Add performance goals" → Define response time, throughput, availability targets

**Visualization:**
- "Add sequence diagram" → Guide through interaction flow patterns
- "Show state transitions" → Suggest state diagram with common patterns
- "Document decision logic" → Create flowchart for business rules
- "Visualize architecture" → Create system topology diagram
- "Map user journey" → Build end-to-end experience flow
- "Add C4 diagrams" → Create system context or container diagrams

**Resources & Traceability:**
- "Add design references" → Help create refs for Figma, Sketch files
- "Link project tickets" → Guide through Jira, ClickUp, GitHub issue refs
- "Include screenshots" → Add image references with proper sizing
- "Organize references" → Suggest ref categorization and lifecycle status
- "Add evidence" → Link to user research, technical analysis, design artifacts

**Platform-Specific:**
- "Optimize for mobile" → Add mobile-specific considerations
- "Add web hints" → Provide browser/web implementation guidance
- "Add API hints" → Backend/API specific considerations
- "Add AI/ML hints" → Model/runtime specific guidance

---

## 🎓 Best Practices Summary

### **SpecPlane Philosophy in Action**

✅ **DO:**
- Start with minimal meta (id, purpose, level)
- Progressively add sections as needed
- Use refs to link to external resources
- Keep diagrams focused and connected to refs
- Separate business analytics from technical observability
- Write implementation-agnostic specs with optional hints
- Use exact meta.id values in relationships
- Track assumptions explicitly
- Define clear alerting rules
- Wire observability to business impact

❌ **DON'T:**
- Copy-paste boilerplate without customizing
- Duplicate information across sections
- Hardcode URLs in diagrams (use refs)
- Mix business and technical concerns
- Over-specify implementation details
- Create orphan specs without relationships
- Ignore edge cases and failure modes
- Skip alerting definitions
- Forget to link specs to evidence

### **Quality Checklist**

Before marking a spec as `status: "active"`:
- [ ] Meta fields complete (id, purpose, level, owner)
- [ ] File naming and location correct
- [ ] Refs organized with proper lifecycle status
- [ ] Behavioral contracts defined (interface, APIs, events)
- [ ] Analytics events specified with destinations
- [ ] Observability instrumented (metrics, logs, traces)
- [ ] Alerting rules defined (critical, warning)
- [ ] Security constraints documented
- [ ] Performance targets set
- [ ] Acceptance criteria measurable
- [ ] Edge cases considered
- [ ] Assumptions listed
- [ ] Diagrams reference external resources
- [ ] Evidence links included
- [ ] Relationships to other specs defined

---

**Remember**: SpecPlane specs should be **implementation-agnostic** but **detailed enough** to guide development across any technology stack. Focus on **WHAT** the component should do and **HOW WELL** it should do it, not **HOW** it should be implemented. Use **implementation_hints** sparingly when truly necessary, and always **connect specs to the broader ecosystem** through refs, relationships, and evidence.