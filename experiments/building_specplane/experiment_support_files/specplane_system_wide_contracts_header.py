# SpecPlane System-Wide Contracts Header v0.3
# Include this header in ALL experiment prompts to prevent type drift

from __future__ import annotations
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator


# =============================================================================
# CORE ENUMS
# =============================================================================

class ComponentType(str, Enum):
    """Standard component types across SpecPlane system"""
    COMPONENT = "component"
    WIDGET = "widget" 
    SERVICE = "service"
    AGENT = "agent"
    CONTAINER = "container"
    MOBILE_COMPONENT = "mobile_component"


class SessionMode(str, Enum):
    """Interview session modes"""
    QUICK = "quick"           # 5-8 questions, basic coverage
    INTERACTIVE = "interactive"  # 10-15 questions, standard flow
    COMPREHENSIVE = "comprehensive"  # 15+ questions, deep analysis


class SessionState(str, Enum):
    """Session state machine values"""
    INITIALIZING = "initializing"
    QUESTIONING = "questioning" 
    ASSESSING = "assessing"
    GENERATING = "generating"
    COMPLETED = "completed"
    PAUSED = "paused"
    ERROR = "error"


class QuestionType(str, Enum):
    """Types of questions in interview"""
    OPEN_ENDED = "open_ended"
    MULTIPLE_CHOICE = "multiple_choice"
    YES_NO = "yes_no"
    SCENARIO = "scenario"
    RANKING = "ranking"


class RiskLevel(str, Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"


class ArtifactType(str, Enum):
    """Types of generated artifacts"""
    YAML_SPEC = "yaml_spec"
    CURSOR_PROMPT = "cursor_prompt"
    COVERAGE_REPORT = "coverage_report"
    MERMAID_DIAGRAM = "mermaid_diagram"


# =============================================================================
# CORE DATA MODELS
# =============================================================================

class ComponentContext(BaseModel):
    """Context information about component being designed"""
    name: str = Field(..., description="Component name")
    type: ComponentType = Field(..., description="Component type")
    description: str = Field(..., description="User-provided description")
    domain: Optional[str] = Field(None, description="Detected domain (storage, ui, api, etc)")
    complexity: Optional[str] = Field(None, description="Estimated complexity (simple, medium, complex)")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Component name cannot be empty")
        return v.strip()


class Question(BaseModel):
    """Individual question in interview"""
    id: str = Field(..., description="Unique question identifier")
    text: str = Field(..., description="Question text to display")
    type: QuestionType = Field(..., description="Question type")
    dependencies: List[str] = Field(default_factory=list, description="Required previous questions")
    reasoning_chain: Optional[str] = Field(None, description="Associated reasoning chain")
    pattern_source: Optional[str] = Field(None, description="Pattern that generated this question")


class Answer(BaseModel):
    """User answer to question"""
    question_id: str = Field(..., description="Question being answered")
    content: str = Field(..., description="Answer content")
    timestamp: datetime = Field(default_factory=datetime.now)
    quality_score: Optional[float] = Field(None, description="Answer quality 0-1")
    needs_clarification: bool = Field(False, description="Whether follow-up needed")


class Pattern(BaseModel):
    """Domain pattern definition"""
    id: str = Field(..., description="Pattern identifier")
    name: str = Field(..., description="Human readable name")
    triggers: List[str] = Field(..., description="Keywords that activate this pattern")
    domain: str = Field(..., description="Domain area (storage, ui, api, etc)")
    reasoning_chains: List[str] = Field(default_factory=list, description="Associated reasoning chains")
    weight: float = Field(1.0, description="Pattern matching weight")


class ReasoningChain(BaseModel):
    """Chain of reasoning steps"""
    id: str = Field(..., description="Chain identifier") 
    name: str = Field(..., description="Human readable name")
    steps: List[str] = Field(..., description="Reasoning steps in order")
    generates_questions: List[str] = Field(default_factory=list, description="Question templates")
    applies_to: List[ComponentType] = Field(default_factory=list, description="Applicable component types")


class Gap(BaseModel):
    """Detected gap in design coverage"""
    id: str = Field(..., description="Gap identifier")
    section: str = Field(..., description="Section with gap")
    description: str = Field(..., description="Gap description")
    severity: RiskLevel = Field(..., description="Gap severity")
    recommendation: str = Field(..., description="How to address gap")


class CoverageReport(BaseModel):
    """Coverage assessment results"""
    overall_score: float = Field(..., ge=0, le=1, description="Overall coverage score 0-1")
    section_scores: Dict[str, float] = Field(default_factory=dict, description="Per-section scores")
    detected_gaps: List[Gap] = Field(default_factory=list, description="Found gaps")
    risk_level: RiskLevel = Field(..., description="Overall risk assessment")
    recommendations: List[str] = Field(default_factory=list, description="Improvement suggestions")


class Artifact(BaseModel):
    """Generated artifact"""
    id: str = Field(..., description="Artifact identifier")
    type: ArtifactType = Field(..., description="Artifact type")
    content: str = Field(..., description="Artifact content")
    file_path: str = Field(..., description="Output file path")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SessionConfig(BaseModel):
    """Session configuration"""
    component_name: str = Field(..., description="Component being designed")
    component_type: ComponentType = Field(..., description="Component type")
    mode: SessionMode = Field(SessionMode.INTERACTIVE, description="Session mode")
    output_directory: str = Field("./output", description="Output directory")
    user_experience_level: str = Field("intermediate", description="User experience level")


class SessionResult(BaseModel):
    """Complete session results"""
    session_id: str = Field(..., description="Session identifier")
    success: bool = Field(..., description="Whether session completed successfully")
    coverage_score: float = Field(..., ge=0, le=1, description="Final coverage score")
    answers: Dict[str, Answer] = Field(default_factory=dict, description="All answers")
    artifacts: List[Artifact] = Field(default_factory=list, description="Generated artifacts")
    duration: float = Field(..., description="Session duration in seconds")
    issues: List[str] = Field(default_factory=list, description="Issues encountered")


# =============================================================================
# EXPERIMENT TRACKING MODELS
# =============================================================================

class ExperimentType(str, Enum):
    """Types of experiments being run"""
    SOURCE_OF_TRUTH = "source_of_truth"
    COMPONENT_KERNEL = "component_kernel"
    SPEC_ONLY = "spec_only" 
    SPEC_TO_PROMPT = "spec_to_prompt"
    VALIDATOR_LOOP = "validator_loop"


class ExperimentRun(BaseModel):
    """Single experiment execution"""
    id: str = Field(..., description="Unique run identifier")
    experiment_type: ExperimentType = Field(..., description="Experiment type")
    component_name: str = Field(..., description="Component being built")
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = Field(None)
    
    # Metrics
    time_to_green: Optional[float] = Field(None, description="Minutes to passing tests")
    rework_cycles: int = Field(0, description="Number of correction iterations")
    spec_drift_count: int = Field(0, description="Number of spec violations")
    editor_friction_count: int = Field(0, description="Manual edits required")
    
    # Results
    success: bool = Field(False, description="Whether experiment succeeded")
    final_quality_score: Optional[float] = Field(None, description="Final quality assessment")
    artifacts_generated: List[str] = Field(default_factory=list, description="Generated files")
    issues_encountered: List[str] = Field(default_factory=list, description="Problems faced")


class ExperimentMetrics(BaseModel):
    """Aggregated metrics across experiments"""
    experiment_type: ExperimentType
    total_runs: int = Field(0)
    success_rate: float = Field(0.0)
    avg_time_to_green: Optional[float] = Field(None)
    avg_rework_cycles: float = Field(0.0)
    avg_quality_score: Optional[float] = Field(None)


# =============================================================================
# ERROR HIERARCHY
# =============================================================================

class SpecPlaneError(Exception):
    """Base exception for SpecPlane system"""
    pass


class ConfigurationError(SpecPlaneError):
    """Configuration loading or validation errors"""
    pass


class PatternMatchError(SpecPlaneError):
    """Pattern matching failures"""
    pass


class QuestionGenerationError(SpecPlaneError):
    """Question generation failures"""
    pass


class SessionStateError(SpecPlaneError):
    """Invalid session state transitions"""
    pass


class ValidationError(SpecPlaneError):
    """Validation failures"""
    pass


class ArtifactGenerationError(SpecPlaneError):
    """Artifact generation failures"""
    pass


# =============================================================================
# QUALITY GATES VALIDATION
# =============================================================================

class QualityGate(BaseModel):
    """Individual quality gate definition"""
    name: str = Field(..., description="Gate name")
    command: str = Field(..., description="Command to run")
    success_criteria: str = Field(..., description="What constitutes success")
    timeout_seconds: int = Field(30, description="Maximum execution time")


# Standard quality gates for all components
STANDARD_QUALITY_GATES = [
    QualityGate(
        name="type_checking",
        command="mypy specplane/ --strict",
        success_criteria="No type errors reported"
    ),
    QualityGate(
        name="unit_tests", 
        command="pytest tests/ -v",
        success_criteria="All tests pass"
    ),
    QualityGate(
        name="code_style",
        command="black --check specplane/ tests/",
        success_criteria="No formatting issues"
    ),
    QualityGate(
        name="import_sorting",
        command="isort --check-only specplane/ tests/",
        success_criteria="Imports properly sorted"
    ),
    QualityGate(
        name="cli_smoke_test",
        command="python -m specplane --help",
        success_criteria="Help command returns successfully"
    )
]


# =============================================================================
# USAGE INSTRUCTIONS
# =============================================================================

"""
USAGE INSTRUCTIONS FOR EXPERIMENTS:

1. Include this entire header in ALL experiment prompts
2. Reference these types instead of creating new ones
3. Use STANDARD_QUALITY_GATES for validation
4. Track metrics using ExperimentRun model

Example prompt header:
```
[PASTE ENTIRE SYSTEM CONTRACTS HEADER]

# Experiment: Component-Kernel Build
# Component: Pattern_Library  
# Expected Types: Pattern, ReasoningChain, ComponentContext
# Quality Gates: All STANDARD_QUALITY_GATES must pass

Now implement the Pattern_Library component...
```
"""