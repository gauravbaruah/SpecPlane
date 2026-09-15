---
section: 10-worked-examples
canonical: ../specplane_schema_prompt_v9.1.0.md
---

# Applicable: Worked capability and component examples

Load this file for the task in the [loading contract](README.md). Do not load the full master prompt unless you are changing the schema itself or the user asks for the complete reference.

Canonical source: `../specplane_schema_prompt_v9.1.0.md` (same content, one file).

---

## 📋 Complete Example: Capability Spec

```yaml
meta:
  id: "capability.authentication"
  purpose: "Allow users to securely prove identity, establish a session, and access their account"
  level: "capability"
  owner: "Product Team"
  tags: ["auth", "security", "legal", "core"]
  status: "in_progress"
  last_updated: "2026-01-15"
  version: "1.0.0"

# ── PHASE 1 (Required) ─────────────────────────────────────────────

responsibilities:
  - "Identity verification (email/password and OAuth)"
  - "Session establishment and token lifecycle"
  - "Consent capture and legal record"
  - "Logout and session revocation"
  - "Account lockout and rate limiting"

flows:
  - "Sign-up"
  - "Login (email/password)"
  - "Login (OAuth — Google, Apple)"
  - "Token refresh"
  - "Logout"
  - "Password reset"

business_value:
  user_outcome: "Users can securely access their personalized account from any device"
  objective: "Enable personalization and reduce drop-off at account creation"
  revenue_dependency: "high"
  strategic_priority: "core"

constraints:
  legal:
    - "GDPR: explicit consent required before account creation; record must be stored"
    - "CCPA: users must be able to request account deletion"
  security:
    - "PKCE required for all OAuth flows"
    - "Tokens stored in httpOnly cookies only — never localStorage"
    - "Passwords hashed with bcrypt, work factor ≥ 12"
  ux:
    - "Explicit consent gate must block account creation until accepted"
    - "Locked account must show clear unlock instructions and support contact"

# ── PHASE 2 (Optional) ─────────────────────────────────────────────

# When using product analytics — see foundation.analytics_conventions
analytics_events:
  - name: "login_attempted"
    when: "user submits login form"
    properties: ["source", "method"]
    emitted_by: "component.login_form"
  - name: "login_succeeded"
    when: "auth succeeds and session established"
    properties: ["method", "duration_ms"]
    emitted_by: "component.login_form"

success_metrics:
  primary: "login_success_rate"
  targets:
    login_success_rate: ">99%"
    consent_capture_completion_rate: ">95%"
    account_creation_drop_off: "<10%"
  derived_from:
    login_success_rate: ["login_attempted", "login_succeeded"]

roadmap:
  phase: "v1.0 launch"
  priority: "P0"
  depends_on: []
  enables:
    - "capability.onboarding"
    - "capability.data_analytics"

# ── PHASE 3 (Engineering-added) ────────────────────────────────────

realized_by:
  containers:
    - "container.web_app"
    - "container.api_gateway"
  components:
    - "component.login_form"
    - "component.consent_capture"
    - "component.auth_callback_handler"
    - "component.auth_api"
    - "component.token_service"
    - "component.session_store"
    - "component.authorization_guard"

# ── SHARED ─────────────────────────────────────────────────────────

refs:
  - id: "auth_epic"
    type: "ticket"
    title: "Authentication System Epic"
    url: "https://company.atlassian.net/browse/AUTH-100"
    owner: "Product"
    tags: ["epic", "v1"]

  - id: "gdpr_policy"
    type: "doc"
    title: "GDPR Consent Policy v2"
    url: "https://docs.company.com/legal/gdpr"
    owner: "Legal"
    status: "active"

diagrams:
  - type: "sequence"
    title: "End-to-end authentication flow"
    description: "Cross-system flow spanning web_app, api_gateway, and external auth provider"
    mermaid: |
      sequenceDiagram
        actor U as User
        participant W as Web App
        participant Auth as Auth Provider
        participant A as API Gateway
        participant S as Session Store

        U->>W: Enter credentials / select OAuth
        W->>Auth: OAuth authorize (PKCE)
        Auth-->>W: Authorization code
        W->>A: POST /auth/callback {code}
        A->>Auth: Exchange code for token
        Auth-->>A: Access + refresh tokens
        A->>S: Create session
        S-->>A: Session ID
        A-->>W: Set httpOnly session cookie
        W-->>U: Redirect to dashboard

        Note over W,A: Consent captured before this flow if new user
        Note over A: Analytics: login_succeeded
        Note over A,S: Observability: auth_flow_complete trace
```

---

## 📋 Complete Example: Component with `implements`

```yaml
meta:
  id: "component.login_form"
  purpose: "Enable users to authenticate with email/password or OAuth providers"
  level: "component"
  owner: "Auth Team"
  tags: ["auth", "security", "frontend"]
  status: "active"
  last_updated: "2026-01-15"
  version: "2.1.0"
  type: "widget"
  domain: "frontend"

implements:
  - "capability.authentication"   # ← declares which capability this serves

refs:
  - id: "figma_login"
    type: "design"
    title: "Login Form Design V2.1"
    url: "https://figma.com/file/abc123"
    owner: "UX Team"
    status: "active"

planning:
  user_flows:
    actions:
      - "User enters email and password"
      - "User clicks login button"
      - "User selects OAuth provider (Google, Apple)"
    success:
      - "User sees dashboard within 2 seconds"
      - "Session persists across browser restarts (if remember me checked)"
    errors:
      - "Invalid credentials → clear error message with retry option"
      - "Account locked → show unlock instructions and support contact"
      - "Network timeout → show retry with exponential backoff"

  analytics:
    success_metric: "successful_login_rate"
    target: ">95% of login attempts succeed within 3 attempts"
    default_destinations: ["mixpanel", "amplitude"]
    events:
      - name: "login_attempted"
        when: "User clicks login button"
        properties:
          method: "email|google|apple"
      - name: "login_succeeded"
        when: "Authentication successful"
        properties:
          method: "email|google|apple"
          duration_ms: "number"

implementation:
  interface:
    capabilities:
      - "validate_email_format"
      - "authenticate_user"
      - "handle_oauth_callback"
      - "manage_session_state"
    inputs:
      - "email: string"
      - "password: string"
      - "remember_me: boolean"
    outputs:
      - "auth_token: string"
      - "user_id: string"
    side_effects:
      - "Creates user session in backend"
      - "Emits auth_state_changed event"

  contracts:
    apis:
      - endpoint: "/api/auth/login"
        method: "POST"
        request: {email: "string", password: "string", remember_me: "boolean"}
        response: {token: "string", user_id: "string", expires_at: "timestamp"}
        errors:
          - {code: 401, reason: "invalid_credentials"}
          - {code: 423, reason: "account_locked"}
          - {code: 429, reason: "rate_limit_exceeded"}

  dependencies:
    internal:
      - "component.error_toast"
      - "component.loading_spinner"
    external:
      - "Auth0 Authentication API"

  observability:
    slos:
      - "login_success_rate ≥ 99.5%"
      - "login_latency_p95 < 500ms"
    alerting:
      critical:
        - "login_success_rate < 95% for 5 minutes → Page on-call"
      warning:
        - "login_latency_p95 > 1s for 10 minutes → Notify #auth-team"

  technical_constraints:
    security:
      authentication: "OAuth 2.0 + PKCE, bcrypt for passwords"
      compliance: "GDPR, SOC 2 Type II"
      threats: ["credential_stuffing", "brute_force_attacks"]
      mitigations:
        - "Rate limiting: 5 attempts per 15 minutes per IP"
        - "Account lockout after 10 failures"

  validation:
    acceptance_criteria:
      - "Valid credentials → dashboard within 2s"
      - "Invalid credentials → clear error message"
      - "6th attempt blocked by rate limiting"
      - "Consent gate shown to new users before login completes"
    readiness: "ready"
```
