---
section: 08-validation-rules
canonical: ../specplane_schema_prompt_v9.1.0.md
---

# Applicable: File validation rules and bidirectional-link checks

Load this file for the task in the [loading contract](README.md). Do not load the full master prompt unless you are changing the schema itself or the user asks for the complete reference.

Canonical source: `../specplane_schema_prompt_v9.1.0.md` (same content, one file).

---

## 🔧 Tooling & Validation

### **File Validation Rules**

1. **Filename matches meta.id**
   ```bash
   # ✅ Valid
   File: capability.authentication.yaml → meta.id: "capability.authentication"
   File: component.login_form.yaml      → meta.id: "component.login_form"

   # ❌ Invalid
   File: capability.authentication.yaml → meta.id: "authentication"
   ```

2. **Capability files live in `specs/capabilities/`**
   ```bash
   # ✅ Valid
   specs/capabilities/capability.authentication.yaml

   # ❌ Invalid
   specs/capability.authentication.yaml        # Should be in capabilities/
   specs/containers/capability.authentication.yaml
   ```

3. **`implements` references existing capability specs**
   ```yaml
   # ✅ Valid
   implements:
     - "capability.authentication"   # File exists: capabilities/capability.authentication.yaml

   # ❌ Invalid
   implements:
     - "authentication"              # Missing level prefix
     - "capability.nonexistent"      # File doesn't exist
   ```

4. **`realized_by` references existing containers/components**
   ```yaml
   # ✅ Valid
   realized_by:
     containers: ["container.web_app"]
     components: ["component.login_form"]

   # ❌ Invalid
   realized_by:
     components: ["login_form"]      # Missing level prefix
   ```

5. **`system_context.capabilities` references existing capability specs**
   ```yaml
   # ✅ Valid
   system_context:
     capabilities: ["capability.authentication"]

   # ❌ Invalid
   system_context:
     capabilities: ["authentication"]
   ```

6. **`ai_config` only on AI-native types**
   ```yaml
   # ✅ Valid
   meta:
     type: "workflow"
   ai_config:
     pattern: "directed_graph"

   # ❌ Invalid — ai_config not applicable to capability, system, or standard component types
   meta:
     level: "capability"
   ai_config: ...
   ```

7. **`type` must be valid for the `level`**
   ```yaml
   # ✅ Valid
   meta:
     level: "component"
     type: "agent"

   # ❌ Invalid — capability and foundation specs have no type field
   meta:
     level: "capability"
     type: "service"

   # ❌ Invalid — container level only allows type: "container"
   meta:
     level: "container"
     type: "widget"
   ```

8. **`realized_by` only on capability specs; `used_by` only on foundation specs**
   ```yaml
   # ✅ Valid
   # capability spec:
   realized_by:
     containers: ["container.web_app"]

   # foundation spec:
   used_by:
     components: ["component.login_form"]

   # ❌ Invalid — realized_by does not exist on foundation specs
   # foundation spec:
   realized_by: ...
   ```

9. **`meta.version` must be valid semver**
   ```bash
   # ✅ Valid
   version: "1.0.0"
   version: "2.3.1"

   # ❌ Invalid
   version: "v1"        # Missing minor and patch
   version: "1.0"       # Missing patch
   version: "draft"     # Not semver
   ```

10. **`changelog` required when `meta.version` changes**
    ```yaml
    # ✅ Valid — version bumped and changelog entry added
    meta:
      version: "1.1.0"
    changelog:
      - date: "2026-03-01"
        author: "james"
        summary: "Added Token refresh flow"
        breaking: false

    # ❌ Invalid — version bumped but no changelog entry for this date
    meta:
      version: "1.1.0"
    changelog: []
    ```

11. **Breaking changes require `breaking: true` in changelog**
    ```yaml
    # ✅ Valid — API contract changed and flagged
    changelog:
      - date: "2026-03-01"
        author: "dev"
        summary: "Renamed /auth/login to /auth/session"
        breaking: true

    # ❌ Invalid — API renamed but breaking not flagged (CI should block this PR)
    changelog:
      - date: "2026-03-01"
        author: "dev"
        summary: "Renamed /auth/login to /auth/session"
        breaking: false
    ```

12. **`introduced_in` required on all specs; `deprecated_in` required when `status: "deprecated"`**
    ```yaml
    # ✅ Valid — active spec with introduction version
    meta:
      version: "2.1.0"
      introduced_in: "1.0.0"
      status: "active"

    # ✅ Valid — deprecated spec with full evolution range
    meta:
      version: "3.0.0"
      introduced_in: "1.0.0"
      deprecated_in: "3.0.0"
      status: "deprecated"
      replaced_by: "component.auth_service_v2"

    # ❌ Invalid — deprecated but deprecated_in missing
    meta:
      status: "deprecated"
      deprecated_in: ""      # CI cannot compute deprecation age or enforce migration gates
    ```

13. **`replaced_by` required when `status: "deprecated"`**
    ```yaml
    # ✅ Valid — deprecated with a clear successor
    meta:
      status: "deprecated"
      replaced_by: "foundation.security_baseline_v2"
      migration_notes: "Update all uses: references to foundation.security_baseline_v2; review new rate_limiting.burst_allowance field"

    # ❌ Invalid — deprecated but no successor or migration guidance
    meta:
      status: "deprecated"
      replaced_by: ""
    ```

14. **`replaced_by` must reference an existing spec by meta.id**
    ```yaml
    # ✅ Valid
    replaced_by: "component.auth_service_v2"   # File exists: components/.../component.auth_service_v2.yaml

    # ❌ Invalid
    replaced_by: "auth_service_v2"             # Missing level prefix
    replaced_by: "the new auth service"        # Not a meta.id
    ```

15. **Component `data_classification` must not be weaker than the parent capability's**
    ```yaml
    # Strictness order (weakest → strictest): public → internal → confidential → regulated

    # ✅ Valid — component is as strict as its capability
    # capability.authentication: data_classification: "confidential"
    # component.login_form: data_classification: "confidential"

    # ✅ Valid — component is stricter than its capability
    # capability.authentication: data_classification: "confidential"
    # component.token_service: data_classification: "regulated"

    # ❌ Invalid — component is weaker than its capability
    # capability.authentication: data_classification: "regulated"
    # component.login_form: data_classification: "public"
    ```

16. **`test_strategy` CI inference rules**
    ```yaml
    # CI derives test requirements as follows:
    # unit != ""        → run unit tests
    # integration != "" → run integration tests
    # e2e != ""         → run E2E tests (Playwright MCP for web; Maestro for Flutter/mobile if configured)
    # performance: true → run load/performance tests
    # data_classification: "confidential" or "regulated" → run security tests

    # ✅ Valid — e2e not required for an internal utility component
    test_strategy:
      unit: "cover all transformation branches; >90% on business logic"
      integration: "verify contract with component.data_store"
      e2e: ""
      performance: false

    # ❌ Invalid — security test not enforced but component handles regulated data
    # (data_classification: "regulated" on the parent capability means CI must require security testing)
    test_strategy:
      unit: "basic coverage"
      e2e: ""
      performance: false
    # Missing: security testing gate is implied by regulated data_classification
    ```

17. **`rollout.feature_flag` is required when strategy is `feature_flag` or `dark_launch`**
    ```yaml
    # ✅ Valid
    rollout:
      strategy: "feature_flag"
      feature_flag: "referral_program_enabled"
      rollback_trigger: "error_rate > 1% for 5min"

    # ✅ Valid — immediate rollout, no flag needed
    rollout:
      strategy: "immediate"
      rollback_trigger: "p99_latency > 2s"

    # ❌ Invalid — strategy requires feature_flag key but it's missing
    rollout:
      strategy: "feature_flag"
      feature_flag: ""
    ```

18. **All bidirectional relationships must be kept in sync (both sides required)**

    The following pairs are bidirectional. Adding an ID to one side **requires** adding the reciprocal ID to the other. CI must validate both directions.

    | If you add X to... | You must also add Y to... |
    |---|---|
    | `implements: ["capability.X"]` on a component | `realized_by.components: ["component.Y"]` on the capability |
    | `uses: ["foundation.X"]` on a component/container | `used_by.components/containers: ["component.Y"]` on the foundation |
    | `dependencies.internal: ["component.X"]` on a component | `depended_on_by.components: ["component.Y"]` on the dependency |
    | `relationships.depends_on: ["container.X"]` on a container | `depended_on_by.containers: ["container.Y"]` on the dependency |

    ```yaml
    # ✅ Valid — both sides populated
    # component.login_form:
    dependencies:
      internal: ["component.token_service"]

    # component.token_service:
    depended_on_by:
      components: ["component.login_form"]

    # ❌ Invalid — only one side populated
    # component.login_form lists component.token_service in dependencies.internal
    # but component.token_service has no depended_on_by entry for component.login_form
    ```

19. **Analytics traceability** — *Only when* `analytics_events` is non-empty *or* `uses` includes `foundation.analytics_conventions`:
    - Each capability `analytics_events[].emitted_by` must reference a component in `realized_by.components`.
    - Each such component must list that event in `planning.analytics.events[].name`.
    - No other component may emit the same event (single-source-of-truth; see foundation).
    - When present, `success_metrics.derived_from` must reference event names that exist in `analytics_events`.
    - When `planning.analytics.events` is non-empty, each event must list `properties` (or reference `foundation.analytics_conventions.properties.common`) so contract-test generation can validate payloads.

20. **Ref resolution** — All refs used in diagrams (`{{refs.<id>.<field>}}`) must have a resolvable `url` or `path`. At least one of `url` or `path` must be non-empty for each ref that is interpolated into diagrams or descriptions.

21. **No conflicting property names** — Property names used in analytics events, observability metrics, and contracts must not conflict (e.g. `invited_count` in one section and `invitedCount` in another for the same concept). Use consistent identifiers across sections; prefer snake_case.

22. **Capability `flows` item shape** — Each item is a non-empty string or a mapping. A mapping requires a non-empty `id`. `goal` and journey / lifecycle / information keys are optional. String items stay valid.
    ```yaml
    # ✅ Valid
    flows:
      - "Sign-up"
      - id: invite_member

    # ❌ Invalid — mapping without id
    flows:
      - goal: "Add a member"
    ```
