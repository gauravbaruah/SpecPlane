# SpecPlane Component-Kernel Prompts Collection

## Overview
This collection contains 8 focused prompts for building SpecPlane using the Component-Kernel approach. Each prompt is standalone and can be used independently to implement specific components.

---

# 1. File_Storage_Kernel.md

## Component: File_Storage
**Purpose**: Handle all file operations for configuration, session persistence, and artifact generation

### Context
You're building the foundational File_Storage component for SpecPlane - a CLI tool that guides developers through systematic software design. This component handles all file I/O operations.

### Component Specification
- **Input**: File paths, data objects, configuration requests
- **Output**: Loaded data, save confirmations, file system operations
- **Key Responsibility**: Reliable file operations with error handling and backup

### Implementation Requirements
```python
# Core classes to implement:
class FileStorage:
    def load_config(self, config_name: str) -> Dict[str, Any]
    def save_session(self, session_id: str, state: SessionState) -> bool
    def load_session(self, session_id: str) -> Optional[SessionState]
    def save_artifact(self, artifact: Artifact, output_path: str) -> bool
    def ensure_directories(self) -> bool
    def backup_file(self, file_path: str) -> str
```

### File Structure to Create
```
specplane/
├── storage/
│   ├── __init__.py
│   ├── file_ops.py         # Main FileStorage class
│   ├── models.py           # Pydantic models
│   └── exceptions.py       # Custom exceptions
├── config/
│   ├── patterns.yaml       # Domain patterns
│   ├── questions.yaml      # Question templates  
│   ├── assessment_rules.yaml
│   └── templates/          # Jinja2 templates
└── .specplane/
    ├── sessions/           # Session persistence
    └── backups/           # Backup files
```

### Configuration Files Schema
```yaml
# patterns.yaml structure
patterns:
  storage_systems:
    triggers: ["storage", "persistence", "file", "database"]
    reasoning_chains: [...]
    
# questions.yaml structure  
questions:
  core:
    - id: "purpose"
      text: "What is the primary purpose of this component?"
      type: "open_ended"
```

### Error Handling Requirements
- Graceful handling of missing files
- Disk space validation before writes
- Automatic backup before overwrites
- Clear error messages with recovery suggestions

### Testing Strategy
```python
def test_config_loading():
    # Test loading valid/invalid config files
    
def test_session_persistence():
    # Test save/load session cycles
    
def test_error_scenarios():
    # Test disk full, permissions, corrupted files
```

### Success Criteria
- All config files load successfully on startup
- Session state persists across CLI interruptions
- File operations complete in <500ms
- Zero data loss during normal operations

---

# 2. Pattern_Library_Kernel.md

## Component: Pattern_Library
**Purpose**: Intelligent pattern matching and domain expertise application

### Context
You're building the Pattern_Library component - the "intelligence" of SpecPlane that recognizes domain patterns and applies expert knowledge to generate relevant questions.

### Component Specification
- **Input**: Component descriptions, user context
- **Output**: Matched patterns, reasoning chains, contextual insights
- **Key Responsibility**: Transform domain expertise into actionable patterns

### Implementation Requirements
```python
class PatternLibrary:
    def __init__(self, file_storage: FileStorage):
        self.patterns = file_storage.load_config("patterns")
        self.reasoning_chains = file_storage.load_config("reasoning_chains")
        
    def match_patterns(self, description: str) -> List[Pattern]:
        # Fuzzy text matching + keyword detection
        
    def get_reasoning_chains(self, pattern: Pattern, context: Dict) -> List[ReasoningChain]:
        # Context-aware reasoning chain selection
        
    def extract_context(self, description: str) -> ComponentContext:
        # Analyze text to extract type, domain, complexity
```

### Pattern Matching Logic
- **Keyword Detection**: Simple string matching for triggers
- **Fuzzy Matching**: Handle variations and synonyms  
- **Context Analysis**: Extract component type, domain, complexity
- **Pattern Ranking**: Score patterns by relevance

### Domain Patterns to Support
1. **Storage Systems**: Files, databases, caching, persistence
2. **User Interfaces**: Widgets, screens, interactions, state
3. **API Services**: REST, GraphQL, authentication, rate limiting
4. **AI Agents**: LLMs, reasoning, safety, cost management
5. **Mobile Apps**: Platform-specific, offline, performance

### Reasoning Chain Examples
```yaml
storage_reliability_chain:
  steps:
    - "Storage operations can fail"
    - "Failures need specific handling strategies"
    - "Users need clear feedback about failures"
  generates_questions:
    - "What happens when {operation} fails?"
    - "How do you communicate failures to users?"
```

### Integration Points
- **Called by**: Question_Generator for pattern analysis
- **Depends on**: File_Storage for configuration loading
- **Events**: Emits `pattern_matched`, `context_extracted`

### Testing Strategy
```python
def test_pattern_matching():
    assert "storage" in match_patterns("file storage system")
    assert "ui" in match_patterns("login screen widget")
    
def test_reasoning_chains():
    chains = get_reasoning_chains(storage_pattern, context)
    assert len(chains) > 0
```

### Success Criteria
- Patterns match correctly for common component types
- Context extraction identifies domain and complexity
- Reasoning chains generate relevant question paths
- Pattern matching completes in <100ms

---

# 3. Question_Generator_Kernel.md

## Component: Question_Generator  
**Purpose**: Dynamically generate contextual questions using patterns and reasoning

### Context
You're building the Question_Generator - the orchestrating component that transforms static patterns into dynamic, contextual questions that guide users through systematic design thinking.

### Component Specification
- **Input**: Component context, session state, previous answers
- **Output**: Prioritized question sequences, follow-up questions
- **Key Responsibility**: Dynamic question creation and sequencing

### Implementation Requirements
```python
class QuestionGenerator:
    def __init__(self, pattern_library: PatternLibrary, file_storage: FileStorage):
        self.pattern_library = pattern_library
        self.base_questions = file_storage.load_config("questions")
        
    def generate_initial_questions(self, context: ComponentContext) -> List[Question]:
        # Generate opening question sequence
        
    def generate_followup(self, answer: Answer, session_state: SessionState) -> Optional[Question]:
        # Context-aware follow-up questions
        
    def prioritize_questions(self, questions: List[Question], context: ComponentContext) -> List[Question]:
        # Order questions by importance and dependencies
```

### Question Generation Logic
1. **Pattern-Based Generation**: Use matched patterns to create relevant questions
2. **Context Adaptation**: Modify questions based on component type/domain
3. **Dependency Ordering**: Sequence questions to build on previous answers
4. **Follow-up Detection**: Generate probing questions from interesting answers

### Question Types to Support
```python
class QuestionType(Enum):
    OPEN_ENDED = "open_ended"          # "Describe the purpose..."
    MULTIPLE_CHOICE = "multiple_choice" # "Choose the primary pattern..."
    YES_NO = "yes_no"                  # "Does this handle failures?"
    SCENARIO = "scenario"              # "What happens when..."
    RANKING = "ranking"                # "Prioritize these concerns..."
```

### Dynamic Question Templates
```yaml
# Template examples
failure_scenario_template:
  text: "What happens when {operation} fails in {context}?"
  triggers: ["storage", "network", "external_dependency"]
  
state_completeness_template:
  text: "What are all possible states for {component_name}?"
  triggers: ["ui", "widget", "state_machine"]
```

### Context-Aware Adaptations
```python
def adapt_question_for_context(self, template: str, context: ComponentContext) -> str:
    # Replace placeholders with context-specific values
    # Adjust complexity based on user experience level
    # Add domain-specific follow-ups
```

### Integration Points
- **Uses**: Pattern_Library for pattern matching and reasoning chains
- **Called by**: Interview_Engine for question sequences
- **Depends on**: File_Storage for question templates

### Testing Strategy
```python
def test_question_generation():
    questions = generator.generate_initial_questions(storage_context)
    assert any("failure" in q.text.lower() for q in questions)
    
def test_followup_logic():
    followup = generator.generate_followup(answer, session_state)
    assert followup is not None if answer.needs_clarification
```

### Success Criteria
- Generates 8-15 relevant questions per component type
- Follow-up questions appear contextually appropriate
- Question sequences feel natural and progressive
- Generation completes in <1 second

---

# 4. Interview_Engine_Kernel.md

## Component: Interview_Engine
**Purpose**: Conduct smooth, interactive CLI conversations with users

### Context
You're building the Interview_Engine - the user-facing component that manages the conversational flow, presents questions naturally, and handles user input gracefully.

### Component Specification
- **Input**: Question sequences, user responses, session configuration
- **Output**: Completed answer sets, session state updates
- **Key Responsibility**: Smooth conversational UX with robust error handling

### Implementation Requirements
```python
class InterviewEngine:
    def __init__(self, question_generator: QuestionGenerator, file_storage: FileStorage):
        self.question_generator = question_generator
        self.file_storage = file_storage
        
    def conduct_interview(self, config: SessionConfig) -> Dict[str, Answer]:
        # Main interview loop
        
    def present_question(self, question: Question) -> None:
        # Display question with proper formatting
        
    def collect_answer(self, question: Question) -> Answer:
        # Handle different input types and validation
        
    def handle_interruption(self, session_state: SessionState) -> None:
        # Graceful handling of Ctrl+C, timeouts
```

### Conversational Flow Design
1. **Welcome & Context Setting**: Brief intro, component overview
2. **Progressive Questioning**: Start broad, get specific
3. **Context-Aware Follow-ups**: Probe interesting answers
4. **Progress Indication**: Show completion percentage
5. **Graceful Conclusion**: Summarize and transition to generation

### CLI User Experience
```bash
# Example interaction flow
┌─ SpecPlane Design Assistant ─┐
│ Component: VoiceRecorderWidget │
│ Type: UI Widget               │
│ Progress: ████████░░ 80%      │
└────────────────────────────────┘

Q: What is the primary purpose of this component?
> Record voice memos for note-taking

✓ Great! Follow-up: What audio formats will you support?
> MP3 and WAV

✓ Noted. Since this handles audio files...
Q: What happens when storage is full?
```

### Input Handling & Validation
```python
def validate_answer(self, answer: str, question: Question) -> ValidationResult:
    # Type-specific validation
    # Length and content checks
    # Suggest improvements for unclear answers
    
def handle_special_inputs(self, input_text: str) -> SpecialCommand:
    # "skip", "back", "help", "save", "quit"
    # Provide contextual help
```

### Error Recovery Strategies
- **Invalid Input**: Re-prompt with helpful guidance
- **Incomplete Answers**: Suggest improvements, allow continuation
- **User Confusion**: Provide examples and context
- **Technical Issues**: Auto-save state, provide resume instructions

### Session Management
```python
class SessionState:
    session_id: str
    component_context: ComponentContext
    answers: Dict[str, Answer]
    current_question_index: int
    timestamp: datetime
    
def save_checkpoint(self, state: SessionState) -> None:
    # Auto-save after each answer
    
def resume_session(self, session_id: str) -> SessionState:
    # Restore previous state seamlessly
```

### Integration Points
- **Uses**: Question_Generator for question sequences and follow-ups
- **Manages**: Session state and persistence via File_Storage
- **Called by**: CLI commands (guide, resume)

### Testing Strategy
```python
def test_question_presentation():
    # Test formatting, progress display, special characters
    
def test_input_validation():
    # Test edge cases, special commands, error recovery
    
def test_session_persistence():
    # Test save/resume cycles, data integrity
```

### Success Criteria
- Natural conversational flow that doesn't feel robotic
- Robust error handling with helpful recovery suggestions
- Session interruption/resume works seamlessly
- Average session completion time <15 minutes

---

# 5. Coverage_Assessor_Kernel.md

## Component: Coverage_Assessor
**Purpose**: Evaluate design completeness and identify critical gaps

### Context
You're building the Coverage_Assessor - the quality assurance component that determines whether a design session produced comprehensive enough specifications for successful AI implementation.

### Component Specification
- **Input**: Answer sets, assessment rules, component context
- **Output**: Coverage scores, gap reports, risk assessments
- **Key Responsibility**: Validate design completeness and surface missing requirements

### Implementation Requirements
```python
class CoverageAssessor:
    def __init__(self, file_storage: FileStorage):
        self.assessment_rules = file_storage.load_config("assessment_rules")
        self.gap_patterns = file_storage.load_config("gap_patterns")
        
    def assess_coverage(self, answers: Dict[str, Answer], context: ComponentContext) -> CoverageReport:
        # Calculate overall coverage score
        
    def detect_gaps(self, answers: Dict[str, Answer]) -> List[Gap]:
        # Identify missing critical requirements
        
    def generate_recommendations(self, gaps: List[Gap]) -> List[Recommendation]:
        # Suggest specific improvements
```

### Coverage Assessment Logic
1. **Section Completeness**: Ensure all critical areas are addressed
2. **Answer Quality**: Evaluate depth and specificity of responses
3. **Gap Pattern Matching**: Detect common missing requirements
4. **Risk Scoring**: Identify high-risk incomplete areas

### Critical Sections to Validate
```yaml
critical_sections:
  purpose:
    weight: 0.2
    required: true
    validation: "Must clearly describe component function"
    
  failure_modes:
    weight: 0.25
    required: true
    validation: "Must identify at least 3 failure scenarios"
    
  data_handling:
    weight: 0.2
    required_for: ["storage", "api", "ai"]
    validation: "Must specify data flow and persistence"
    
  user_interaction:
    weight: 0.15
    required_for: ["ui", "widget"]
    validation: "Must define all user interaction states"
```

### Gap Detection Patterns
```yaml
common_gaps:
  missing_error_handling:
    pattern: "No mention of failure scenarios or error states"
    severity: "high"
    recommendation: "Define specific error handling strategies"
    
  unclear_data_flow:
    pattern: "Vague descriptions of data movement or storage"
    severity: "medium"
    recommendation: "Specify exact data flow and persistence approach"
    
  missing_edge_cases:
    pattern: "Only happy path scenarios described"
    severity: "medium"
    recommendation: "Consider boundary conditions and edge cases"
```

### Scoring Algorithm
```python
def calculate_score(self, answers: Dict[str, Answer], rules: AssessmentRules) -> float:
    section_scores = {}
    
    for section, rule in rules.sections.items():
        if section in answers:
            quality_score = self.assess_answer_quality(answers[section])
            completeness_score = self.assess_completeness(answers[section], rule)
            section_scores[section] = (quality_score + completeness_score) / 2 * rule.weight
    
    return sum(section_scores.values())
```

### Coverage Report Generation
```python
class CoverageReport:
    overall_score: float
    section_scores: Dict[str, float]
    detected_gaps: List[Gap]
    recommendations: List[Recommendation]
    risk_level: RiskLevel
    
    def to_markdown(self) -> str:
        # Generate human-readable report
```

### Quality Gates
```python
def passes_quality_gates(self, report: CoverageReport) -> bool:
    return (
        report.overall_score >= 0.7 and
        all(section in report.section_scores for section in CRITICAL_SECTIONS) and
        report.risk_level != RiskLevel.HIGH
    )
```

### Integration Points
- **Called by**: CLI validate command and generation pipeline
- **Uses**: File_Storage for assessment rules and gap patterns
- **Produces**: Coverage reports for Artifact_Generator

### Testing Strategy
```python
def test_coverage_calculation():
    # Test scoring algorithm with known answer sets
    
def test_gap_detection():
    # Test pattern matching for common gaps
    
def test_quality_gates():
    # Test pass/fail thresholds
```

### Success Criteria
- Coverage scores correlate with spec quality in practice
- Gap detection identifies actual missing requirements
- Quality gates prevent insufficient specs from proceeding
- Assessment completes in <5 seconds

---

# 6. Session_Orchestrator_Kernel.md

## Component: Session_Orchestrator
**Purpose**: Manage interview flow and coordinate component interactions

### Context
You're building the Session_Orchestrator - the conductor that coordinates all other components to deliver smooth, stateful design sessions from start to finish.

### Component Specification
- **Input**: Session configuration, component interactions, state changes
- **Output**: Orchestrated workflow, state management, component coordination
- **Key Responsibility**: Overall session flow and inter-component communication

### Implementation Requirements
```python
class SessionOrchestrator:
    def __init__(self, components: Dict[str, Component]):
        self.interview_engine = components["interview_engine"]
        self.question_generator = components["question_generator"] 
        self.coverage_assessor = components["coverage_assessor"]
        self.artifact_generator = components["artifact_generator"]
        
    def start_session(self, config: SessionConfig) -> SessionResult:
        # Orchestrate complete design session
        
    def manage_state_transitions(self, event: SessionEvent) -> StateTransition:
        # Handle state changes and component coordination
        
    def handle_session_pause(self, session_id: str) -> PauseResult:
        # Graceful session interruption
        
    def resume_session(self, session_id: str) -> SessionState:
        # Seamless session restoration
```

### Session State Machine
```python
class SessionState(Enum):
    INITIALIZING = "initializing"
    QUESTIONING = "questioning"
    ASSESSING = "assessing"
    GENERATING = "generating"
    COMPLETED = "completed"
    PAUSED = "paused"
    ERROR = "error"

# State transitions
VALID_TRANSITIONS = {
    SessionState.INITIALIZING: [SessionState.QUESTIONING, SessionState.ERROR],
    SessionState.QUESTIONING: [SessionState.ASSESSING, SessionState.PAUSED, SessionState.ERROR],
    SessionState.ASSESSING: [SessionState.QUESTIONING, SessionState.GENERATING, SessionState.ERROR],
    SessionState.GENERATING: [SessionState.COMPLETED, SessionState.ERROR],
    SessionState.PAUSED: [SessionState.QUESTIONING, SessionState.ERROR],
}
```

### Orchestration Flow
1. **Session Initialization**
   - Validate configuration
   - Initialize component dependencies
   - Create session state and persistence
   
2. **Interview Coordination**
   - Generate initial questions via Question_Generator
   - Coordinate Interview_Engine conversation
   - Handle dynamic follow-up generation
   
3. **Coverage Assessment**
   - Trigger Coverage_Assessor evaluation
   - Handle insufficient coverage scenarios
   - Coordinate additional questioning if needed
   
4. **Artifact Generation**
   - Coordinate Artifact_Generator when coverage sufficient
   - Handle generation errors and retries
   - Finalize session completion

### Component Coordination
```python
def orchestrate_questioning_phase(self, session_state: SessionState) -> QuestioningResult:
    # 1. Generate questions
    questions = self.question_generator.generate_initial_questions(session_state.context)
    
    # 2. Conduct interview
    answers = self.interview_engine.conduct_interview(questions, session_state)
    
    # 3. Generate follow-ups dynamically
    for answer in answers:
        followup = self.question_generator.generate_followup(answer, session_state)
        if followup:
            additional_answer = self.interview_engine.ask_question(followup)
            answers.append(additional_answer)
    
    return QuestioningResult(answers, session_state)
```

### Error Handling & Recovery
```python
def handle_component_failure(self, component: str, error: Exception, session_state: SessionState) -> RecoveryAction:
    # Component-specific recovery strategies
    recovery_strategies = {
        "question_generator": self.fallback_to_static_questions,
        "interview_engine": self.save_state_and_restart,
        "coverage_assessor": self.skip_assessment_with_warning,
        "artifact_generator": self.retry_with_simpler_template
    }
    
    return recovery_strategies.get(component, self.graceful_session_termination)(error, session_state)
```

### Session Persistence & Resume
```python
def create_checkpoint(self, session_state: SessionState) -> None:
    # Save complete session state after each major phase
    
def resume_from_checkpoint(self, session_id: str) -> SessionState:
    # Restore session and determine appropriate resume point
    
def cleanup_expired_sessions(self) -> None:
    # Remove old session files (>30 days)
```

### Integration Points
- **Coordinates**: All other components in the system
- **Manages**: Session state persistence via File_Storage
- **Responds to**: CLI commands and user interruptions

### Event System
```python
class SessionEvent:
    type: EventType
    component: str
    data: Dict[str, Any]
    timestamp: datetime

# Events to handle
EVENT_TYPES = [
    "session_started", "question_answered", "assessment_completed",
    "generation_requested", "session_paused", "session_resumed",
    "component_error", "session_completed"
]
```

### Testing Strategy
```python
def test_state_transitions():
    # Test all valid state transitions and invalid attempts
    
def test_component_coordination():
    # Test inter-component communication and data flow
    
def test_error_recovery():
    # Test recovery from various component failure scenarios
    
def test_session_persistence():
    # Test pause/resume functionality
```

### Success Criteria
- Sessions complete successfully >80% of the time
- State transitions are always valid and logged
- Component failures trigger appropriate recovery actions
- Session pause/resume works seamlessly

---

# 7. Artifact_Generator_Kernel.md

## Component: Artifact_Generator
**Purpose**: Generate comprehensive specifications and natural language prompts

### Context
You're building the Artifact_Generator - the final component that transforms interview answers into polished, AI-ready specifications and cursor prompts.

### Component Specification
- **Input**: Answer sets, coverage reports, generation templates
- **Output**: YAML specifications, markdown prompts, coverage reports
- **Key Responsibility**: High-quality artifact generation optimized for AI development

### Implementation Requirements
```python
class ArtifactGenerator:
    def __init__(self, file_storage: FileStorage):
        self.templates = self.load_templates(file_storage)
        self.jinja_env = self.setup_jinja_environment()
        
    def generate_specification(self, answers: Dict[str, Answer], context: ComponentContext) -> YAMLSpec:
        # Generate comprehensive YAML specification
        
    def generate_cursor_prompt(self, spec: YAMLSpec, context: ComponentContext) -> MarkdownPrompt:
        # Generate natural language prompt for AI development
        
    def generate_coverage_report(self, coverage: CoverageReport) -> MarkdownReport:
        # Generate human-readable coverage analysis
```

### Template System Architecture
```
config/templates/
├── specs/
│   ├── component.yaml.j2      # Component specification template
│   ├── widget.yaml.j2         # UI widget specific template
│   ├── service.yaml.j2        # Service/API specific template
│   └── agent.yaml.j2          # AI agent specific template
├── prompts/
│   ├── component_prompt.md.j2 # Natural language prompt template
│   ├── system_prompt.md.j2    # System-level prompt template
│   └── incremental_prompt.md.j2 # Iterative development prompt
└── reports/
    ├── coverage_report.md.j2  # Coverage analysis template
    └── risk_assessment.md.j2  # Risk analysis template
```

### YAML Specification Generation
```python
def generate_specification(self, answers: Dict[str, Answer], context: ComponentContext) -> YAMLSpec:
    # Select appropriate template based on component type
    template_name = self.select_template(context.type)
    template = self.templates[template_name]
    
    # Transform answers into structured data
    structured_data = self.transform_answers(answers, context)
    
    # Apply template with context
    spec_content = template.render(
        component=structured_data,
        context=context,
        timestamp=datetime.now(),
        metadata=self.generate_metadata(context)
    )
    
    return YAMLSpec(content=spec_content, context=context)
```

### Natural Language Prompt Generation
```python
def generate_cursor_prompt(self, spec: YAMLSpec, context: ComponentContext) -> MarkdownPrompt:
    # Extract key implementation guidance from spec
    implementation_hints = self.extract_implementation_hints(spec)
    
    # Generate contextual development guidance
    development_context = self.build_development_context(spec, context)
    
    # Apply prompt template
    prompt_template = self.templates["component_prompt.md.j2"]
    prompt_content = prompt_template.render(
        specification=spec,
        context=context,
        implementation_hints=implementation_hints,
        development_context=development_context
    )
    
    return MarkdownPrompt(content=prompt_content, context=context)
```

### Template Variables & Helpers
```python
# Jinja2 environment setup with custom filters
def setup_jinja_environment(self) -> jinja2.Environment:
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("config/templates"))
    
    # Custom filters for better template rendering
    env.filters['to_snake_case'] = self.to_snake_case
    env.filters['to_pascal_case'] = self.to_pascal_case
    env.filters['format_list'] = self.format_list
    env.filters['extract_keywords'] = self.extract_keywords
    
    return env

# Template helper functions
def extract_implementation_hints(self, spec: YAMLSpec) -> Dict[str, List[str]]:
    # Extract technical guidance from specification
    
def format_error_scenarios(self, failures: List[str]) -> str:
    # Format failure modes for prompt inclusion
```

### Artifact Types & Templates
```yaml
# component.yaml.j2 - Main specification template
meta:
  id: "{{ component.id }}"
  name: "{{ component.name }}"
  purpose: "{{ component.purpose }}"
  type: "{{ context.type }}"

contracts:
  interfaces:
    {% for interface in component.interfaces %}
    - name: "{{ interface.name }}"
      input: "{{ interface.input }}"
      output: "{{ interface.output }}"
    {% endfor %}

behavior:
  success_scenarios:
    {% for scenario in component.success_scenarios %}
    - "{{ scenario }}"
    {% endfor %}
  
  failure_modes:
    {% for failure in component.failure_modes %}
    - trigger: "{{ failure.trigger }}"
      response: "{{ failure.response }}"
    {% endfor %}
```

### Quality Assurance
```python
def validate_generated_artifacts(self, artifacts: List[Artifact]) -> ValidationResult:
    # YAML syntax validation
    # Template completeness check
    # Cross-reference consistency
    # AI prompt quality assessment
    
def enhance_prompt_quality(self, prompt: MarkdownPrompt) -> MarkdownPrompt:
    # Add implementation examples
    # Include common pitfalls
    # Provide testing guidance
    # Suggest related components
```

### Output File Organization
```
output/
├── specs/
│   ├── VoiceRecorderWidget.yaml
│   └── UserAuthService.yaml
├── prompts/
│   ├── VoiceRecorderWidget_cursor_prompt.md
│   └── UserAuthService_cursor_prompt.md
└── reports/
    ├── VoiceRecorderWidget_coverage_report.md
    └── session_summary.md
```

### Integration Points
- **Called by**: Session_Orchestrator after successful coverage assessment
- **Uses**: File_Storage for template loading and artifact saving
- **Produces**: Final deliverables for the design session

### Testing Strategy
```python
def test_template_rendering():
    # Test all templates with sample data
    
def test_yaml_validity():
    # Ensure generated YAML is valid and parseable
    
def test_prompt_quality():
    # Human evaluation of generated prompts
```

### Success Criteria
- Generated YAML specifications are valid and comprehensive
- Cursor prompts enable successful AI implementation
- Artifacts are well-formatted and professionally presented
- Generation completes in <30 seconds

---

# 8. CLI_Application_Kernel.md

## Component: CLI_Application (Main Entry Point)
**Purpose**: Provide the command-line interface and coordinate all system components

### Context
You're building the main CLI application entry point for SpecPlane - the user-facing interface that coordinates all components to deliver the complete design thinking experience.

### Component Specification
- **Input**: Command-line arguments, user interactions
- **Output**: Complete design sessions, file artifacts, user feedback
- **Key Responsibility**: CLI interface and overall system coordination

### Implementation Requirements
```python
# main.py - Entry point using Typer
import typer
from specplane.core import SessionOrchestrator, ComponentFactory

app = typer.Typer(name="specplane", help="Interactive Design Thinking Agent")

@app.command()
def guide(
    component_name: str,
    component_type: ComponentType = typer.Option("component", help="Type of component"),
    mode: SessionMode = typer.Option("interactive", help="Session mode"),
    output_dir: str = typer.Option("./output", help="Output directory")
):
    """Start a guided design session for a component."""
    
@app.command() 
def validate(
    spec_file: str = typer.Argument(..., help="YAML spec file to validate")
):
    """Validate an existing component specification."""
    
@app.command()
def resume(
    session_id: str = typer.Argument(..., help="Session ID to resume")
):
    """Resume a paused design session."""
```

### CLI Command Structure
```bash
# Main commands
specplane guide "VoiceRecorderWidget" --type widget --mode quick
specplane guide "UserAuthService" --type service --mode comprehensive  
specplane validate ./specs/VoiceRecorderWidget.yaml
specplane resume session_20241215_143022

# Additional utility commands
specplane list-sessions                    # Show available sessions
specplane clean --older-than 30d         # Clean old session files
specplane config --show                  # Display current configuration
specplane templates --list               # Show available templates
```

### Component Factory & Dependency Injection
```python
class ComponentFactory:
    def __init__(self, config_dir: str = "./config"):
        self.config_dir = config_dir
        
    def create_file_storage(self) -> FileStorage:
        return FileStorage(config_dir=self.config_dir)
        
    def create_pattern_library(self, file_storage: FileStorage) -> PatternLibrary:
        return PatternLibrary(file_storage)
        
    def create_question_generator(self, pattern_library: PatternLibrary, file_storage: FileStorage) -> QuestionGenerator:
        return QuestionGenerator(pattern_library, file_storage)
        
    def create_interview_engine(self, question_generator: QuestionGenerator, file_storage: FileStorage) -> InterviewEngine:
        return InterviewEngine(question_generator, file_storage)
        
    def create_coverage_assessor(self, file_storage: FileStorage) -> CoverageAssessor:
        return CoverageAssessor(file_storage)
        
    def create_artifact_generator(self, file_storage: FileStorage) -> ArtifactGenerator:
        return ArtifactGenerator(file_storage)
        
    def create_session_orchestrator(self) -> SessionOrchestrator:
        # Wire up all dependencies
        file_storage = self.create_file_storage()
        pattern_library = self.create_pattern_library(file_storage)
        question_generator = self.create_question_generator(pattern_library, file_storage)
        interview_engine = self.create_interview_engine(question_generator, file_storage)
        coverage_assessor = self.create_coverage_assessor(file_storage)
        artifact_generator = self.create_artifact_generator(file_storage)
        
        return SessionOrchestrator({
            "interview_engine": interview_engine,
            "question_generator": question_generator,
            "coverage_assessor": coverage_assessor,
            "artifact_generator": artifact_generator
        })
```

### CLI Command Implementations
```python
def guide_command(component_name: str, component_type: ComponentType, mode: SessionMode, output_dir: str):
    """Main design session command implementation."""
    try:
        # Initialize system
        factory = ComponentFactory()
        orchestrator = factory.create_session_orchestrator()
        
        # Configure session
        config = SessionConfig(
            component_name=component_name,
            component_type=component_type,
            mode=mode,
            output_directory=output_dir
        )
        
        # Run design session
        typer.echo(f"🎯 Starting design session for {component_name}")
        typer.echo(f"   Type: {component_type.value}")
        typer.echo(f"   Mode: {mode.value}")
        typer.echo()
        
        result = orchestrator.start_session(config)
        
        # Display results
        if result.success:
            typer.echo("✅ Design session completed successfully!")
            typer.echo(f"📁 Generated files:")
            for artifact in result.artifacts:
                typer.echo(f"   - {artifact.file_path}")
            typer.echo(f"📊 Coverage Score: {result.coverage_score:.1%}")
        else:
            typer.echo("❌ Session completed with issues")
            for issue in result.issues:
                typer.echo(f"   ⚠️  {issue}")
                
    except KeyboardInterrupt:
        typer.echo("\n⏸️  Session paused. Use 'specplane resume <session_id>' to continue.")
    except Exception as e:
        typer.echo(f"❌ Error: {e}")
        raise typer.Exit(1)

def validate_command(spec_file: str):
    """Validate existing specification file."""
    try:
        factory = ComponentFactory()
        file_storage = factory.create_file_storage()
        coverage_assessor = factory.create_coverage_assessor(file_storage)
        
        # Load and parse spec file
        with open(spec_file, 'r') as f:
            spec_content = yaml.safe_load(f)
            
        # Convert to internal format and assess
        answers = convert_spec_to_answers(spec_content)
        context = extract_context_from_spec(spec_content)
        
        # Run coverage assessment
        report = coverage_assessor.assess_coverage(answers, context)
        
        # Display results
        typer.echo(f"📋 Validation Results for {spec_file}")
        typer.echo(f"📊 Coverage Score: {report.overall_score:.1%}")
        
        if report.overall_score >= 0.7:
            typer.echo("✅ Specification meets quality standards")
        else:
            typer.echo("⚠️  Specification needs improvement")
            
        if report.detected_gaps:
            typer.echo("\n🔍 Detected Gaps:")
            for gap in report.detected_gaps:
                typer.echo(f"   - {gap.description}")
                
    except FileNotFoundError:
        typer.echo(f"❌ File not found: {spec_file}")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Validation error: {e}")
        raise typer.Exit(1)

def resume_command(session_id: str):
    """Resume paused session."""
    try:
        factory = ComponentFactory()
        orchestrator = factory.create_session_orchestrator()
        
        # Resume session
        typer.echo(f"🔄 Resuming session {session_id}")
        result = orchestrator.resume_session(session_id)
        
        # Continue with normal flow
        # (Same completion logic as guide_command)
        
    except FileNotFoundError:
        typer.echo(f"❌ Session not found: {session_id}")
        typer.echo("   Use 'specplane list-sessions' to see available sessions")
        raise typer.Exit(1)
```

### Rich CLI Output & Progress
```python
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table

console = Console()

def display_welcome(config: SessionConfig):
    """Display welcome panel with session info."""
    panel = Panel(
        f"Component: {config.component_name}\n"
        f"Type: {config.component_type.value}\n"
        f"Mode: {config.mode.value}",
        title="🎯 SpecPlane Design Assistant",
        border_style="blue"
    )
    console.print(panel)

def display_progress(current: int, total: int, current_task: str):
    """Show progress during session."""
    progress_bar = "█" * (current * 20 // total) + "░" * (20 - current * 20 // total)
    console.print(f"Progress: [{progress_bar}] {current}/{total} - {current_task}")

def display_completion_summary(result: SessionResult):
    """Show final results summary."""
    table = Table(title="📊 Session Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Coverage Score", f"{result.coverage_score:.1%}")
    table.add_row("Questions Answered", str(len(result.answers)))
    table.add_row("Files Generated", str(len(result.artifacts)))
    table.add_row("Session Duration", format_duration(result.duration))
    
    console.print(table)
```

### Configuration Management
```python
class CLIConfig:
    def __init__(self):
        self.config_file = Path.home() / ".specplane" / "config.yaml"
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load CLI configuration with defaults."""
        defaults = {
            "output_directory": "./output",
            "session_timeout": 1800,  # 30 minutes
            "auto_save_interval": 60,  # 1 minute
            "cleanup_after_days": 30
        }
        
        if self.config_file.exists():
            with open(self.config_file) as f:
                user_config = yaml.safe_load(f)
                defaults.update(user_config)
        
        return defaults
    
    def save_config(self):
        """Save current configuration."""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f)
```

### Error Handling & Logging
```python
import logging
from pathlib import Path

def setup_logging():
    """Configure logging for CLI application."""
    log_dir = Path.home() / ".specplane" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "specplane.log"),
            logging.StreamHandler()
        ]
    )

def handle_unexpected_error(e: Exception, context: str):
    """Handle unexpected errors gracefully."""
    logging.error(f"Unexpected error in {context}: {e}", exc_info=True)
    
    typer.echo("❌ An unexpected error occurred")
    typer.echo("📝 Error details have been logged")
    typer.echo("🔧 If this persists, please file an issue at github.com/yourrepo/specplane")
```

### Application Entry Point
```python
# pyproject.toml entry point configuration
[project.scripts]
specplane = "specplane.cli.main:app"

# main.py
def main():
    """Main application entry point."""
    setup_logging()
    app()

if __name__ == "__main__":
    main()
```

### Integration Points
- **Coordinates**: All system components via Session_Orchestrator
- **Manages**: CLI user experience and command routing
- **Handles**: Error recovery, logging, and user feedback

### Testing Strategy
```python
def test_cli_commands():
    # Test all CLI commands with various inputs
    
def test_error_handling():
    # Test graceful error handling and user feedback
    
def test_session_flow():
    # End-to-end testing of complete design sessions
```

### Success Criteria
- CLI commands execute successfully with clear feedback
- Error messages are helpful and actionable
- Session state persistence works reliably
- User experience feels polished and professional

---

## Usage Instructions for Component-Kernel Prompts

### How to Use These Prompts

1. **Choose a Component**: Start with any component (recommended: File_Storage or Pattern_Library)

2. **Copy the Entire Kernel**: Copy the complete prompt for that component to Cursor

3. **Set Context**: Ensure Cursor has the file structure and dependencies mentioned

4. **Implement Incrementally**: Build the component step-by-step, testing as you go

5. **Integration**: Use the integration points to connect components together

### Recommended Build Order
1. **File_Storage** (foundation - no dependencies)
2. **Pattern_Library** (depends on File_Storage)
3. **Question_Generator** (depends on Pattern_Library)
4. **Coverage_Assessor** (depends on File_Storage)
5. **Interview_Engine** (depends on Question_Generator)
6. **Artifact_Generator** (depends on File_Storage)
7. **Session_Orchestrator** (coordinates all components)
8. **CLI_Application** (entry point - coordinates everything)

### Testing Each Component
Each kernel includes specific testing strategies. Implement and test each component independently before integration.

### Integration Strategy
Use the integration points defined in each kernel to wire components together through the Session_Orchestrator and CLI_Application.