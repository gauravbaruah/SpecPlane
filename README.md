# SpecPlane 

> Interactive design thinking agent that transforms vague component ideas into detailed, validated specifications for AI-assisted development.

## What It Does

SpecPlane asks the **right questions** to surface critical design decisions before you start coding:

- **"What happens if this component fails?"** → Better error handling
- **"What are all the possible states?"** → Complete state management  
- **"What APIs does this call?"** → Robust integration patterns
- **"How will you know it's working?"** → Clear acceptance criteria

## The Problem

AI coding tools are powerful but produce brittle code when given vague requirements:

```
❌ "Build a voice recording widget"
→ AI generates basic component missing edge cases

✅ "Build a voice recording widget that handles microphone 
   permissions, storage limits, background interruption, 
   network failures, and provides clear user feedback"
→ AI generates production-ready component
```

## Quick Start

```bash
# Install
pip install -e .

# Design a component
specplane guide "VoiceRecorderWidget" --type widget

# Follow the guided interview (10-15 minutes)
# Get generated outputs:
# → specs/voice_recorder.yaml      (SpecPlane specification)
# → prompts/voice_recorder.md      (Ready-to-use Cursor prompt)  
# → reports/coverage.md            (Design completeness score)
```

## Example Output

**Generated Cursor Prompt:**
```markdown
Implement VoiceRecorderWidget for React Native.

PURPOSE: Enable quick voice note capture without typing friction

CRITICAL EDGE CASES:
- Microphone permission denied → Show settings deep-link
- Storage full → Check space first, suggest cleanup  
- Background interruption → Resume recording on return
- Network timeout → Save locally, sync later

STATES: idle, recording, paused, processing, complete, error

PERFORMANCE: Max 120s duration, <2MB files, <100ms UI response

Generate component with proper state management, error handling, 
and accessibility support...
```

## Philosophy

**Better upfront thinking → Better AI-generated code → Fewer bugs**

SpecPlane doesn't replace coding. It makes coding more intentional by front-loading the hard questions that prevent most production issues.

## Architecture

```
specplane/          # System design specs
├── context.yaml    # System overview
├── containers/     # Service boundaries  
├── components/     # Feature specifications
├── code/           # Module specifications 
└── linked/         # Shared contracts

app/               # Implementation
├── main.py        # CLI interface
├── interview.py   # Guided questioning
└── generator.py   # Spec generation
```

## Status

**Prototype 0** - Proving the core hypothesis with minimal viable implementation.

---

*"The best time to think about edge cases is before you write the code."*



## Directory Structure for SpecPlane Framework
```
specplane/
  context.yaml                    # ✅ System overview
  containers/
    cli.yaml                     # ✅ CLI interface
    orchestrator.yaml            # ✅ Session orchestration
    generator.yaml               # ✅ Spec generation
    storage.yaml                 # ✅ Data persistence
  components/
    interview_engine.yaml        # ✅ Question flow logic
    coverage_scorer.yaml         # ✅ Coverage calculation
    spec_generator.yaml          # ✅ YAML generation
    risk_assessor.yaml          # ➕ Risk identification
    template_renderer.yaml      # ➕ Jinja2 rendering
  code/
  linked/
    openapi.yaml                # ✅ API contracts
    events.csv                  # ✅ Event definitions
    schemas/
      SpecPlaneSpec.json        # ✅ Output schema
      QuestionBank.json         # ✅ Question schema
      Session.json              # ➕ Session state schema
      CoverageReport.json       # ➕ Coverage schema
  questions.yaml                # ✅ Question bank
  dfd.mmd                      # ➕ Data flow diagram
  state_machines.mmd           # ➕ Session state flows
  reports/.gitkeep             # ✅ Generated reports
  out/.gitkeep                 # ✅ Generated specs
```   