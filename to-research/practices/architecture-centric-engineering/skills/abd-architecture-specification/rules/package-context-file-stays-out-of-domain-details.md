### Rule: A package context file documents the package, not the domain

A package context file documents what the package is and how it works — its public surface, its internals, its lifecycle, its consumers, its dependencies, its failure shapes. Documenting internals is part of the job: anyone modifying the package needs to know how the pieces fit together. What the file MUST NOT document are the *domain* rules that the package's consumers must enforce: business invariants, entity state transitions, validation policies for domain data, anything that belongs in `abd-domain-specification`. The split is between "how is this package built and used" (architecture, documented here) and "what business rules must callers obey" (domain, documented elsewhere). Domain rules appearing in a package file mean either the package has absorbed responsibilities it should not own, OR the documentation has accidentally taken on the role of the domain specification. Passing means a reader learns how the package works and how to call it, and goes to the domain spec to learn what business rules apply. Failing means the file inlines business invariants, domain state machines, or domain validation policies.

#### DO

- Document the package fully — public surface, internal participants, lifecycle, dependencies, error shapes, consumer list.

  **Example (pass):** The context file has Overview, Public Surface, Participants (internal files and their roles), Dependencies (`AxiosFactory`, `ConfigService`), Failure translation (how upstream errors map), Consumers (named callers), and a canonical usage pattern.

- Document HOW the package works internally when that matters for change.

  **Example (pass):** "Internally `signRequest()` builds an HMAC over the canonical request form using the secret loaded once at module init from `/src/configs/zendesk.config.ts`. To rotate the secret without redeploy, swap the config and call `reinit()` from the composition root." A future engineer modifying signing has the picture.

- Point at the domain spec for the rules the consumer must enforce.

  **Example (pass):** "The caller is responsible for the voucher-redemption invariant (one voucher can be redeemed at most once); see [/docs/domain/specification/domain-specification.md#voucher-redemption](/docs/domain/specification/domain-specification.md#voucher-redemption)."

- Distinguish *input contracts* (legitimate package concerns) from *business rules* (domain concerns).

  **Example (pass):** "Email parameter must be RFC 5322 compliant — the package validates before sending to SES, which rejects malformed addresses." This is an input contract, not a business rule. Document it.

#### DO NOT

- Inline domain invariants.

  **Example (fail):**
  ```markdown
  ### Business Rules

  - A voucher can be redeemed at most once.
  - Vouchers expire 90 days after issuance.
  - Redemption requires an active customer.
  ```
  These are domain rules; they belong in the domain spec and are enforced by the caller. The package's job is to provide inventory data, not to police redemption.

- Inline a domain state machine.

  **Example (fail):** A package context file for an Axios wrapper contains a diagram of the Voucher lifecycle (`pending → active → redeemed → expired`). The Axios wrapper has no opinion about Voucher state; the diagram has migrated from the domain spec.

- Document validation policy for domain data.

  **Example (fail):** "Customer email must be valid because customers need valid addresses for receipt delivery and to ensure regulatory compliance with CASL." The reasoning is a business rule about customer records; it belongs in the domain spec.

- Hide package internals because "they aren't part of the public surface".

  **Example (fail):** A package context file lists only the three public operations and stops. The next engineer touching the package has to read every file to understand how it works. Documenting internals is the job; staying out of the domain is the boundary.

**Source:** Separation of concerns — the architecture specification documents how units work and interact; the domain specification documents the business rules behind those seams. Domain content in a package file is a smell that one document is colonising the other.
