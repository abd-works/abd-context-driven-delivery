### Rule: The Overview names what the system owns AND what it does not

The central spec's Overview MUST state both halves of the system boundary: what the system is responsible for AND what it is explicitly not responsible for. The negative half is what stops scope creep and stops AI assistants from inventing responsibilities the system never had. The boundary line is the single most useful sentence in the spec because every later decision flows from it. Passing means the Overview answers "what is this for?" and "what should I never build here?" in two or three sentences. Failing means the Overview describes only what the system does and lets the reader (or AI) infer the boundary by absence.

#### DO

- State what the system is and what it is NOT responsible for, naming the systems or layers that own what this one disowns.

  **Example (pass):**
  ```markdown
  ## Overview

  Acme Gateway is a boundary service between customer-facing channels and
  the partner systems that own subscriber state. It validates inbound work,
  calls the right partner adapter, maps the response, and returns it.

  It does NOT own subscriber state (Mavenir owns that), billing rules
  (Zoho owns those), or identity records (Cognito owns those). It does NOT
  retain request data beyond the lifetime of a single request.

  > **Sources:** ADR-001 (boundary-not-domain decision); blueprint.md.
  ```

- Name the responsibilities at the boundary so the reader can place new feature work on the right side.

  **Example (pass):** "Payments orchestration owns the choice of provider and the retry policy. It does NOT own provider-specific failure mapping — each provider adapter does." A new feature that adds a provider failure message clearly belongs in the adapter, not in orchestration.

#### DO NOT

- Describe the system in positive terms only.

  **Example (fail):**
  ```markdown
  ## Overview

  Acme Gateway is the API for the platform. It exposes endpoints to
  customer-facing applications and proxies them to backend systems.
  ```
  What's outside the gateway? The reader has to guess; the next person inventing a new responsibility puts it here by default.

- Use a generic statement that fits any service.

  **Example (fail):** "Acme Gateway is a microservice in the Acme platform that provides API access to data." — true of every microservice ever; tells the reader nothing.

- Bury the boundary in a later section.

  **Example (fail):** The Overview describes capabilities; the "what we don't own" list lives in a Decision section three pages down. Most readers stop after the Overview.

**Source:** Arc42 § Solution Strategy and C4 § Context — a system's boundary is the first decision; documentation that hides it lets the boundary erode silently.
