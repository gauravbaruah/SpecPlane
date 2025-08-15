# SpecPlane Quality Gates Checklist
## Systematic validation for all experiments

## 🎯 Purpose
This checklist ensures consistent quality standards across all experiments and components. Each quality gate must pass before considering a component "complete."

---

## 📋 Pre-Implementation Checklist

### Setup Validation
- [ ] **System Contracts Header included** in experiment prompt
- [ ] **Test Command**: `make test-component-file_storage`

### Pattern_Library Component
- [ ] **Pattern matching accurate** - Correctly identifies domain patterns from descriptions
- [ ] **Reasoning chain selection** - Returns appropriate chains for matched patterns
- [ ] **Context extraction** - Properly extracts component type, domain, complexity
- [ ] **Performance acceptable** - Pattern matching completes in <100ms
- [ ] **Configuration loading** - Loads patterns and reasoning chains from YAML

**UAT Tests**:
```yaml
acceptance:
  - "Input 'file storage component' matches 'storage_systems' pattern with confidence >0.8"
  - "Input 'login screen widget' matches 'user_interfaces' pattern with confidence >0.8"
  - "Input 'chatbot agent' matches 'ai_agents' pattern with confidence >0.8"
  - "Unknown component type 'quantum processor' falls back to generic questions"
  - "Pattern matching completes in <100ms for typical component descriptions"

human_validation:
  - "Review 10 random pattern matches: Are they contextually appropriate? (Rate 1-5)"
  - "Rate question relevance 1-5: Do generated questions fit the component type?"

automated_metrics:
  - "pattern_match_confidence_p95 > 0.7"
  - "pattern_matching_latency_p95 < 100ms"
  - "fallback_rate < 10%"
```

**Test Command**: `make test-component-pattern_library`

### Question_Generator Component
- [ ] **Question generation working** - Produces 8-15 relevant questions per component
- [ ] **Follow-up logic functional** - Generates contextual follow-up questions
- [ ] **Question sequencing** - Proper dependency ordering and prioritization
- [ ] **Template expansion** - Correctly substitutes variables in question templates
- [ ] **Performance acceptable** - Question generation completes in <1 second

**UAT Tests**:
```yaml
acceptance:
  - "Storage component generates backup/corruption questions automatically"
  - "UI component generates state management questions automatically"
  - "AI component generates safety/cost questions automatically"
  - "Question sequence follows dependency order (purpose → failure modes → data)"
  - "Context-aware follow-ups: 'offline' mentioned → sync conflict questions added"

human_validation:
  - "Rate question clarity 1-5: Can developer understand without explanation?"
  - "Rate question relevance 1-5: Does this question improve component design?"
  - "Completeness check: Do generated questions cover critical design aspects?"

automated_metrics:
  - "questions_generated_per_session_avg between 10-25"
  - "question_generation_time_p95 < 1s"
  - "context_adaptation_trigger_rate > 30%"
```

**Test Command**: `make test-component-question_generator`

### Session_Orchestrator Component
- [ ] **State transitions valid** - All state machine transitions properly validated
- [ ] **Component coordination** - Successfully orchestrates all other components
- [ ] **Error recovery** - Graceful handling of component failures
- [ ] **Session persistence** - State properly saved and restored
- [ ] **Event handling** - Component events properly processed

**UAT Tests**:
```yaml
acceptance:
  - "Session state transitions: init → questioning → generating → complete"
  - "Pause/resume cycle preserves all answers and progress"
  - "Session timeout (30min) auto-saves and provides resume instructions"
  - "Invalid state transition logged with clear error message"
  - "Component failure triggers graceful degradation + user notification"

human_validation:
  - "Rate session flow smoothness 1-5: Does progression feel natural?"
  - "Error recovery assessment: Are error messages helpful and actionable?"

automated_metrics:
  - "session_completion_rate > 80%"
  - "state_transition_latency_p95 < 100ms"
  - "session_recovery_success_rate > 99%"
```

**Test Command**: `make test-component-session_orchestrator`

### CLI_Application Component
- [ ] **Command routing works** - All CLI commands properly parsed and routed
- [ ] **Error handling user-friendly** - Clear error messages and help text
- [ ] **Integration complete** - Successfully coordinates all system components
- [ ] **Session management** - Create, pause, resume functionality working
- [ ] **Rich output functional** - Progress bars, formatting, colors work

**UAT Tests**:
```yaml
acceptance:
  - "Command 'specplane guide ComponentName --type widget' starts interview"
  - "Command 'specplane validate spec.yaml' returns clear pass/fail results"
  - "Command 'specplane resume session123' restores previous state"
  - "Invalid command shows help text with examples"
  - "Ctrl+C during session saves state and shows resume instructions"

human_validation:
  - "Rate CLI UX 1-5: Is the interface intuitive for new users?"
  - "Error message quality: Are CLI errors helpful and actionable?"

automated_metrics:
  - "cli_response_latency_p95 < 500ms"
  - "command_success_rate > 95%"
  - "help_text_access_rate" # How often users need help
```

**Test Command**: `make test-component-cli_application`

---

## 🔗 Integration Quality Gates

### Component Integration
- [ ] **Dependency injection works** - Components properly receive dependencies
- [ ] **Data flow functional** - Information flows correctly between components
- [ ] **Event communication** - Components communicate via events as designed
- [ ] **Error propagation** - Errors properly handled across component boundaries
- [ ] **Performance acceptable** - End-to-end operations complete within SLA

**Test Command**: `make test-integration`

### End-to-End Validation
- [ ] **Complete session flow** - Full design session works start to finish
- [ ] **Artifact quality** - Generated specs and prompts meet quality standards
- [ ] **Session interruption** - Pause/resume works across component boundaries
- [ ] **Error scenarios** - System degrades gracefully under failure conditions
- [ ] **User experience** - Complete workflow feels professional and polished

**Test Command**: `make test`

---

## 📊 Experiment Measurement Gates

### Velocity Metrics
- [ ] **Time-to-green recorded** - Time until tests pass measured and logged
- [ ] **Rework cycles tracked** - Number of correction iterations documented
- [ ] **Implementation speed** - Component completion time within expected range
- [ ] **Integration time** - Time to integrate with existing components measured

### Quality Metrics  
- [ ] **Spec drift measured** - Number of violations of system contracts
- [ ] **Test coverage adequate** - >80% code coverage for component
- [ ] **Type safety achieved** - Zero type checking errors
- [ ] **Performance benchmarks** - All performance requirements met

### Developer Experience Metrics
- [ ] **Editor friction minimal** - Manual edits required documented
- [ ] **Prompt effectiveness** - Cursor generated working code efficiently  
- [ ] **Documentation gaps** - Missing or unclear requirements identified
- [ ] **Learning captured** - Insights and improvements documented

---

## 🚫 Failure Response Checklist

### When Quality Gate Fails

#### 1. Immediate Actions
- [ ] **Stop implementation** - Do not proceed until gate passes
- [ ] **Identify root cause** - Determine why gate failed
- [ ] **Document issue** - Record failure in experiment tracking
- [ ] **Assess impact** - Determine if this affects other components

#### 2. Resolution Process
- [ ] **Fix implementation** - Address the specific failure
- [ ] **Re-run gate** - Verify fix resolves the issue
- [ ] **Update tracking** - Increment rework cycle count
- [ ] **Review dependencies** - Check if fix affects other components

#### 3. Learning Integration
- [ ] **Update experiment notes** - Document what was learned
- [ ] **Improve future prompts** - Incorporate learnings into methodology
- [ ] **Share insights** - Add to knowledge base for team
- [ ] **Refine quality gates** - Improve gate if it missed something important

---

## 📝 Quality Gate Report Template

### Component Quality Report
```markdown
# Quality Gate Report: [Component Name]
**Experiment**: [Experiment Type]
**Date**: [Date]
**Implementer**: [Name]

## Automated Gates Status
- [ ] Type Checking: ✅ Pass / ❌ Fail
- [ ] Unit Tests: ✅ Pass / ❌ Fail  
- [ ] Code Formatting: ✅ Pass / ❌ Fail
- [ ] Import Organization: ✅ Pass / ❌ Fail
- [ ] CLI Smoke Test: ✅ Pass / ❌ Fail

## Component-Specific Gates
- [ ] [Component Gate 1]: ✅ Pass / ❌ Fail
- [ ] [Component Gate 2]: ✅ Pass / ❌ Fail
- [ ] [Component Gate 3]: ✅ Pass / ❌ Fail

## Metrics
- **Time to Green**: [X] minutes
- **Rework Cycles**: [N] iterations
- **Test Coverage**: [X]%
- **Type Safety**: [X] errors

## Issues Encountered
1. [Issue description and resolution]
2. [Issue description and resolution]

## Lessons Learned
- [Key insight 1]
- [Key insight 2]

## Recommendation
✅ Component ready for integration
❌ Component needs additional work

**Next Steps**: [What to do next]
```

---

## 🎯 Daily Development Checklist

### Before Starting Implementation
- [ ] Review system contracts header
- [ ] Understand component requirements
- [ ] Set up experiment tracking
- [ ] Prepare test environment

### During Implementation
- [ ] Follow TDD - write tests first when possible
- [ ] Run quality gates frequently
- [ ] Track metrics continuously
- [ ] Document issues immediately

### After Implementation
- [ ] Run full quality gate suite
- [ ] Complete quality gate report
- [ ] Update experiment tracking
- [ ] Prepare for integration testing

### End of Day
- [ ] Commit working code
- [ ] Update documentation
- [ ] Share learnings with team
- [ ] Plan next day's work

---

## 🔄 Continuous Improvement

### Weekly Quality Review
- [ ] **Analyze metrics trends** - Are we getting faster and better?
- [ ] **Review failed gates** - What patterns emerge?
- [ ] **Update methodology** - Incorporate lessons learned
- [ ] **Refine quality gates** - Add new gates or improve existing ones

### Experiment Retrospective
- [ ] **Compare experiment results** - Which approaches work best?
- [ ] **Document best practices** - Capture what works
- [ ] **Share with community** - Contribute to collective knowledge
- [ ] **Plan next experiments** - Design improved approaches

---

## 🔧 Jinja2 Template System Validation

### Template Rendering Quality Gates
- [ ] **Template syntax valid** - All Jinja2 templates parse without errors
- [ ] **Variable substitution works** - All template variables properly replaced
- [ ] **Conditional logic functional** - if/else blocks render correctly
- [ ] **Loop processing correct** - for loops iterate as expected
- [ ] **Template inheritance working** - extends/blocks function properly

### Jinja2 Usage Locations
```yaml
# Templates used by Artifact_Generator
templates:
  specs:
    - "config/templates/specs/component.yaml.j2"     # Generic component spec
    - "config/templates/specs/widget.yaml.j2"       # UI widget specific
    - "config/templates/specs/service.yaml.j2"      # API service specific
    - "config/templates/specs/agent.yaml.j2"        # AI agent specific
  
  prompts:
    - "config/templates/prompts/component_prompt.md.j2"    # Cursor prompt template
    - "config/templates/prompts/system_prompt.md.j2"       # System-level prompt
    - "config/templates/prompts/incremental_prompt.md.j2"  # Iterative development
  
  reports:
    - "config/templates/reports/coverage_report.md.j2"     # Coverage analysis
    - "config/templates/reports/risk_assessment.md.j2"     # Risk analysis
    - "config/templates/reports/session_summary.md.j2"     # Session results
```

### Template Quality Gates
```yaml
acceptance:
  - "All template files parse successfully with Jinja2"
  - "Sample data renders without errors for each template"
  - "Generated YAML passes syntax validation"
  - "Generated Markdown displays properly"
  - "Template variables all have fallback values"

automated_metrics:
  - "template_render_success_rate > 99%"
  - "template_render_time_p95 < 2s"
  - "generated_yaml_validity_rate = 100%"
```

---

## ⚙️ Configuration Management Quality Gates

### Configuration System Requirements
- [ ] **Environment detection** - Automatically detects dev/staging/prod environments
- [ ] **API key management** - Secure storage and rotation of API credentials
- [ ] **Observability sinks** - Configurable logging and metrics destinations
- [ ] **Feature flags** - Runtime configuration toggles
- [ ] **Rate limiting** - Configurable API rate limits and timeouts

### Configuration File Structure
```yaml
# ~/.specplane/config.yaml - User configuration
user_config:
  default_output_dir: "./output"
  preferred_session_mode: "interactive"
  editor_preference: "cursor"  # cursor, vscode, vim
  
# API integrations (optional)
integrations:
  openai:
    api_key: "${OPENAI_API_KEY}"
    model: "gpt-4"
    timeout: 30
    
  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"
    model: "claude-3-sonnet"
    timeout: 30

# Observability configuration
observability:
  logging:
    level: "INFO"
    file: "~/.specplane/logs/specplane.log"
    max_size: "10MB"
    backup_count: 5
    
  metrics:
    enabled: true
    sink_type: "file"  # file, prometheus, datadog
    sink_config:
      file_path: "~/.specplane/metrics/metrics.jsonl"
      
  telemetry:
    enabled: false  # Opt-in analytics
    endpoint: "https://telemetry.specplane.io/v1/events"

# System configuration  
system:
  max_session_duration: 1800  # 30 minutes
  auto_save_interval: 60      # 1 minute
  cleanup_after_days: 30
  max_concurrent_sessions: 3
  
# Feature flags
features:
  mermaid_visualizer: true
  code_analysis: false
  ai_question_generation: true
  validator_loop: false
```

### Configuration Quality Gates
```yaml
acceptance:
  - "Configuration loads successfully from default locations"
  - "Environment variables properly substituted in config values"
  - "Missing API keys fallback gracefully with clear warnings"
  - "Invalid configuration values trigger helpful error messages"
  - "Configuration changes take effect without restart"

human_validation:
  - "Rate configuration UX 1-5: Is setup process clear for new users?"
  - "Security review: Are API keys handled securely?"

automated_metrics:
  - "config_load_success_rate > 99%"
  - "config_validation_accuracy > 95%"
  - "sensitive_data_leak_count = 0"
```

### API Key Management Gates
- [ ] **Environment variable support** - Reads from ${VAR_NAME} syntax
- [ ] **Secure storage** - No plaintext API keys in logs or outputs
- [ ] **Key rotation support** - Can update keys without restart
- [ ] **Fallback graceful** - Works without API keys (local-only mode)
- [ ] **Validation functional** - Tests API key validity on startup

### Observability Integration Gates
- [ ] **Structured logging** - JSON logs with correlation IDs
- [ ] **Metrics collection** - Performance and usage metrics
- [ ] **Error tracking** - Exception capture and reporting
- [ ] **Health checks** - System health monitoring endpoints
- [ ] **Privacy compliant** - No PII in logs or metrics scaffold exists** for target component
- [ ] **Workspace prepared** with proper directory structure
- [ ] **Dependencies installed** (pytest, mypy, black, etc.)
- [ ] **Experiment tracking initialized** with ExperimentRun model

---

## 🔧 During Implementation Checklist

### Code Quality Standards
- [ ] **Type annotations complete** - All functions and methods have proper type hints
- [ ] **No TODO comments** - All placeholder code implemented or removed
- [ ] **Error handling implemented** - Graceful handling of expected failure modes
- [ ] **Logging added** where appropriate for debugging
- [ ] **Docstrings present** for public interfaces

### System Contracts Compliance
- [ ] **Uses canonical types** from system contracts header
- [ ] **No type drift** - No custom types that duplicate system types
- [ ] **Error hierarchy followed** - Uses SpecPlaneError base classes
- [ ] **Standard enums used** - ComponentType, SessionMode, etc.
- [ ] **Pydantic models validated** - All data models use proper validation

---

## ✅ Automated Quality Gates

### 1. Type Checking Gate
```bash
Command: mypy specplane/ --strict
Success Criteria: No type errors reported
```
**Must Pass**: Zero type checking errors

**Common Issues**:
- Missing type annotations
- Incompatible type assignments  
- Optional/None handling
- Generic type specifications

### 2. Unit Testing Gate
```bash
Command: pytest tests/unit/ -v
Success Criteria: All tests pass with coverage >80%
```
**Must Pass**: All component-specific tests green

**Test Categories**:
- Happy path functionality
- Error handling scenarios
- Edge cases and boundary conditions
- Integration with system contracts

### 3. Code Formatting Gate
```bash
Command: black --check specplane/ tests/
Success Criteria: No formatting issues
```
**Must Pass**: Consistent code formatting

**Auto-fix**: Run `black specplane/ tests/` to fix issues

### 4. Import Organization Gate
```bash
Command: isort --check-only specplane/ tests/
Success Criteria: Imports properly sorted
```
**Must Pass**: Standard import organization

**Auto-fix**: Run `isort specplane/ tests/` to fix issues

### 5. CLI Smoke Test Gate
```bash
Command: python -m specplane --help
Success Criteria: Help command returns successfully (exit code 0)
```
**Must Pass**: Basic CLI functionality works

**Validates**:
- CLI entry point functional
- Basic command parsing
- No import errors

---

## 🔍 Component-Specific Quality Gates

### File_Storage Component
- [ ] **Config loading works** - Can load YAML configuration files
- [ ] **Session persistence works** - Save/load session state successfully  
- [ ] **Error handling robust** - Graceful handling of missing files, permissions
- [ ] **Backup functionality** - Automatic backup creation before overwrites
- [ ] **Directory creation** - Auto-creates required directories

**UAT Tests**:
```yaml
acceptance:
  - "Config files load from config/ directory on startup without errors"
  - "Session state persists after each answer and survives process restart"
  - "Missing file scenarios handled gracefully with clear error messages"
  - "Disk full scenario triggers cleanup and user warning"
  - "File operations complete in <500ms for typical session data"

human_validation:
  - "Rate file organization 1-5: Is directory structure logical and clear?"
  - "Assess error messages: Are they helpful and suggest recovery actions?"

automated_metrics:
  - "config_load_success_rate > 99%"
  - "session_save_latency_p95 < 500ms"
  - "backup_creation_success_rate > 95%"
```

**Test Command**: `make test-component-file_storage`