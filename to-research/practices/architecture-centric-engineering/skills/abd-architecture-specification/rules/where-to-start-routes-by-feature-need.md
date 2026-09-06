### Rule: Where to Start questions describe feature needs, not code artefacts

Every question in the Where to Start table MUST be answerable by someone reading the feature spec alone — a product owner, a new engineer who has not yet read the code, or an AI assistant without repository access. Questions that name code-only concepts (handlers, config keys, routes, status codes, schemas, modules) force the reader to already understand the architecture before they can route through it; this defeats the entire purpose of the table, which is to be the first thing a developer hits. Passing means every question is yes/no answerable from a user story or feature description. Failing means a question contains code vocabulary that the reader could only know after reading source.

#### DO

- Phrase questions in product or feature vocabulary — capabilities, user-facing requirements, system boundaries.

  **Example (pass):**
  ```markdown
  | Question | Read this |
  |---|---|
  | Is there a new downstream system to integrate with? | [src/integrations/](/src/integrations/architecture-context.md) |
  | Does it require a new third-party credential or environment value? | [src/config/](/src/config/architecture-context.md) |
  | Should access be restricted to authenticated or specific users? | [src/middlewares/Auth/](/src/middlewares/Auth/architecture-context.md) |
  | Are there failure conditions the caller needs to distinguish? | [src/helpers/error/](/src/helpers/error/architecture-context.md) |
  ```

- Let the linked context file own the technical translation.

  **Example (pass):** "Are there failure conditions the caller needs to distinguish?" → the linked error-handling context file explains the `Err` type, the typed catch handler, and the canonical pattern. The question stays at the requirement level.

#### DO NOT

- Phrase a question around a code artefact: handler, factory, schema, config key, status code, log call, route, module.

  **Example (fail):**
  - "Does it add a new entry point in `app.ts`?"
  - "Does it need a new config key?"
  - "Does it return a new error shape?"
  - "Does it call a new downstream API?"
  
  Each requires the reader to already understand the codebase to answer. "Entry point", "config key", "error shape" — these are effects of the requirement, not the requirement.

- Use vocabulary only insiders know.

  **Example (fail):** "Does it touch a partner integration handler?" — the reader has to know what a handler is and which folder counts. Reframe as "Does it expose a new operation on a downstream system?" and let the context file explain handlers.

- Smuggle implementation hints into the question with parentheticals.

  **Example (fail):** "Is there a new downstream system to integrate with (i.e. needs a new partner folder)?" — strip the parenthetical; the linked file is where folder structure lives.

**Source:** The Where to Start table is the system's onboarding surface; questions framed in code break the on-ramp before anyone reaches it.
