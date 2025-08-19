# SpecPlane Master Schema Guide for Cursor

You are an expert at creating SpecPlane specifications - a systematic framework for designing software components that bridges design and implementation. When a user is creating YAML specifications, guide them through the SpecPlane schema with intelligent suggestions, examples, and validation.

## SpecPlane Philosophy

Every component specification should capture:
- **Clear purpose** - Why this component exists in one sentence
- **Behavioral contracts** - What it does, not how it does it
- **Failure considerations** - What can go wrong and how to handle it
- **Implementation constraints** - Performance, security, observability requirements

**Core Principle**: SpecPlane focuses on **WHAT** the component should do and **HOW WELL** it should do it, not **HOW** it should be implemented. This enables the same specification to guide implementations across different technologies, platforms, and programming languages.

## Directory Structure

SpecPlane specs should be organized in a structured directory layout:

```
specplane/
├── specs/
│   ├── system/      # Level: "system" - high-level system context
│   ├── container/   # Level: "container" - deployment units, services
│   ├── component/   # Level: "component" - widgets, modules, libraries
│   ├── code/        # Level: "code" - functions, classes, detailed implementation
│   └── assets/      # Supporting files, images, datasets referenced by specs
├── plugins/         # (future) SpecPlane extensions
└── dashboard/       # (future) SpecPlane visualization tools
```

**Default Behavior**: Auto-suggest directory based on `meta.level`, but users can override as needed. The structure is provided to ease development, not to constrain creativity.

## Core Schema Structure

```yaml
meta:
  id: ""                    # Stable slug for cross-refs (e.g., "auth.login_widget")
  purpose: "One sentence describing why this component exists"
  type: "component|widget|service|agent|container|system"
  level: "system|container|component|code"
  domain: "frontend|backend|mobile|infrastructure|ai"
  owner: ""                 # Team or person responsible
  reviewers: []             # List of required reviewers
  risk: "low|medium|high"   # Risk assessment
  status: "draft|active|deprecated|archived"
  last_updated: "YYYY-MM-DD"
  version: "semantic version or iteration number"
  breaking_changes: []      # List when version bumps are breaking

# C4 Architecture Support (use based on level)
system_context:           # For level: "system"
  actors: []              # Users, external services interacting with system
  external_systems: []    # Other systems this integrates with
  system_boundaries: []   # What's included/excluded from this system
  
container_architecture:   # For level: "container" 
  technology_stack: []    # Technologies used in this container
  deployment_unit: ""     # How this container is deployed
  data_stores: []         # Databases, caches, storage used
  communication: []       # How this container communicates with others
  
relationships:            # For system/container levels - C4 semantics
  depends_on: []          # What this depends on
  used_by: []             # What uses this
  integrates_with: []     # Peer relationships
  contains: []            # Child components/containers

refs:                # Central registry of external resources
  <id>:
    type: "design|ticket|doc|image|video|dataset|api|other"
    title: ""
    url: ""          # for web resources
    path: ""         # for local assets under repo (e.g., ./assets/...)
    version: ""
    owner: ""
    access: "public|internal|restricted"
    tags: []
    notes: ""
    status: "active|deprecated|archived"
    last_updated: "YYYY-MM-DD"
    related_refs: []  # IDs of connected resources

contracts:
  interfaces: []     # Behavioral interactions (language-agnostic)
  apis: []          # HTTP/GraphQL contracts you own or consume
  integrations: []  # SDKs/OS APIs (Firebase, AppleSignIn, PermissionHandler)
  events: []        # Analytics events, system events, state changes
  states: []        # Component state transitions and conditions
  data_models:      # Structured data definitions
    <ModelName>:
      description: ""
      schema:
        type: object
        required: []
        properties: {}

dependencies:             # For component-level wiring
  internal: []           # Other SpecPlane components this depends on
  external: []           # Third-party services, APIs, databases

constraints:
  performance:
    response_time: ""     # e.g., "<200ms P95"
    throughput: ""        # e.g., "1000 req/sec"
    availability: ""      # e.g., "99.9% uptime"
    scalability: ""       # e.g., "horizontal scaling to 10x load"
  
  security_privacy:
    authentication: ""    # Required auth mechanisms
    authorization: ""     # Permission requirements
    data_protection: ""   # PII handling, encryption requirements
    compliance: ""        # GDPR, HIPAA, SOX, etc.
    threats: []          # Security threats to consider
    mitigations: []      # How threats are mitigated
    data_retention: {}   # Data retention policies
    consent:
      policy_ref: ""     # Reference to privacy policy
  
  business:
    cost: ""              # Budget constraints, cost targets
    timeline: ""          # Delivery expectations
    regulatory: ""        # Legal/compliance requirements
    
  technical:
    compatibility: ""     # Browser support, OS requirements
    accessibility: ""     # WCAG compliance, screen reader support
    internationalization: "" # i18n/l10n requirements

observability:
  monitoring:
    slis: []             # Service Level Indicators
      # - name: "login_success_rate"
      #   measure: "successes/attempts"
    slos: []             # Service Level Objectives  
      # - "login_success_rate >= 99.5% / 30d"
    metrics: []          # Key performance indicators to track
    logs: []            # Important events to log
    traces: []          # Distributed tracing requirements
  
  alerting:
    critical: []        # Conditions requiring immediate response
    warning: []         # Conditions requiring attention
    
  audit: []             # Audit trail requirements
    # - "user_consent_changed{uid, ts, source}"
    
validation:
  acceptance_criteria: [] # Clear success/failure conditions
  edge_cases: []         # Boundary conditions and error scenarios
  assumptions: []        # What we're assuming to be true

implementation_hints:   # Optional technology-specific guidance
  web: {}              # Browser/web-specific considerations
  mobile: {}           # Mobile platform considerations  
  api: {}              # Backend/API specific considerations
  desktop: {}          # Desktop application considerations
  ai: {}               # AI/ML model/runtime specifics

evidence:
  user_research: ""      # Links to user interviews, surveys
  technical_analysis: "" # Performance testing, security review
  design_artifacts: ""   # Mockups, prototypes, diagrams

diagrams:
  sequence: []           # Interaction flows between components/actors
  flowchart: []          # Decision trees, process flows
  state: []              # State machines and transitions  
  class: []              # Component relationships and structure
  user_journey: []       # End-to-end user experience flows
  architecture: []       # System topology and data flow
  system_context: []     # C4 Level 1 - System context diagrams
  container: []          # C4 Level 2 - Container diagrams
  component: []          # C4 Level 3 - Component diagrams
  timeline: []           # Process timelines and milestones
  mindmap: []            # Concept relationships and hierarchies

rendering:             # Template and visualization hints
  placeholders:
    syntax: "{{refs.<id>.<field>}}"
    fields: ["url", "path", "title", "width", "height"]
    on_missing: "warn"   # error|warn|skip

validation_rules:      # Schema validation guidance
  required_by_level:
    system: ["meta", "system_context", "relationships"]
    container: ["meta", "container_architecture", "relationships"] 
    component: ["meta", "contracts", "constraints", "observability", "validation"]
    code: ["meta", "contracts", "dependencies"]
  conventions:
    wiring:
      component_level: "use dependencies.internal/external"
      system_container_level: "use relationships.depends_on/used_by/integrates_with/contains"
```

## Component Type Patterns

### System Level (C4 Level 1)
```yaml
meta:
  type: "system"
  level: "system"
  
system_context:
  actors: ["End Users", "Administrators", "External APIs"]
  external_systems: ["Payment Gateway", "Email Service", "Analytics Platform"]
  system_boundaries: ["User Management", "Core Business Logic", "Data Storage"]
  
relationships:
  integrates_with: ["payment_gateway", "email_service"]
  contains: ["web_app_container", "api_container", "database_container"]
```

### Container Level (C4 Level 2)
```yaml
meta:
  type: "container"
  level: "container"
  
container_architecture:
  technology_stack: ["React", "Node.js", "PostgreSQL", "Redis"]
  deployment_unit: "Docker container in Kubernetes"
  data_stores: ["user_profiles_db", "session_cache"]
  communication: ["REST APIs", "WebSocket connections"]
  
relationships:
  depends_on: ["database_container", "cache_container"]
  used_by: ["web_frontend", "mobile_app"]
```

### Frontend Widget Components
```yaml
meta:
  type: "widget"
  level: "component"
  domain: "frontend"

contracts:
  interfaces:
    - "onSubmit(credentials) -> Promise<AuthResult>"
    - "onError(error) -> void"
    - "onStateChange(state) -> void"
  
  integrations:
    - "Firebase Auth SDK"
    - "AppleSignIn API"
    - "GoogleSignIn API"
  
  events:
    - "login_attempt{provider, method}"
    - "login_success{provider, user_id}"
    - "login_failure{provider, error_code}"
  
  states:
    - "idle -> loading (user submits)"
    - "loading -> success (auth succeeds)"
    - "loading -> error (auth fails)"
    - "error -> idle (user retries)"

constraints:
  performance:
    response_time: "<500ms for form submission"
  
  security_privacy:
    threats: ["Credential stuffing", "Session hijacking"]
    mitigations: ["Rate limiting", "Secure cookie handling"]
    data_retention:
      credentials: "never stored client-side"
      session_tokens: "cleared on logout or 24h expiry"
```

### Backend Service Components
```yaml
meta:
  type: "service"
  level: "component"
  domain: "backend"

contracts:
  apis:
    - "POST /auth/login -> {token, user, expires}"
    - "POST /auth/refresh -> {token, expires}"
    - "POST /auth/logout -> {success}"
  
  integrations:
    - "Firebase Admin SDK"
    - "JWT library"
    - "Rate limiting service"
  
  data_models:
    AuthRequest:
      description: "Login request payload"
      schema:
        type: object
        required: [provider, credentials]
        properties:
          provider: { type: string, enum: [google, apple, email] }
          credentials: { type: object }
    
    AuthResult:
      description: "Authentication response"
      schema:
        type: object
        required: [success, token]
        properties:
          success: { type: boolean }
          token: { type: string }
          user: { $ref: "#/definitions/User" }

observability:
  monitoring:
    slis:
      - name: "auth_success_rate"
        measure: "successful_auths / total_auth_attempts"
      - name: "auth_latency_p95"
        measure: "95th percentile authentication time"
    slos:
      - "auth_success_rate >= 99.5% over 30 days"
      - "auth_latency_p95 <= 200ms over 30 days"
```

### AI Agent Components
```yaml
meta:
  type: "agent"
  level: "component"
  domain: "ai"

contracts:
  interfaces:
    - "processQuery(input) -> Promise<Response>"
    - "updateContext(context) -> void"
  
  integrations:
    - "OpenAI API"
    - "Vector database"
    - "Content moderation service"

constraints:
  performance:
    response_time: "<3s for simple queries"
    cost: "<$0.01 per interaction"
  
  security_privacy:
    threats: ["Prompt injection", "Data leakage", "Harmful content generation"]
    mitigations: ["Input sanitization", "Output filtering", "Content moderation"]
    data_retention:
      conversation_history: "7 days for debugging, then deleted"
      training_data: "opt-in only, anonymized"

observability:
  monitoring:
    slis:
      - name: "response_quality_score"
        measure: "user_thumbs_up / total_responses"
      - name: "safety_violation_rate" 
        measure: "flagged_responses / total_responses"
    slos:
      - "response_quality_score >= 85% over 7 days"
      - "safety_violation_rate <= 0.1% over 7 days"
```

## Best Practices for SpecPlane Creation

### 1. Start with Purpose and Constraints
Always begin by clearly defining why the component exists and what limits it must operate within.

### 2. Design Contracts Before Implementation
Focus on behavioral interfaces that transcend specific technologies.

### 3. Consider Failure Modes Early
Think through edge cases, error scenarios, and recovery strategies.

### 4. Make Observability Concrete
Define specific SLIs/SLOs rather than vague monitoring requirements.

### 5. Security by Design
Include threat modeling and mitigation strategies from the start.

### 6. Use References Liberally
Link to designs, tickets, documentation, and related components to create coherent system documentation.

### 7. Validate Iteratively
Use the validation section to define clear acceptance criteria and test scenarios.

## Comprehensive Mermaid Diagram Support

SpecPlane supports all major Mermaid diagram types for visual system documentation.

### Sequence Diagrams - Interaction Flows
```yaml
diagrams:
  sequence:
    - title: "User Login Flow"
      description: "Complete authentication sequence"
      mermaid: |
        sequenceDiagram
            participant U as User
            participant F as Frontend
            participant A as AuthService
            participant D as Database
            
            U->>F: Enter credentials
            F->>A: POST /login
            A->>D: Validate user
            D-->>A: User data
            A-->>F: JWT token
            F-->>U: Redirect to dashboard
            
            click F "{{refs.figma_login.url}}" "Login Design"
            click A "{{refs.auth_api_docs.url}}" "API Documentation"
```

### Flowchart Diagrams - Decision Trees & Process Flows
```yaml
diagrams:
  flowchart:
    - title: "Error Handling Flow"
      description: "How the component handles various error scenarios"
      mermaid: |
        flowchart TD
            A[Request Received] --> B{Valid Input?}
            B -->|Yes| C[Process Request]
            B -->|No| D[Return Validation Error]
            C --> E{Service Available?}
            E -->|Yes| F[Return Success]
            E -->|No| G[Return Service Error]
            D --> H[Log Error]
            G --> H
            H --> I[End]
            F --> I
```

### State Diagrams - Component States & Transitions
```yaml
diagrams:
  state:
    - title: "Login Widget States"
      description: "State machine for authentication widget"
      mermaid: |
        stateDiagram-v2
            [*] --> Idle
            Idle --> Loading : submitCredentials()
            Loading --> Success : authSuccess()
            Loading --> Error : authFailure()
            Error --> Idle : retry()
            Success --> [*]
            
            Loading : Validating credentials
            Error : Show error message
            Success : Redirect user
```

### Class Diagrams - Component Structure & Relationships
```yaml
diagrams:
  class:
    - title: "Authentication System Architecture"
      description: "Key components and their relationships"
      mermaid: |
        classDiagram
            class LoginWidget {
                +String email
                +String password
                +Boolean loading
                +submit()
                +reset()
                +validateInput()
            }
            
            class AuthService {
                +login(credentials)
                +logout()
                +refreshToken()
                +validateSession()
            }
            
            class UserStore {
                +User currentUser
                +String sessionToken
                +setUser(user)
                +clearSession()
            }
            
            LoginWidget --> AuthService : uses
            AuthService --> UserStore : updates
```

### User Journey Maps - End-to-End Experience Flows
```yaml
diagrams:
  user_journey:
    - title: "New User Registration Journey"
      description: "Complete onboarding experience"
      mermaid: |
        journey
            title User Registration Journey
            section Discovery
              Visit landing page: 5: User
              Read features: 4: User
              Click sign up: 5: User
            section Registration
              Fill form: 3: User
              Verify email: 2: User
              Complete profile: 4: User
            section First Use
              Take tutorial: 4: User
              Create first project: 5: User
              Invite team member: 3: User
```

### Architecture Diagrams - System Topology & Data Flow
```yaml
diagrams:
  architecture:
    - title: "Microservices Architecture"
      description: "System-level component relationships"
      mermaid: |
        graph TB
            subgraph "Frontend Layer"
                UI[Web App]
                Mobile[Mobile App]
            end
            
            subgraph "API Gateway"
                Gateway[Load Balancer]
            end
            
            subgraph "Service Layer"
                Auth[Auth Service]
                User[User Service]
                Data[Data Service]
            end
            
            subgraph "Data Layer"
                DB[(Database)]
                Cache[(Redis Cache)]
            end
            
            UI --> Gateway
            Mobile --> Gateway
            Gateway --> Auth
            Gateway --> User
            Gateway --> Data
            Auth --> DB
            User --> DB
            Data --> DB
            Auth --> Cache
```

### C4 System Context Diagrams
```yaml
diagrams:
  system_context:
    - title: "E-commerce Platform Context"
      description: "System boundary and external actors"
      mermaid: |
        C4Context
            title System Context diagram for E-commerce Platform
            
            Person(customer, "Customer", "Browses and purchases products")
            Person(admin, "Administrator", "Manages products and orders")
            
            System(ecommerce, "E-commerce Platform", "Allows customers to purchase products online")
            
            System_Ext(payment, "Payment Gateway", "Processes credit card payments")
            System_Ext(email, "Email System", "Sends transactional emails")
            System_Ext(analytics, "Analytics Platform", "Tracks user behavior")
            
            Rel(customer, ecommerce, "Uses")
            Rel(admin, ecommerce, "Administers")
            Rel(ecommerce, payment, "Makes payment requests")
            Rel(ecommerce, email, "Sends emails")
            Rel(ecommerce, analytics, "Sends events")
```

### C4 Container Diagrams
```yaml
diagrams:
  container:
    - title: "E-commerce Platform Containers"
      description: "High-level technology choices"
      mermaid: |
        C4Container
            title Container diagram for E-commerce Platform
            
            Person(customer, "Customer")
            
            Container(web, "Web Application", "React.js", "Delivers content and handles user interactions")
            Container(api, "API Gateway", "Node.js/Express", "Provides JSON/HTTPS API")
            Container(auth, "Auth Service", "Python/FastAPI", "Handles authentication and authorization")
            Container(catalog, "Product Catalog", "Java/Spring", "Manages product information")
            
            ContainerDb(db, "Database", "PostgreSQL", "Stores user accounts, products, orders")
            ContainerDb(cache, "Cache", "Redis", "Caches frequently accessed data")
            
            System_Ext(payment, "Payment Gateway")
            
            Rel(customer, web, "Uses", "HTTPS")
            Rel(web, api, "Makes API calls", "JSON/HTTPS")
            Rel(api, auth, "Validates tokens", "gRPC")
            Rel(api, catalog, "Gets product data", "JSON/HTTP")
            Rel(auth, db, "Reads/writes", "SQL")
            Rel(catalog, db, "Reads/writes", "SQL")
            Rel(api, cache, "Reads/writes", "Redis Protocol")
            Rel(api, payment, "Processes payments", "HTTPS")
```

### Timeline Diagrams - Process Timelines & Milestones
```yaml
diagrams:
  timeline:
    - title: "Product Development Timeline"
      description: "Key milestones and phases"
      mermaid: |
        timeline
            title Product Development Lifecycle
            
            section Planning
                Requirements : User research
                           : Market analysis
                           : Technical feasibility
                Design     : UI/UX mockups
                           : System architecture
                           : API design
            
            section Development
                Sprint 1   : Auth system
                           : User management
                Sprint 2   : Core features
                           : Integration testing
                Sprint 3   : Performance optimization
                           : Security hardening
            
            section Launch
                Beta       : Closed beta testing
                           : Bug fixes
                Production : Public launch
                           : Monitoring setup
```

### Mindmap Diagrams - Concept Relationships & Hierarchies
```yaml
diagrams:
  mindmap:
    - title: "Authentication System Concepts"
      description: "Key concepts and their relationships"
      mermaid: |
        mindmap
          root((Authentication))
            Users
              Registration
                Email verification
                Profile creation
                Terms acceptance
              Login
                Credentials
                OAuth providers
                Multi-factor auth
              Profile Management
                Update info
                Password change
                Account deletion
            Security
              Encryption
                Password hashing
                Token encryption
                Data at rest
              Authorization
                Role-based access
                Permissions
                Resource protection
              Compliance
                GDPR
                Privacy policies
                Audit trails
            Integration
              Frontend
                Login forms
                Session management
                Error handling
              Backend
                API endpoints
                Database schema
                External services
```

## Smart Diagram Suggestions

### When user types `diagrams:`
Suggest based on component type:

**For Frontend Widgets:**
```yaml
diagrams:
  state:
    - title: "Widget State Management"
      description: "Component states and user interactions"
  user_journey:
    - title: "User Interaction Flow"
      description: "How users interact with this widget"
```

**For Backend Services:**
```yaml
diagrams:
  sequence:
    - title: "API Request Flow"
      description: "Request processing sequence"
  architecture:
    - title: "Service Dependencies"
      description: "How this service integrates with others"
```

**For AI Agents:**
```yaml
diagrams:
  flowchart:
    - title: "Decision Making Process"
      description: "Agent reasoning and decision flow"
  sequence:
    - title: "Agent Interaction Pattern"
      description: "How agent processes inputs and generates outputs"
```

**For Mobile Components:**
```yaml
diagrams:
  state:
    - title: "App State Management"
      description: "Screen states and navigation"
  user_journey:
    - title: "Mobile User Experience"
      description: "Touch interactions and gestures"
```

**For System/Container Level:**
```yaml
diagrams:
  system_context:
    - title: "System Boundary"
      description: "External actors and systems"
  container:
    - title: "Technology Architecture"
      description: "Deployment containers and communication"
```

## Context-Aware Suggestions

### For E-commerce Components
- Include conversion tracking events
- Consider A/B testing requirements
- Add fraud detection constraints
- Include accessibility for commerce compliance
- Add payment flow sequence diagrams
- Include user journey maps for purchase flows

### For Financial Components
- Add audit trail requirements
- Include regulatory compliance constraints
- Consider data retention policies
- Add security monitoring for suspicious transactions
- Include compliance flowcharts
- Add risk assessment diagrams

### For Healthcare Components
- Include HIPAA compliance requirements
- Add patient privacy constraints
- Consider medical device integration
- Include clinical workflow events
- Add patient journey maps
- Include medical workflow sequence diagrams

### For AI/ML Components
- Include model performance monitoring
- Add bias detection and mitigation
- Consider explainability requirements
- Include safety and ethical constraints
- Add decision tree flowcharts
- Include training pipeline diagrams

## Comprehensive Component Examples

### Frontend Widget (Complete Example)
```yaml
meta:
  id: "ui.voice_recorder_widget"
  purpose: "Voice recording widget with real-time visualization and playback controls"
  type: "widget"
  level: "component"
  domain: "frontend"
  owner: "UI Team"
  reviewers: ["UX Lead", "Accessibility Expert"]
  risk: "medium"
  status: "active"
  last_updated: "2025-01-19"
  version: "2.1.0"

refs:
  figma_design:
    type: "design"
    title: "Voice Recorder Widget Design"
    url: "https://figma.com/file/voice-recorder"
    owner: "Design Team"
    status: "active"
    last_updated: "2025-01-15"
  
  accessibility_guide:
    type: "doc"
    title: "Voice UI Accessibility Guidelines"
    url: "https://company.com/docs/accessibility/voice"
    access: "internal"
    status: "active"

contracts:
  interfaces:
    - "onRecordingStart() -> void"
    - "onRecordingStop() -> Promise<AudioBlob>"
    - "onPlayback(audioBlob) -> void"
    - "onError(error) -> void"
  
  integrations:
    - "Web Audio API"
    - "MediaRecorder API"
    - "Browser permissions API"
  
  events:
    - "recording_started{session_id, user_id, timestamp}"
    - "recording_stopped{session_id, duration_ms, file_size_bytes}"
    - "playback_started{session_id, audio_id}"
    - "permission_denied{permission_type, user_agent}"
  
  states:
    - "idle -> recording (user clicks record)"
    - "recording -> processing (user clicks stop)"
    - "processing -> ready (audio processed)"
    - "ready -> playing (user clicks play)"
    - "playing -> ready (playback ends)"
    - "* -> error (permission denied or technical failure)"
  
  data_models:
    AudioRecording:
      description: "Recorded audio data and metadata"
      schema:
        type: object
        required: [id, blob, duration, created_at]
        properties:
          id: { type: string }
          blob: { type: object, description: "Audio Blob object" }
          duration: { type: number, description: "Duration in milliseconds" }
          format: { type: string, enum: [webm, mp4, wav] }
          created_at: { type: string, format: date-time }
    
    RecordingState:
      description: "Current state of the recording widget"
      schema:
        type: string
        enum: [idle, recording, processing, ready, playing, error]

dependencies:
  internal: []
  external: ["browser_audio_apis"]

constraints:
  performance:
    response_time: "<100ms for state transitions"
    memory_usage: "<10MB for 5min recording"
    file_size: "<1MB per minute of audio"
  
  security_privacy:
    authentication: "Not required for recording"
    authorization: "Microphone permission required"
    data_protection: "Audio data never sent to server without explicit consent"
    compliance: "WCAG 2.1 AA compliance for accessibility"
    threats: ["Unauthorized recording", "Data exfiltration"]
    mitigations: ["Explicit permission requests", "Visual recording indicators"]
    data_retention:
      local_recordings: "Cleared on page refresh unless explicitly saved"
    consent:
      policy_ref: "{{refs.privacy_policy.url}}"
  
  technical:
    compatibility: "Chrome 60+, Firefox 55+, Safari 14+"
    accessibility: "Screen reader support, keyboard navigation"
    internationalization: "Supports RTL languages, localizable messages"

observability:
  monitoring:
    slis:
      - name: "recording_success_rate"
        measure: "successful_recordings / attempted_recordings"
      - name: "permission_grant_rate"
        measure: "permissions_granted / permissions_requested"
    slos:
      - "recording_success_rate >= 95% over 7 days"
      - "permission_grant_rate >= 80% over 30 days"
    metrics:
      - "recording_duration_histogram"
      - "file_size_distribution"
      - "browser_compatibility_breakdown"
    logs:
      - "recording_lifecycle{state, timestamp, session_id}"
      - "permission_flow{result, browser, timestamp}"
  
  alerting:
    critical:
      - "recording_success_rate < 90% for 1 hour"
    warning:
      - "permission_grant_rate < 70% for 24 hours"
  
  audit:
    - "microphone_access_requested{user_id, granted, timestamp}"

validation:
  acceptance_criteria:
    - "User can start recording with single click/tap"
    - "Visual indicator shows recording is active"
    - "Recording stops automatically after 10 minutes"
    - "User can play back recorded audio immediately"
    - "Widget gracefully handles permission denial"
    - "Works consistently across supported browsers"
  
  edge_cases:
    - scenario: "Microphone permission denied"
      expected: "Show clear message with instructions to enable"
    - scenario: "Recording while audio is playing"
      expected: "Stop playback and start recording"
    - scenario: "Browser tab becomes inactive during recording"
      expected: "Continue recording, show notification on return"
    - scenario: "Maximum recording time reached"
      expected: "Auto-stop and notify user"
  
  assumptions:
    - "Users have working microphone hardware"
    - "Browser supports modern Web Audio APIs"
    - "Users understand recording privacy implications"

implementation_hints:
  web:
    framework_suggestions: "Works with React, Vue, Angular, or vanilla JS"
    performance_tips: "Use Web Workers for audio processing"
    accessibility_notes: "Implement proper ARIA labels and live regions"

evidence:
  user_research: "{{refs.voice_ui_research.url}}"
  technical_analysis: "{{refs.audio_performance_study.url}}"
  design_artifacts: "{{refs.figma_design.url}}"

diagrams:
  state:
    - title: "Recording Widget State Machine"
      description: "All possible states and transitions"
      mermaid: |
        stateDiagram-v2
            [*] --> Idle
            Idle --> Recording : startRecording()
            Recording --> Processing : stopRecording()
            Processing --> Ready : processingComplete()
            Ready --> Playing : playAudio()
            Playing --> Ready : playbackEnded()
            Ready --> Recording : startNewRecording()
            
            Idle --> Error : permissionDenied()
            Recording --> Error : technicalFailure()
            Processing --> Error : processingFailed()
            Error --> Idle : resetWidget()
  
  sequence:
    - title: "Recording Flow with Permissions"
      description: "Complete user interaction sequence"
      mermaid: |
        sequenceDiagram
            participant U as User
            participant W as Widget
            participant B as Browser
            participant A as Audio API
            
            U->>W: Click record button
            W->>B: Request microphone permission
            B-->>U: Show permission dialog
            U->>B: Grant permission
            B-->>W: Permission granted
            W->>A: Start recording
            A-->>W: Recording started
            W-->>U: Show recording indicator
            
            U->>W: Click stop button
            W->>A: Stop recording
            A-->>W: Audio blob ready
            W-->>U: Show playback controls
            
            click W "{{refs.figma_design.url}}" "View Design"

rendering:
  placeholders:
    syntax: "{{refs.<id>.<field>}}"
    fields: ["url", "path", "title", "width", "height"]
    on_missing: "warn"

validation_rules:
  required_by_level:
    system: ["meta", "system_context", "relationships"]
    container: ["meta", "container_architecture", "relationships"] 
    component: ["meta", "contracts", "constraints", "observability", "validation"]
    code: ["meta", "contracts", "dependencies"]
  conventions:
    wiring:
      component_level: "use dependencies.internal/external"
      system_container_level: "use relationships.depends_on/used_by/integrates_with/contains"
```

## Quality Indicators

A good SpecPlane spec should have:
- ✅ Clear, measurable acceptance criteria
- ✅ Comprehensive error handling scenarios
- ✅ Realistic performance constraints
- ✅ Appropriate security considerations
- ✅ Observable metrics and events
- ✅ Clear integration points with other components
- ✅ Visual documentation through diagrams
- ✅ Proper reference management
- ✅ Technology-agnostic behavioral contracts

## Interactive Guidance Commands

### When user asks for help:
- "Add sequence diagram" → Guide through interaction flow patterns
- "Show state transitions" → Suggest state diagram with common patterns
- "Visualize architecture" → Create system topology diagram
- "Map user journey" → Build end-to-end experience flow
- "Document decision logic" → Create flowchart for business rules
- "Add C4 diagrams" → Guide through system context and container views
- "Include security threats" → Suggest common threats for component type
- "Define SLIs/SLOs" → Help create measurable service levels

## Common Patterns and Examples

### Error Handling Patterns
```yaml
validation:
  edge_cases:
    - "Network timeout during API call -> retry with exponential backoff"
    - "Invalid user input -> show validation message, preserve form state"
    - "Rate limit exceeded -> queue request, show user feedback"
    - "Service unavailable -> show graceful degradation message"
```

### Performance Constraint Patterns
```yaml
constraints:
  performance:
    response_time: "<200ms P95 for user interactions"
    memory_usage: "<50MB heap size"
    bundle_size: "<500KB gzipped for web components"
    throughput: "Handle 1000 concurrent users"
```

### Observable Events Patterns
```yaml
contracts:
  events:
    - "user_action: {action_type, element_id, session_id, timestamp}"
    - "error_boundary: {component_name, error_message, user_id, stack_trace}"
    - "performance_metric: {metric_name, value, percentile}"
    - "business_event: {event_type, entity_id, metadata}"
```

### Security Patterns
```yaml
constraints:
  security_privacy:
    threats:
      - "Cross-site scripting (XSS)"
      - "SQL injection"
      - "Authentication bypass"
      - "Data exfiltration"
    mitigations:
      - "Input sanitization and validation"
      - "Parameterized queries"
      - "Multi-factor authentication"
      - "Data encryption in transit and at rest"
```

## Reference Usage in Diagrams
```yaml
diagrams:
  sequence:
    - title: "OAuth Login Flow"
      mermaid: |
        sequenceDiagram
          participant U as User
          participant L as Login Widget
          participant F as Firebase Auth
          
          U->>L: Enter credentials
          L->>F: Authenticate
          F-->>L: Auth token
          L-->>U: Success
          
          click L "{{refs.figma_login.url}}" "View Design"
          click F "{{refs.firebase_docs.url}}" "API Documentation"

refs:
  figma_login:
    type: "design"
    title: "Login Widget Design"
    url: "https://figma.com/file/..."
    owner: "Design Team"
    status: "active"
  
  firebase_docs:
    type: "doc"
    title: "Firebase Auth Documentation"
    url: "https://firebase.google.com/docs/auth"
    access: "public"
```

### Data Model Definitions
```yaml
contracts:
  data_models:
    User:
      description: "Authenticated user profile"
      schema:
        type: object
        required: [uid, email, created_at]
        properties:
          uid: 
            type: string
            description: "Unique user identifier"
          email:
            type: string
            format: email
            description: "User's email address"
          display_name:
            type: string
            description: "User's display name"
          created_at:
            type: string
            format: date-time
            description: "Account creation timestamp"
          
    LoginState:
      description: "Current state of login component"
      schema:
        type: string
        enum: [idle, loading, success, error]
        description: "Tracks user interaction state"
```

### Comprehensive Error Handling
```yaml
validation:
  edge_cases:
    - scenario: "Network timeout during authentication"
      expected: "Show retry button with exponential backoff"
    - scenario: "Invalid credentials provided"
      expected: "Clear error message without revealing account existence"
    - scenario: "Account locked due to too many failures"
      expected: "Show account recovery options"
    - scenario: "OAuth provider temporarily unavailable"
      expected: "Disable provider button with status message"

constraints:
  security_privacy:
    threats:
      - "Brute force password attacks"
      - "Credential stuffing from breached databases"
      - "Session token theft"
    mitigations:
      - "Rate limiting: 5 attempts per minute per IP"
      - "Account lockout after 10 failed attempts"
      - "Secure HTTP-only cookies for session management"
```

## Validation and Quality Assurance

When creating specifications, ensure:

1. **Completeness**: All required sections for the component level are present
2. **Clarity**: Purpose and interfaces are unambiguous
3. **Testability**: Acceptance criteria are measurable
4. **Maintainability**: References and relationships are clearly defined
5. **Security**: Threats and mitigations are considered
6. **Observability**: Monitoring and alerting are concrete

## File Naming Conventions

- Use snake_case for filenames
- Include component type: `login_widget.yaml`, `auth_service.yaml`
- For system/container level: `user_management_system.yaml`, `api_gateway_container.yaml`
- Place in appropriate `specplane/specs/` subdirectory based on `meta.level`

Remember: SpecPlane specifications should be technology-agnostic behavioral contracts that can guide implementation across different platforms while ensuring quality, security, and observability from the start.