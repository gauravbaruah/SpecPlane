---
section: 09-diagrams-and-refs
canonical: ../specplane_schema_prompt_v9.1.0.md
---

# Applicable: Diagram types and using refs in diagrams

Load this file for the task in the [loading contract](README.md). Do not load the full master prompt unless you are changing the schema itself or the user asks for the complete reference.

Canonical source: `../specplane_schema_prompt_v9.1.0.md` (same content, one file).

---

## 📚 Diagram Type Catalog & Usage Guidance

| Diagram Type | Best For | Common Patterns |
|---|---|---|
| **sequence** | Request/response flows, actor interactions | Auth flows, agent-to-agent handoffs, API calls |
| **flowchart** | Decision trees, business logic, error handling | Branching, retry logic, agent routing |
| **state** | Component lifecycle, state machines | Login states, agent execution states |
| **class** | Component structure, data relationships | Domain models, tool registry structure |
| **architecture** | System topology, data flow | Agentic backend layout, microservices |
| **user_journey** | End-to-end UX flows | Onboarding, purchase flow, AI-assisted workflows |
| **timeline** | Schedules, phases, event sequences | Release timeline, migration plan |
| **mindmap** | Concept hierarchies, brainstorming | Capability map, feature exploration |
| **system_context** | C4 Level 1: System + capability boundaries | System landscape, capability overlay |
| **container** | C4 Level 2: Deployment units | Agentic backend + data_model + evaluations |

---

## 🔗 Using References in Diagrams

```yaml
refs:
  - id: "figma_login"
    type: "design"
    title: "Login Screen Mockup V2"
    url: "https://figma.com/file/xyz"
    status: "active"

  - id: "system_prompt_v3"
    type: "prompt"
    title: "Agent System Prompt v3"
    path: "./prompts/agent_v3.baml"
    version: "3.0.0"

diagrams:
  - type: "sequence"
    mermaid: |
      sequenceDiagram
          Note over U,App: Design: {{refs.figma_login.title}}
          click App "{{refs.figma_login.url}}" "View Design"
```

**Reference type auto-detection:**
- `figma.com` → `design` | `atlassian.net|jira.com` → `ticket` | `linear.app` → `ticket`
- `docs.google.com` → `doc` | `.png|.jpg|.svg` → `image` | `.mp4|.mov` → `video`
- `.baml|.prompt|system_prompt` → `prompt` | other `.yaml` SpecPlane files → `spec`
- incident tracking URLs (PagerDuty, Opsgenie, Statuspage) → `incident`
- post-mortem docs (Notion, Confluence, Google Docs titled "post-mortem") → `postmortem`
