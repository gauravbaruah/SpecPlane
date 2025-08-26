# SpecPlane Core Prompts

This directory contains the master schema definitions and guidance for creating SpecPlane specifications. The core prompts serve as the **control plane for specifications**, ensuring that all components are described in a consistent, machine-readable, and AI-ready way.

SpecPlane prompts are especially powerful in AI-assisted development: they ensure that generated code follows specified requirements whenever available, rather than drifting from design intent. By capturing design, architecture, and observability in one schema, they reduce the burden of spec-to-code drift as systems evolve.

## Schema & Examples Overview

### Schema Definitions

- **`specplane_schema_prompt_v5.5.1_balanced.md`** - The current production schema (RECOMMENDED)
  - Optimized balance of comprehensiveness and usability
  - Proven through experimental validation
  - Includes smart constraints to prevent complexity bloat
  - Enhanced with business metrics and observability patterns

- **`specplane_schema_prompt_v7_detailed.md`** - Extended schema with advanced features
  - More comprehensive business metrics tracking
  - Advanced compliance and governance features
  - Detailed organizational workflow integration
  - (Possibly) Use for enterprise or heavily regulated environments

### Usage Instructions

- **`README_START_HERE.md`** - Quick setup guide for AI development tools
  - How to load the schema into your development session
  - Basic workflow for creating specifications
  - Integration with Cursor and other AI assistants

### Example Patterns

- **`spec_validation_prompt_examples.md`** - Validation and review prompts
  - How to validate existing specifications
  - Gap analysis techniques
  - Quality improvement suggestions

- **`widget_spec_examples.md`** - Component specification examples
  - Login widget with OAuth integration
  - Onboarding flow specifications
  - Real-world component patterns

## How to Use These Prompts

### For AI Development Tools (Cursor, Claude, etc.)

1. **Load the Schema**: Start your session by referencing the schema prompt:
   ```
   Please review and remember the instructions in @specplane_schema_prompt_v5.5.1_balanced.md
   ```

2. **Generate Specifications**: Use the schema to create component specs:
   ```
   Create a SpecPlane specification for a login widget with OAuth support
   ```

3. **Validate and Improve**: Use validation prompts to review your specs:
   ```
   Can you validate this spec and find any gaps we need to address?
   ```

### Schema Selection Guide

**Use v5.5.1 (Balanced) when:**
- Creating specifications for most development teams
- Need proven patterns with good usability
- Want built-in constraints to prevent over-engineering
- Building MVPs or iterative development

**Use v7 (Detailed) when:**
- Working in regulated industries (healthcare, finance)
- Need comprehensive business metrics tracking
- Require detailed compliance documentation
- Building large enterprise systems

## Core Schema Philosophy

SpecPlane specifications focus on **behavioral contracts** rather than implementation details:

- **What** the component should do (capabilities)
- **How well** it should perform (constraints and SLOs)
- **What can go wrong** (edge cases and error handling)
- **How success is measured** (acceptance criteria and metrics)

Beyond technical contracts, SpecPlane enables teams to align **product, design, engineering, and observability** responsibilities in one shared artifact, ensuring clarity across disciplines.

### Key Sections Explained

**`meta`** - Component identification and ownership
**`contracts`** - Behavioral capabilities, APIs, events, and state transitions
**`constraints`** - Performance, security, and technical requirements
**`observability`** - Monitoring, alerting, and business metrics
**`validation`** - Acceptance criteria and edge cases
**`diagrams`** - Mermaid-based visual documentation

## C4 Architecture Integration

SpecPlane uses the C4 model for architectural specifications:

- **System Level** (`level: "system"`) - High-level system context and boundaries
- **Container Level** (`level: "container"`) - Services, databases, deployment units
- **Component Level** (`level: "component"`) - Features, widgets, modules
- **Code Level** (`level: "code"`) - Functions, classes, detailed implementation

## Best Practices

### 1. Start with Purpose and Constraints
Define why the component exists and its operating limits before detailing behavior.

### 2. Focus on Observable Behavior
Describe what users and other systems can observe, not internal implementation.

### 3. Consider Failure Modes Early
Think through what can go wrong and how to handle it before implementation.

### 4. Make Requirements Testable
Every acceptance criterion should be measurable and verifiable.

### 5. Link to External Resources
Use the `refs` section to connect specifications to designs, tickets, and documentation.

## Example Component Types

### Frontend Widgets
```yaml
meta:
  type: "widget"
  domain: "frontend"
contracts:
  capabilities:
    - "User authentication via OAuth providers"
    - "Display validation errors with clear messaging"
constraints:
  performance:
    response_time: "<200ms for UI interactions"
  technical:
    accessibility: "WCAG 2.1 AA compliance"
```

### Backend Services
```yaml
meta:
  type: "service"
  domain: "backend"
contracts:
  apis:
    - "POST /auth/login -> {token, user, expires}"
  events:
    - "user_authenticated: {user_id, provider, timestamp}"
constraints:
  performance:
    response_time: "<500ms P95"
    throughput: "1000 requests/second"
```

### AI Agents
```yaml
meta:
  type: "agent"
  domain: "ai"
contracts:
  capabilities:
    - "Process user queries with contextual understanding"
    - "Generate responses with confidence scoring"
constraints:
  performance:
    response_time: "<3s for text generation"
  security_privacy:
    data_protection: "No PII in training data"
```

## Integration with Development Tools

### Cursor Integration
The schema prompts work seamlessly with Cursor for:
- Context-aware specification generation
- Code generation from specifications
- Specification validation and improvement

### Other AI Tools
Compatible with Claude, Cursor, and "possibly" other AI development assistants for:
- Specification creation and review
- Architecture design guidance
- Implementation planning

*Tested with: Cursor, Claude* (copilot testing to follow. Please let us know your experience with copilot and specplane.)

## Quality Guidelines

Good SpecPlane specifications should have:
- Clear, one-sentence purpose statement
- Measurable acceptance criteria
- Comprehensive error handling scenarios
- Realistic performance constraints
- Appropriate security considerations
- Observable metrics and events
- Language-agnostic behavioral contracts

## Contributing to Schema Evolution

The schema evolves based on:
- Real-world usage patterns
- Experimental validation results
- Community feedback
- Industry best practices

To suggest schema improvements:
1. Create specifications using current schema
2. Document gaps or usability issues
3. Propose specific enhancements
4. Test with actual development workflows

## Version History

- **v5.5.1** - Production-ready balanced schema with smart constraints
- **v7** - Extended schema with advanced enterprise features
- **v5** - Original foundational schema with C4 integration
- **Earlier versions** - Experimental iterations and validation studies

---

**Getting Started**: Begin with `README_START_HERE.md` to set up your development environment, then use `specplane_schema_prompt_v5.5.1_balanced.md` to create your first specification.


> **🚧 Work in Progress** - This project is actively evolving and we're working to make the core prompts better. We welcome feedback, contributions, and suggestions for improvement! Please share your experiences using SpecPlane in your development workflows.