---
section: 07-ai-native
canonical: ../specplane_schema_prompt_v9.1.0.md
---

# Applicable: AI-native component types, ai_config, NodeContext

Load this file for the task in the [loading contract](README.md). Do not load the full master prompt unless you are changing the schema itself or the user asks for the complete reference.

Canonical source: `../specplane_schema_prompt_v9.1.0.md` (same content, one file).

---

# ============================================
# AI CONFIG (for AI-native component types)
# ============================================
# Only include when meta.type is one of:
# agent | tool | workflow | tool_registry | state_store | evaluator

# ── FOR meta.type: "agent" ─────────────────────────────────────────
ai_config:
  role: ""
  tools: []
  memory:
    strategy: "stateless|turn_based|persistent"
    schema_ref: ""
  model:
    capability: "fast|balanced|capable"
    context_window: ""
  output_contract: ""
  handoffs:
    - to: ""
      condition: ""
  human_in_loop:
    trigger: ""
    escalation: ""

# ── FOR meta.type: "tool" ──────────────────────────────────────────
ai_config:
  computation_type: "compute|ai_structured|ai_classify|ai_extract|hybrid"
  is_destructive: false
  authorization_required: ""
  output_contract: ""
  returns_provenance: false
  call_sites: []
  modes: []
  cost_hint: "cheap|medium|expensive"
  timeout_ms: 0

# ── FOR meta.type: "workflow" ──────────────────────────────────────
ai_config:
  pattern: "sequential|parallel|router|directed_graph|loop"
  computation_model:
    orchestration: ""
    computation: ""
    structure: ""
  state_schema:
    identity: []
    input: []
    routing: []
    working: []
    output: []
  nodes:
    - id: ""
      purpose: ""
      computation_type: "compute|ai_structured|ai_classify|ai_extract|hybrid|route"
      inputs: []
      outputs: []
      output_contract: ""
      constrained_inputs: []
  edges:
    - from: ""
      to: ""
      condition: ""
  entry_node: ""
  terminal_nodes: []
  trigger: "api_call|event|schedule|webhook"
  streaming: false

# ── FOR meta.type: "tool_registry" ─────────────────────────────────
ai_config:
  provides_discovery: true
  provides_validation: true
  node_allowlists: true
  mcp_compatible: false

# ── FOR meta.type: "state_store" ───────────────────────────────────
ai_config:
  persistence: "in_memory|database|vector_store|cache"
  schema_ref: ""
  access_pattern: "read_write|read_only|append_only"

# ── FOR meta.type: "evaluator" ─────────────────────────────────────
ai_config:
  eval_type: "invariant|dataset|scorer|sim_generator"
  # invariant      → hard rule that must always hold; fails if violated
  #                  e.g., "response must never contain PII", "output schema must be valid JSON"
  # dataset        → a set of input/expected-output pairs used to measure model accuracy or regression
  #                  e.g., labelled test cases for a classification tool
  # scorer         → a function or LLM judge that assigns a quality score to a model output
  #                  e.g., "rate coherence 1–5", "check if answer is grounded in context"
  # sim_generator  → generates synthetic inputs to stress-test the system at scale
  #                  e.g., produce 1000 varied user queries to probe edge cases before launch
  target: ""        # The component or workflow this evaluator tests (meta.id)
  scoring_method: "" # How outputs are judged: e.g., "exact_match", "llm_judge", "human_review", "regex"
  threshold: ""      # Pass/fail threshold: e.g., ">0.85 accuracy", "0 invariant violations"

# ============================================
# OPTIONAL: IMPLEMENTATION HINTS
# ============================================
implementation_hints:
  web: {}
  mobile: {}
  api: {}
  desktop: {}
  ai:
    framework: ""
    output_schema: ""
    llm_provider: ""
    model_id: ""
    vector_store: ""
    agent_memory: ""

# ============================================
# EVIDENCE & TRACEABILITY
# ============================================
evidence:
  user_research: ""
  technical_analysis: ""
  design_artifacts: ""

# ============================================
# DIAGRAMS
# ============================================
diagrams:
  - type: "sequence|flowchart|state|class|architecture|user_journey|timeline|mindmap|system_context|container"
    title: ""
    description: ""
    mermaid: |
      # Mermaid diagram code here
```


## 🤖 NodeContext Pattern (AI-Native Best Practice)

The NodeContext pattern prevents AI from hallucinating invalid tool names, chart types, or other constrained values. Use it whenever an AI node must choose from a finite set of options.

**The pattern:**
```
1. Python builds an allowed-set from registry + current state
2. Pass allowed-set to AI as input alongside the task
3. AI selects only from the provided menu
4. Python validates AI output against the allowed-set; reject or clamp if outside bounds
```

**In a spec, capture it with `constrained_inputs`:**
```yaml
nodes:
  - id: "PlanQuery"
    computation_type: "ai_structured"
    constrained_inputs:
      - "allowed_tools"
      - "allowed_chart_types"
    output_contract: "baml_extract_plan"
```
