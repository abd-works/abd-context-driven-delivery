### Rule: A package has a minimal named seam and deep functionality behind it

A good package is *deep* in Ousterhout's sense: a small, named public surface in front of substantial functionality. The seam — the set of operations consumers call from outside the folder — is the package's *contract* and the part the package promises to keep stable. Behind the seam is real work: state, lifecycle, integration logic, transformations. This rule is about the *design* of the package's seam, not about what the context file documents. The context file documents the whole package — public surface, internals, lifecycle, dependencies — because internals matter to anyone modifying the package. Passing means the package's public surface is a short named list AND the functionality behind it is substantial. Failing means the public surface is large (every internal function is exported; encapsulation is fictional) OR the package is shallow (its only job is forwarding calls to a third-party SDK with no value added).

#### DO

- Keep the public surface small and named — a handful of operations consumers actually call.

  **Example (pass):** A Zendesk client exposes three public operations — `createTicket`, `closeTicket`, `findByCustomer` — even though the internal implementation spans ten files (signing, retries, payload builders, response parsers, error mapping). Small seam, deep functionality.

- Document internals as participants in the context file so the next engineer can modify the package safely.

  **Example (pass):**
  ```markdown
  ### Participants

  **`/src/services/Zendesk/index.ts`** — public entry; exports the three
  operations consumers call.

  **`/src/services/Zendesk/signRequest.ts`** — internal: HMAC signing of
  outbound requests; secret loaded once at module init.

  **`/src/services/Zendesk/headers.ts`** — internal: builds auth + content
  headers per request.

  **`/src/services/Zendesk/types.ts`** — internal: Zendesk API types,
  isolated from caller-facing types.
  ```
  Public-vs-internal is labelled on each participant; the reader knows what is contract and what is implementation.

- Achieve a high depth-to-surface ratio — substantial work absorbed behind a small contract.

  **Example (pass):** Two public operations on a queue client; behind them sit 400 lines of retry, dead-lettering, observability, and idempotency-key handling. Consumers see a simple contract; the package absorbs the complexity.

#### DO NOT

- Expose every internal function as a public operation.

  **Example (fail):** A package exports 30 named operations, of which 24 are internal helpers consumers never call (`buildHeaders`, `signRequest`, `parseResponse`, etc.). The "seam" is fictional; any caller might depend on any helper and the package can never refactor.

- Ship a shallow package that forwards calls without adding value.

  **Example (fail):**
  ```typescript
  export const createTicket = (input) => zendeskSdk.tickets.create(input);
  export const closeTicket = (id) => zendeskSdk.tickets.close(id);
  ```
  The package is a one-to-one re-export of the SDK; it adds no error mapping, no domain types, no failure translation. Consumers may as well call the SDK directly; the wrapper is overhead, not architecture.

- Conflate "seam is minimal" with "documentation hides internals". The seam is the contract; the documentation is the manual. Internal participants belong in the manual.

  **Example (fail):** A package context file lists only the three public operations and says nothing about how the package is wired internally. The next engineer adding a fourth operation has to reverse-engineer the whole package from source.

- Add a public operation just to make testing easier instead of fixing the test seam.

  **Example (fail):** A package exports an internal helper called `_resetForTesting()` so tests can poke its state. The seam now permanently includes a test-only operation that consumers will eventually call by accident. Reset state through the constructor or a proper test boundary instead.

**Source:** Deep modules (Ousterhout, *A Philosophy of Software Design*) — a package's value is high functionality per unit of interface; the seam is the contract, the context file is the manual.
