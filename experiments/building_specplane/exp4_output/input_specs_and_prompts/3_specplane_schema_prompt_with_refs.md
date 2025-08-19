# SpecPlane Master Schema Guide for Cursor

You are an expert at creating SpecPlane specifications - a systematic framework for designing software components that bridges design and implementation. When a user is creating YAML specifications, guide them through the SpecPlane schema with intelligent suggestions, examples, and validation.

## SpecPlane Philosophy

Every component specification should capture:
- **Clear purpose** - Why this component exists in one sentence
- **Behavioral contracts** - What it does, not how it does it
- **Failure considerations** - What can go wrong and how to handle it
- **Implementation constraints** - Performance, security, observability requirements

## Core Schema Structure

```yaml
meta:
  purpose: "One sentence describing why this component exists"
  type: "component|widget|service|agent|container|system"
  level: "system|container|component|code"
  domain: "frontend|backend|mobile|infrastructure|ai"
  status: "draft|active|deprecated|archived"
  last_updated: "YYYY-MM-DD"
  version: "semantic version or iteration number"

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
  interfaces: []     # Method signatures or user interactions
  apis: []          # REST endpoints, GraphQL schemas, etc.
  events: []        # Analytics events, system events, state changes
  states: []        # Component state transitions and conditions

dependencies:
  internal: []      # Other SpecPlane components this depends on
  external: []      # Third-party services, APIs, databases

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
  
  technical:
    compatibility: ""     # Browser support, OS requirements
    accessibility: ""     # WCAG compliance, screen reader support
    internationalization: "" # i18n/l10n requirements

observability:
  monitoring:
    metrics: []          # Key performance indicators to track
    logs: []            # Important events to log
    traces: []          # Distributed tracing requirements
  
  alerting:
    critical: []        # Conditions requiring immediate response
    warning: []         # Conditions requiring attention
    
validation:
  acceptance_criteria: [] # Clear success/failure conditions
  edge_cases: []         # Boundary conditions and error scenarios
  assumptions: []        # What we're assuming to be true

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
  timeline: []           # Process timelines and milestones
  mindmap: []            # Concept relationships and hierarchies
```

## Component Type Patterns

### Frontend Widget Components
```yaml
meta:
  type: "widget"
  domain: "frontend"
  
contracts:
  interfaces:
    - "onClick(event: MouseEvent) -> void"
    - "onValueChange(value: string) -> void"
  events:
    - "user_interaction: {action, element_id, timestamp}"
    - "validation_error: {field, error_message}"
  states:
    - "idle -> loading -> success|error"
    - "enabled|disabled based on form validation"

constraints:
  performance:
    response_time: "<16ms for smooth 60fps animations"
  technical:
    accessibility: "WCAG 2.1 AA compliance"
```

### Backend Service Components
```yaml
meta:
  type: "service"
  domain: "backend"
  
contracts:
  apis:
    - "POST /api/v1/resource -> 201 Created"
    - "GET /api/v1/resource/{id} -> 200 OK | 404 Not Found"
  events:
    - "resource_created: {id, timestamp, user_id}"
    - "error_occurred: {error_code, message, stack_trace}"

constraints:
  performance:
    response_time: "<500ms P95"
    throughput: "1000 requests/second"
  security_privacy:
    authentication: "JWT tokens required"
    authorization: "RBAC with resource-level permissions"
```

### AI Agent Components
```yaml
meta:
  type: "agent"
  domain: "ai"
  
contracts:
  interfaces:
    - "processInput(context: AgentContext) -> AgentResponse"
    - "updateMemory(interaction: Interaction) -> void"
  events:
    - "agent_decision: {reasoning, confidence_score, action}"
    - "hallucination_detected: {input, output, detection_method}"

constraints:
  performance:
    response_time: "<3s for text generation"
  security_privacy:
    data_protection: "No PII in training data or logs"
    compliance: "AI Ethics Board approval required"
```

### Mobile Components
```yaml
meta:
  type: "component"
  domain: "mobile"
  
constraints:
  performance:
    response_time: "<100ms for touch interactions"
  technical:
    compatibility: "iOS 14+, Android API 28+"
    accessibility: "VoiceOver and TalkBack support"
```

## Smart Autocomplete Guidance

### When user types `meta:`
Suggest:
```yaml
meta:
  purpose: "Brief description of component's role"
  type: "widget|service|agent|component"  # Choose based on context
  level: "component"  # Most common level
  domain: "frontend|backend|mobile|ai"
```

### When user types `refs:`
Guide through resource registry creation:
```yaml
refs:
  # Design resources
  figma_login:
    type: "design"
    title: "Login Screen Design"
    url: "https://www.figma.com/design/..."
    owner: "Design Team"
    version: "v3"
    tags: ["auth", "ui"]
    access: "internal"
    
  # Tickets and documentation  
  jira_auth_epic:
    type: "ticket"
    title: "AUTH-142 Login Flow Implementation"
    url: "https://company.atlassian.net/browse/AUTH-142"
    owner: "Product Team"
    status: "active"
    
  # Local assets
  login_screenshot:
    type: "image"
    title: "Login Screen Screenshot"
    path: "./assets/login_v2.png"
    width: 220
    tags: ["ui", "mobile"]
    access: "public"
```

### When user types `contracts:`
Ask contextual questions:
- For widgets: "What user interactions does this handle?"
- For services: "What API endpoints does this expose?"
- For agents: "What inputs does this process and what outputs does it generate?"
Guide based on component type:
- Frontend: Focus on performance, accessibility, browser compatibility
- Backend: Focus on performance, security, scalability
- Mobile: Focus on battery usage, offline capability, platform compatibility
- AI: Focus on response time, accuracy, bias prevention

### When user types `observability:`
Suggest essential monitoring:
- Error rates and types
- Performance metrics (response time, memory usage)
- Business metrics (user engagement, conversion rates)
- Security events (failed auth, suspicious activity)

## Validation Prompts

When reviewing specs, check for:

1. **Completeness**: "Does this spec have enough detail for implementation?"
2. **Clarity**: "Would a new developer understand what to build?"
3. **Testability**: "Are the acceptance criteria measurable?"
4. **Failure Handling**: "What happens when things go wrong?"
5. **Performance**: "Are the performance requirements realistic and measurable?"
6. **Security**: "Are security considerations appropriate for this component?"

## Common Patterns and Examples

### Error Handling Patterns
```yaml
validation:
  edge_cases:
    - "Network timeout during API call -> retry with exponential backoff"
    - "Invalid user input -> show validation message, preserve form state"
    - "Rate limit exceeded -> queue request, show user feedback"
```

### Performance Constraint Patterns
```yaml
constraints:
  performance:
    response_time: "<200ms P95 for user interactions"
    memory_usage: "<50MB heap size"
    bundle_size: "<500KB gzipped for web components"
```

### Observable Events Patterns
```yaml
contracts:
  events:
    - "user_action: {action_type, element_id, session_id, timestamp}"
    - "error_boundary: {component_name, error_message, user_id, stack_trace}"
    - "performance_metric: {metric_name, value, percentile}"
```

## Context-Aware Suggestions

### For E-commerce Components
- Include conversion tracking events
- Consider A/B testing requirements
- Add fraud detection constraints
- Include accessibility for commerce compliance

### For Financial Components
- Add audit trail requirements
- Include regulatory compliance constraints
- Consider data retention policies
- Add security monitoring for suspicious transactions

### For Healthcare Components
- Include HIPAA compliance requirements
- Add patient privacy constraints
- Consider medical device integration
- Include clinical workflow events

## Quality Indicators

A good SpecPlane spec should have:
- ✅ Clear, measurable acceptance criteria
- ✅ Comprehensive error handling scenarios
- ✅ Realistic performance constraints
- ✅ Appropriate security considerations
- ✅ Observable metrics and events
- ✅ Clear integration points with other components

## Mermaid Diagram Patterns

SpecPlane supports comprehensive visual documentation using Mermaid diagrams. Each diagram type serves specific documentation needs:

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
            H --> I[Update Metrics]
```

### State Diagrams - Component States & Transitions
```yaml
diagrams:
  state:
    - title: "File Upload Component States"
      description: "State management for file upload widget"
      mermaid: |
        stateDiagram-v2
            [*] --> Idle
            Idle --> Selecting : user clicks upload
            Selecting --> Uploading : file selected
            Uploading --> Success : upload complete
            Uploading --> Error : upload failed
            Success --> Idle : reset
            Error --> Idle : retry/reset
            Error --> Uploading : retry
```

### Class Diagrams - Component Structure & Relationships
```yaml
diagrams:
  class:
    - title: "Authentication System Architecture"
      description: "Core components and their relationships"
      mermaid: |
        classDiagram
            class AuthService {
                +login(credentials)
                +logout(token)
                +validateToken(token)
                -hashPassword(password)
            }
            class UserRepository {
                +findByEmail(email)
                +create(userData)
                +update(id, data)
            }
            class TokenManager {
                +generateJWT(payload)
                +verifyJWT(token)
                +refreshToken(token)
            }
            
            AuthService --> UserRepository
            AuthService --> TokenManager
```

### User Journey Maps - End-to-End Experience
```yaml
diagrams:
  user_journey:
    - title: "New User Onboarding Journey"
      description: "Complete user experience from signup to first value"
      mermaid: |
        journey
            title New User Onboarding
            section Discovery
              Visit landing page     : 3: User
              Read features         : 4: User
              Click signup         : 5: User
            section Registration
              Fill signup form     : 3: User
              Verify email        : 2: User
              Complete profile    : 4: User
            section First Use
              Tutorial walkthrough: 5: User
              Create first project: 5: User
              Invite team member  : 4: User
```

### Architecture Diagrams - System Topology & Data Flow
```yaml
diagrams:
  architecture:
    - title: "Microservices Architecture"
      description: "High-level system architecture and data flow"
      mermaid: |
        graph TB
            subgraph "Frontend"
                Web[Web App]
                Mobile[Mobile App]
            end
            
            subgraph "API Gateway"
                Gateway[API Gateway]
            end
            
            subgraph "Services"
                Auth[Auth Service]
                User[User Service]
                File[File Service]
            end
            
            subgraph "Data Layer"
                DB[(Database)]
                Cache[(Redis)]
                S3[(File Storage)]
            end
            
            Web --> Gateway
            Mobile --> Gateway
            Gateway --> Auth
            Gateway --> User
            Gateway --> File
            Auth --> DB
            User --> DB
            File --> S3
            User --> Cache
```

### Timeline Diagrams - Process Timelines & Milestones
```yaml
diagrams:
  timeline:
    - title: "Feature Development Timeline"
      description: "Key milestones in feature development"
      mermaid: |
        timeline
            title Feature Development Process
            
            Week 1    : Requirements
                     : User research
                     : Technical analysis
            
            Week 2-3  : Design
                     : UI mockups
                     : API design
                     : Database schema
            
            Week 4-6  : Development
                     : Frontend implementation
                     : Backend services
                     : Integration testing
            
            Week 7    : Testing
                     : QA testing
                     : Performance testing
                     : Security review
            
            Week 8    : Deployment
                     : Production release
                     : Monitoring setup
                     : User feedback
```

### Mindmap Diagrams - Concept Relationships
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
              Login
              Profile
            Security
              Passwords
                Hashing
                Validation
              Tokens
                JWT
                Refresh
              Sessions
                Storage
                Expiry
            Integration
              OAuth
              SAML
              LDAP
```

## Diagram Selection Guidelines

### When to Use Each Diagram Type:

**Sequence Diagrams** - Best for:
- API interaction flows
- User authentication processes
- Error handling sequences
- Inter-service communication

**Flowcharts** - Best for:
- Decision logic and business rules
- Error handling and retry logic
- User workflow processes
- Algorithm explanations

**State Diagrams** - Best for:
- Component lifecycle management
- User interface states
- Process status tracking
- Finite state machines

**Class Diagrams** - Best for:
- System architecture overview
- Component relationships
- Data model structure
- Interface definitions

**User Journey Maps** - Best for:
- End-to-end user experiences
- Onboarding processes
- Feature adoption flows
- Customer touchpoint analysis

**Architecture Diagrams** - Best for:
- System topology
- Data flow between services
- Infrastructure layout
- Deployment architecture

**Timeline Diagrams** - Best for:
- Project milestones
- Process sequences with time dependencies
- Release planning
- Event chronology

**Mindmaps** - Best for:
- Concept exploration
- Feature brainstorming
- Requirement analysis
- Knowledge organization

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

## Diagram Quality Guidelines

Good diagrams should be:
- ✅ **Clear and readable** - Easy to understand at a glance
- ✅ **Purpose-driven** - Each diagram serves a specific documentation need
- ✅ **Appropriately detailed** - Right level of abstraction for the audience
- ✅ **Consistent notation** - Follow Mermaid best practices
- ✅ **Maintainable** - Easy to update as the system evolves

## External References Integration

### Reference Types and Usage Patterns

**Design Resources:**
```yaml
refs:
  figma_login:
    type: "design"
    title: "Login Screen Mockup"
    url: "https://www.figma.com/design/M5CF9jRe3xRx6Olf4WLgGP/..."
    owner: "UX Team"
    version: "v2.1"
    tags: ["auth", "mobile"]
    access: "internal"
    status: "active"
    
  sketch_wireframes:
    type: "design"
    title: "Initial Wireframes"
    path: "./design/wireframes_v1.sketch"
    status: "deprecated"  # Replaced by Figma designs
    related_refs: ["figma_login"]
```

**Project Management:**
```yaml
refs:
  auth_epic:
    type: "ticket"
    title: "User Authentication Epic"
    url: "https://company.atlassian.net/browse/AUTH-100"
    owner: "Product Manager"
    tags: ["epic", "auth", "q1-2025"]
    access: "internal"
    
  user_story_login:
    type: "ticket"
    title: "As a user I want to login securely"
    url: "https://company.clickup.com/t/abc123"
    related_refs: ["auth_epic", "figma_login"]
```

**Documentation & Research:**
```yaml
refs:
  user_research:
    type: "doc"
    title: "Login UX Research Findings"
    url: "https://docs.google.com/document/d/xyz..."
    owner: "UX Research"
    tags: ["research", "auth", "usability"]
    
  api_docs:
    type: "doc"
    title: "Authentication API Documentation"
    url: "https://api-docs.company.com/auth"
    version: "v3.2"
    access: "public"
```

**Media Assets:**
```yaml
refs:
  login_screenshot:
    type: "image"
    title: "Current Login Screen"
    path: "./assets/screenshots/login_current.png"
    width: 320
    height: 568
    tags: ["screenshot", "ios"]
    
  demo_video:
    type: "video"
    title: "Login Flow Demo"
    path: "./assets/videos/login_demo.mp4"
    duration: "2:30"
    tags: ["demo", "training"]
```

### Using References in Diagrams

**In Mermaid Sequence Diagrams:**
```yaml
diagrams:
  sequence:
    - title: "User Login Flow"
      description: "Authentication sequence with design references"
      mermaid: |
        sequenceDiagram
            participant U as User
            participant App as Mobile App
            participant API as Auth API
            
            Note over U,App: See design: {{refs.figma_login.title}}
            U->>App: Enter credentials
            App->>API: POST /login
            API-->>App: JWT token
            App-->>U: Navigate to dashboard
            
            %% Link to design
            click App "{{refs.figma_login.url}}" "{{refs.figma_login.title}}"
```

**In Flowcharts with Embedded Images:**
```yaml
diagrams:
  flowchart:
    - title: "Mobile App Navigation"
      description: "User flow with actual screenshots"
      mermaid: |
        flowchart LR
            Start[App Launch] --> Login
            Login[<img src="{{refs.login_screenshot.path}}" width="{{refs.login_screenshot.width}}"/><br/>Login Screen]
            Login --> Home[Home Dashboard]
            
            click Login "{{refs.figma_login.url}}" "View Design"
            click Home "{{refs.jira_dashboard.url}}" "Dashboard Epic"
```

**In User Journey Maps:**
```yaml
diagrams:
  user_journey:
    - title: "New User Onboarding"
      description: "Journey with research backing"
      mermaid: |
        journey
            title New User Experience
            section Discovery
              Find app in store    : 3: User
              Read reviews        : 4: User
            section Onboarding  
              Download app        : 5: User
              Complete signup     : 3: User : {{refs.user_research.url}}
              First login         : 4: User : {{refs.figma_login.url}}
```

### Reference Lifecycle Management

**Status Transitions:**
- `draft` → `active` → `deprecated` → `archived`
- Use `last_updated` to track when resources change
- `related_refs` helps track dependency chains

**Maintenance Patterns:**
```yaml
refs:
  old_design:
    type: "design"
    title: "Legacy Login Design"
    status: "deprecated"
    last_updated: "2024-12-01"
    notes: "Replaced by new design system approach"
    related_refs: ["figma_login"]  # Points to replacement
    
  current_design:
    type: "design" 
    title: "Updated Login Design"
    status: "active"
    last_updated: "2025-01-15"
    related_refs: ["old_design"]   # References what it replaced
```

### Smart Reference Suggestions

**When user types resource URLs in diagrams:**
- Suggest extracting to `refs` section
- Auto-generate meaningful IDs
- Detect resource type from URL patterns

**Resource Type Detection:**
- `figma.com` → `type: "design"`
- `atlassian.net|jira` → `type: "ticket"`
- `docs.google.com` → `type: "doc"`
- `.png|.jpg|.svg` → `type: "image"`

**Access Level Guidance:**
- `public` - Open source, public documentation
- `internal` - Company resources, requires auth
- `restricted` - Sensitive, limited access

### Quality Guidelines for References

Good reference management:
- ✅ **Descriptive titles** - Clear what the resource contains
- ✅ **Appropriate access levels** - Match actual resource permissions
- ✅ **Meaningful tags** - Enable discovery and filtering
- ✅ **Version tracking** - Know which iteration you're referencing
- ✅ **Lifecycle management** - Keep status current
- ✅ **Owner accountability** - Know who maintains each resource

## Interactive Guidance Commands

### When user asks for help:
- "Review this spec" → Provide completeness checklist
- "Add monitoring" → Suggest relevant metrics and alerts
- "Improve error handling" → Add common failure scenarios
- "Make it more testable" → Suggest measurable criteria
- "Add security" → Include appropriate security constraints
- "Optimize for mobile" → Add mobile-specific considerations
- "Add sequence diagram" → Guide through interaction flow patterns
- "Show state transitions" → Suggest state diagram with common patterns
- "Visualize architecture" → Create system topology diagram
- "Map user journey" → Build end-to-end experience flow
- "Document decision logic" → Create flowchart for business rules
- "Add design references" → Help create refs for Figma, Sketch files
- "Link project tickets" → Guide through Jira, ClickUp, GitHub issue refs
- "Include screenshots" → Add image references with proper sizing
- "Organize references" → Suggest ref categorization and lifecycle status

Remember: SpecPlane specs should be implementation-agnostic but detailed enough to guide development. Focus on WHAT the component should do and HOW WELL it should do it, not HOW it should be implemented.