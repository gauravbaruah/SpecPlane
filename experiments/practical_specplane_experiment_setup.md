# Practical SpecPlane Experiment Setup
## Step-by-Step Guide for Real Cursor Workflow

## 🎯 Reality Check

You're absolutely right - I over-engineered this! Here's what you actually need:

1. **Simple directory structure** that matches your workflow
2. **Step-by-step guidance** for each experiment  
3. **Manual measurement tracking** (you paste prompts, I help you measure)
4. **Contained experiments** in separate output folders

---

## 📁 Recommended Directory Structure

Based on your current setup, let's organize it properly:

```
.
├── experiments/
│   ├── building_specplane/           # Current experiment series
│   │   ├── prompts/                  # All the cursor prompts
│   │   │   ├── system_contracts.py  # The canonical types (from artifacts)
│   │   │   ├── exp1_source_of_truth.md
│   │   │   ├── exp2_component_kernels.md  
│   │   │   ├── exp3_spec_only.md
│   │   │   ├── exp4_spec_to_prompt.md
│   │   │   └── exp5_validator_loop.md
│   │   ├── exp1_output/              # Experiment 1 results
│   │   │   ├── specplane/            # Generated Python code
│   │   │   ├── tests/                # Generated tests
│   │   │   ├── experiment_log.md     # Your notes and observations
│   │   │   └── results.json          # Simple metrics
│   │   ├── exp2_output/              # Experiment 2 results  
│   │   │   ├── specplane/
│   │   │   ├── tests/
│   │   │   ├── experiment_log.md
│   │   │   └── results.json
│   │   ├── exp3_output/              # And so on...
│   │   ├── exp4_output/
│   │   ├── exp5_output/
│   │   └── comparison_analysis.md    # Final comparison
│   │
│   ├── building_mermaid_charts/      # Future experiment series
│   │   ├── prompts/
│   │   └── exp1_output/
│   │
│   └── building_reading_list_app/    # Future experiment series
│       ├── prompts/
│       └── exp1_output/
│
├── specplane/                        # Your spec files (keep as-is)
│   ├── components/
│   ├── config/
│   ├── containers/
│   ├── context.yaml
│   └── templates/
│
├── tools/                           # Helper scripts (simplified)
│   ├── simple_tracker.py           # Basic experiment tracking
│   └── quality_checker.py          # Basic quality validation
│
├── LICENSE
└── README.md
```

---

## 🚀 Step-by-Step Experiment Process

### Step 1: Prepare Experiment (5 minutes)

```bash
# Create experiment output directory
mkdir -p experiments/building_specplane/exp1_output
cd experiments/building_specplane/exp1_output

# Initialize basic project structure
mkdir -p specplane tests docs
touch experiment_log.md results.json
```

### Step 2: Run Cursor Experiment (30-60 minutes)

1. **Open Cursor** in the `exp1_output` directory
2. **Paste the prompt** (e.g., `exp1_source_of_truth.md`)
3. **Work with Cursor** to build the components
4. **Document what happens** in `experiment_log.md`

### Step 3: Measure Results (10 minutes)

Use simple tracking:

```bash
# Run basic quality checks
python ../../tools/quality_checker.py

# Log your observations
echo "Time taken: 45 minutes" >> experiment_log.md
echo "Components built: File_Storage, Pattern_Library" >> experiment_log.md
echo "Issues encountered: Had to clarify type annotations 3 times" >> experiment_log.md
```

---

## 📝 Simplified Tracking System

Instead of complex automation, let's use simple manual tracking:

### experiment_log.md Template
```markdown
# Experiment 1: Source of Truth Approach
**Date**: [Date]
**Duration**: [Start time] - [End time] ([Total minutes])
**Components Attempted**: [List]

## What Worked Well
- [Observation 1]
- [Observation 2]

## What Needed Manual Intervention  
- [Issue 1 and how you fixed it]
- [Issue 2 and how you fixed it]

## Cursor Behavior
- How well did Cursor understand the prompt?
- How many clarifications did you need to give?
- What code quality did it produce?

## Final Assessment
- **Success**: ✅/❌ Did you get working components?
- **Quality**: [1-5] How good was the generated code?
- **Efficiency**: [1-5] How much manual work was needed?

## Files Generated
- [List of files Cursor created]

## Next Steps
- [What would you do differently?]
- [What to test in next experiment?]
```

### results.json Template
```json
{
  "experiment": "exp1_source_of_truth",
  "date": "2024-12-15",
  "duration_minutes": 45,
  "components_attempted": ["File_Storage", "Pattern_Library"],
  "components_completed": ["File_Storage"],
  "success": true,
  "quality_score": 4,
  "efficiency_score": 3,
  "manual_interventions": 3,
  "files_generated": 8,
  "key_learnings": [
    "Needed to clarify type annotations",
    "Cursor understood architecture well",
    "File operations worked first try"
  ]
}
```

---

## 🔧 Simplified Tools

### tools/simple_tracker.py
```python
#!/usr/bin/env python3
"""Simple experiment tracking for SpecPlane experiments"""

import json
import os
from datetime import datetime
from pathlib import Path

def start_experiment(exp_name: str):
    """Start tracking an experiment"""
    data = {
        "experiment": exp_name,
        "start_time": datetime.now().isoformat(),
        "status": "in_progress"
    }
    
    with open("experiment_status.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"🔬 Started experiment: {exp_name}")
    print(f"⏰ Start time: {data['start_time']}")

def end_experiment(success: bool = True):
    """End experiment tracking"""
    if not os.path.exists("experiment_status.json"):
        print("❌ No active experiment found")
        return
    
    with open("experiment_status.json", "r") as f:
        data = json.load(f)
    
    data["end_time"] = datetime.now().isoformat()
    data["status"] = "completed" if success else "failed"
    
    # Calculate duration
    start = datetime.fromisoformat(data["start_time"])
    end = datetime.fromisoformat(data["end_time"])
    duration = (end - start).total_seconds() / 60
    data["duration_minutes"] = round(duration, 1)
    
    with open("results.json", "w") as f:
        json.dump(data, f, indent=2)
    
    os.remove("experiment_status.json")
    
    print(f"✅ Experiment completed in {duration:.1f} minutes")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python simple_tracker.py start <exp_name> | end [success/fail]")
    elif sys.argv[1] == "start":
        start_experiment(sys.argv[2])
    elif sys.argv[1] == "end":
        success = len(sys.argv) < 3 or sys.argv[2] != "fail"
        end_experiment(success)
```

### tools/quality_checker.py
```python
#!/usr/bin/env python3
"""Basic quality checks for generated code"""

import os
import subprocess
from pathlib import Path

def check_python_syntax():
    """Check if Python files have valid syntax"""
    python_files = list(Path("specplane").glob("**/*.py"))
    
    print("🐍 Checking Python syntax...")
    for file in python_files:
        try:
            with open(file) as f:
                compile(f.read(), file, 'exec')
            print(f"  ✅ {file}")
        except SyntaxError as e:
            print(f"  ❌ {file}: {e}")

def check_imports():
    """Check if imports work"""
    print("\n📦 Checking imports...")
    try:
        result = subprocess.run(
            ["python", "-c", "import specplane"],
            cwd=".",
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("  ✅ Main package imports successfully")
        else:
            print(f"  ❌ Import error: {result.stderr}")
    except Exception as e:
        print(f"  ❌ Import check failed: {e}")

def count_files():
    """Count generated files"""
    py_files = len(list(Path("specplane").glob("**/*.py")))
    test_files = len(list(Path("tests").glob("**/*.py")))
    yaml_files = len(list(Path(".").glob("**/*.yaml")))
    
    print(f"\n📊 Files generated:")
    print(f"  Python files: {py_files}")
    print(f"  Test files: {test_files}")
    print(f"  YAML files: {yaml_files}")

if __name__ == "__main__":
    check_python_syntax()
    check_imports()
    count_files()
```

---

## 🎯 Your First Experiment - Simplified Steps

### 1. Set Up Experiment 1 (2 minutes)
```bash
cd experiments/building_specplane
mkdir exp1_output
cd exp1_output
python ../../tools/simple_tracker.py start "exp1_source_of_truth"
```

### 2. Prepare Cursor Prompt (3 minutes)
- Copy `system_contracts.py` content 
- Copy `exp1_source_of_truth.md` content
- Combine them into one prompt for Cursor

### 3. Work with Cursor (30-60 minutes)
- Paste the combined prompt
- Build components step by step
- Document issues in `experiment_log.md` as you go

### 4. Measure and Wrap Up (5 minutes)
```bash
python ../../tools/quality_checker.py
python ../../tools/simple_tracker.py end
# Fill out experiment_log.md and results.json
```

---

## 🤔 Does This Feel More Manageable?

This approach:
- ✅ **Matches your actual workflow** with Cursor
- ✅ **Keeps experiments separated** in clear directories  
- ✅ **Simple manual tracking** that you can actually use
- ✅ **Step-by-step guidance** without overwhelming automation
- ✅ **Flexible structure** for future experiments

Want me to help you set up the first experiment with this simplified approach?