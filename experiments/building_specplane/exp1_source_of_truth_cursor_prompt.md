# SpecPlane - Interactive Design Thinking Agent
## Source of Truth Implementation Prompt

You are building **SpecPlane**, an interactive CLI application that transforms vague component ideas into detailed, validated specifications optimized for AI-assisted development.

## 🎯 Core Mission
**Better upfront thinking → Better AI prompts → Better code**

SpecPlane encodes expert systems thinking into a repeatable process that guides developers through systematic software design, generating comprehensive specifications and natural language prompts for AI development tools.

## 🏗️ Architecture Overview

### System Boundary
- **Purpose**: Transform human intention into AI-implementable specifications
- **Flow**: User Input → Pattern Recognition → Dynamic Questioning → Coverage Assessment → Generated Artifacts
- **Value**: Compress expert design thinking into 15-minute guided sessions

### Container Architecture
```
CLI_Application (Python + Typer + Pydantic + Jinja2)
├── Session_Orchestrator     # Flow and state management
├── Question_Generator       # Dynamic question creation
├── Pattern_Library         # Domain expertise and reasoning chains  
├── Interview_Engine        # Interactive CLI sessions
├── Coverage_Assessor       # Design completeness validation
└── Artifact_Generator      # YAML specs + cursor prompts

File_Storage (Local Filesystem)
├── config/                 # Patterns, questions, templates
├── sessions/              # Interview state persistence  
└── output/                # Generated specs and prompts
```

## 🔄 Core Process Flow

1. **Pattern Recognition**: Analyze component description → Identify applicable domain patterns
2. **Dynamic Questioning**: Generate contextual questions using reasoning chains
3. **Interactive Session**: Conduct guided interview with follow-up questions
4. **Coverage Assessment**: Evaluate completeness, identify gaps, assign scores
5. **Artifact Generation**: Produce comprehensive specs + natural language prompts

## 🎯 Implementation Requirements

### CLI Interface
```bash
# Primary commands
specplane guide "VoiceRecorderWidget" --type widget --mode quick
specplane validate spec.yaml  
specplane resume session_id
```

### Key Components to Build

#### 1. Question_Generator
- **Purpose**: Dynamically create contextual questions using pattern matching
- **Logic**: Pattern detection → Reasoning chain selection → Question templating
- **Key Feature**: Adaptive intelligence that asks exactly the right questions

#### 2. Pattern_Library  
- **Purpose**: Encode domain expertise (storage, UI, API, AI, mobile patterns)
- **Logic**: Fuzzy matching + context analysis + reasoning chains
- **Key Feature**: Intelligent middleware that transforms static patterns into dynamic questions

#### 3. Coverage_Assessor
- **Purpose**: Evaluate design completeness and identify critical gaps
- **Logic**: Gap pattern matching + scoring rules + risk assessment
- **Key Feature**: Ensures specifications are comprehensive enough for successful AI implementation

#### 4. Interview_Engine
- **Purpose**: Conduct smooth, natural CLI conversations
- **Logic**: State management + context-aware follow-ups + graceful error handling
- **Key Feature**: Progressive disclosure that doesn't overwhelm users

## 📁 File Structure to Implement
```
specplane/
├── cli/
│   ├── __init__.py
│   ├── main.py              # Typer CLI entry point
│   └── commands/
│       ├── guide.py         # Main interview command
│       ├── validate.py      # Spec validation
│       └── resume.py        # Session resumption
├── core/
│   ├── orchestrator.py      # Session_Orchestrator
│   ├── generator.py         # Question_Generator  
│   ├── patterns.py          # Pattern_Library
│   ├── engine.py           # Interview_Engine
│   ├── assessor.py         # Coverage_Assessor
│   └── artifacts.py        # Artifact_Generator
├── storage/
│   ├── file_ops.py         # File_Storage operations
│   └── models.py           # Pydantic data models
├── config/
│   ├── patterns.yaml       # Domain patterns + reasoning chains
│   ├── questions.yaml      # Base question templates
│   ├── assessment_rules.yaml # Coverage scoring logic
│   └── templates/          # Jinja2 templates for generation
└── tests/
    ├── test_components.py
    └── test_integration.py
```

## 🚀 Progressive Implementation Strategy

### P0: Core Engine (Week 1)
- File operations (read configs, save sessions)
- Basic pattern matching (keyword detection)
- Simple question loading from YAML
- CLI interaction with basic state management
- Percentage-based coverage scoring
- Template-based artifact generation

### P1: Intelligence Layer (Week 2-3)  
- Dynamic question generation
- Context-aware follow-ups
- Gap pattern detection
- Improved coverage assessment
- Better error handling and recovery

### P2: Advanced Features (Week 4+)
- Learning system that improves over time
- Complex reasoning chain execution
- Advanced pattern matching (fuzzy + semantic)
- Plugin architecture for new domains

## 🎯 Success Criteria

### Functional Requirements
- Sessions complete in <15 minutes with >70% coverage
- Generated prompts enable AI to produce working, robust code  
- Critical design gaps surfaced before implementation begins
- State persistence allows pause/resume of sessions

### Quality Gates
- Command response latency <500ms
- Session completion rate >80%
- Spec generation time <30s
- Generated artifacts pass validation

## 🔧 Technical Implementation Notes

### Key Libraries
- **Typer**: CLI framework with rich features
- **Pydantic**: Data validation and serialization
- **Jinja2**: Template engine for artifact generation
- **PyYAML**: Configuration file handling
- **Rich**: Enhanced CLI output and progress bars

### Data Models (Pydantic)
```python
class ComponentContext(BaseModel):
    name: str
    type: ComponentType
    description: str
    domain: Optional[str]

class Question(BaseModel):
    id: str
    text: str
    type: QuestionType
    dependencies: List[str]
    reasoning_chain: Optional[str]

class SessionState(BaseModel):
    session_id: str
    component: ComponentContext
    answers: Dict[str, Any]
    current_question: Optional[str]
    coverage_score: float
```

### Error Handling Philosophy
- Graceful degradation when components fail
- Clear error messages with actionable recovery steps
- Auto-save session state on interruption
- Comprehensive logging for debugging

## 🎯 Immediate Next Steps

1. **Setup Project Structure**: Initialize Python package with proper structure
2. **Implement File_Storage**: Basic file operations and configuration loading
3. **Build Pattern_Library**: Simple pattern matching and question loading
4. **Create Interview_Engine**: Basic CLI interaction and state management
5. **Add Coverage_Assessor**: Simple scoring and gap detection
6. **Integrate Components**: End-to-end flow with basic artifact generation

## 🔥 The Meta Insight

**SpecPlane was designed using SpecPlane's own methodology** - trying to prove that systematic design thinking produces better software architecture. The specifications you're implementing were generated through the exact process SpecPlane automates.

This recursive self-improvement makes SpecPlane not just a tool, but a methodology that demonstrates its own value through its own creation.

---

**Start with the file structure and basic CLI setup. Build incrementally, test each component, and maintain the core value proposition: transforming vague ideas into implementable specifications.**