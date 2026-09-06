### Rule: Surrounding systems are discovered, not assumed

The outline must establish a complete picture of every system the subject connects to — callers and downstreams — before any package or mechanism decision is made. This requires active discovery: from the codebase (HTTP clients, SDK imports, env vars pointing at external hosts), from the user (integrations in flight, planned connections, manual handoffs that happen outside the code), and from any existing documentation. An outline that names only the systems the author already knows about is not an outline — it is a partial map that will corrupt every decision made from it.

The surrounding-systems table is the *output* of that discovery. Every entry must answer two questions a downstream reader needs to reason from: what does this system do, and what is its role relative to the subject? If either answer is missing, the discovery is incomplete.

#### DO

- Treat discovery as a step, not a formality. For each system already named, ask: who else does this system talk to? Are there manual processes (Slack notifications, spreadsheet exports, support tool integrations) that are part of the operational reality even if they are not in the code yet?

  **Example (pass):** Codebase shows HTTP calls to Mavenir, Cognito, Zendesk, and Twilio. User confirms a Voucher Lambda and Persona integration not yet in the main branch. A planned Fygaro payment integration is in the roadmap. All appear in the table — the map reflects the real operational boundary, not just what is merged.

- For each entry, state what the connected system does (not just what it's called) and what crosses the boundary in each direction.

  **Example (pass):** `| **AWS Cognito** | Identity provider — issues and validates JWTs for subscriber accounts. | **Downstream** — JWT verified on every protected route; token exchange invoked during onboarding login |`

- Flag entries that are uncertain or planned so the team can correct or confirm them.

  **Example (pass):** `| **n8n** | Workflow automation — receives onboarding trigger webhooks. | **Downstream (unconfirmed)** — integration hooks exist in InternalRoutes; exact event contract not yet agreed |`

#### DO NOT

- List only the systems that were obvious from a first read of the codebase and call the table done.

  **Example (fail):** A midtier with 14 integration points lists 4. The remaining 10 are discovered during blueprint work — after package boundaries have already been drawn around the wrong surface.

- Use the table as a formatting exercise — copy system names from imports without understanding what crosses the boundary or who initiates.

  **Example (fail):** `| **Twilio** | SMS provider. | Downstream |` — tells a reader nothing about what triggers a Twilio call, what data crosses the boundary, or whether the subject or Twilio initiates.

- Defer discovery to a later fidelity level.

  **Example (fail):** "We'll add the remaining integrations at blueprint stage once the code is better understood." The surrounding-systems table is the reason to do the outline — if the boundary is unknown, the outline cannot be started; stop and discover first.

**Source:** Practice-skill authoring convention (abd-architecture-outline); a system context that does not reflect the real operational boundary produces architecture decisions that do not survive contact with integration.
