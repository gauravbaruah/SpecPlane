---
section: 05-foundation
canonical: ../specplane_schema_prompt_v9.1.0.md
---

# Applicable: Foundation spec schema

Load this file for the task in the [loading contract](README.md). Do not load the full master prompt unless you are changing the schema itself or the user asks for the complete reference.

Canonical source: `../specplane_schema_prompt_v9.1.0.md` (same content, one file).

---

# ============================================
# FOUNDATION SPEC (level: "foundation")
# ============================================
# Progressive disclosure:
#   Minimal: meta + provides + used_by
#   Full:    + content fields specific to the foundation type + refs + diagrams
#
# Foundation specs live in specs/foundations/.
# Components and containers reference them via `uses`.
# Foundations reference back via `used_by`.
# A foundation may extend another foundation via `extends`.

# (meta + changelog — see Shared Meta Block above; use foundation-specific status and review_state values)

# What this foundation provides to those who use it
provides:
  - ""    # e.g., "Color palette and semantic color tokens"
          # e.g., "API URL naming and versioning rules"

# Who uses this foundation (bidirectional with component/container `uses`)
used_by:
  containers: []    # container meta.ids
  components: []    # component meta.ids

# If this foundation builds on another foundation (e.g., component_library extends design_system)
extends: []         # foundation meta.ids

# Foundation-specific content fields
# These vary per foundation type — see boilerplate specs in specplane/foundations/
# for the canonical field shapes per category (Design, API, Technical, Compliance, AI, etc.)

refs: []
diagrams: []
