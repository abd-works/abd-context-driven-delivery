### Rule: A mechanism names a pattern with multiple instances

A mechanism is **a recurring code shape that multiple components instantiate**. Naming "Authentication" as a mechanism means committing that there is one pattern — one principle, one named template, one technology — that every authenticated route will follow. If you cannot name the pattern and at least two concrete things in the system that will (or do) follow it, you have not identified a mechanism. You have named a topic. The outline catalogue is the place where the team agrees on what patterns the system commits to; passing means each entry is something blueprint and specification will later flesh out into a five-part section (Principles & Patterns, File Structure, Participants, Flow, Walkthrough). Failing means an entry is a topic without a pattern, a technology pick with no shape, or a one-off concern misclassified as a mechanism.

#### DO

- For each mechanism, state the **principle** (the one-line constraint that, if violated, means the code is no longer in this mechanism), the **pattern** (the named shape every instance will take), and the **technology** that realises it.

  **Example (pass):** *Authentication.* **Principle:** every protected route validates a JWT before any handler runs. **Pattern:** an `Auth` middleware mounted ahead of the route group; the middleware delegates to `CognitoService.verify()` and attaches the decoded claims to `req.user`. **Technology:** AWS Cognito for issuance; `jsonwebtoken` for verification.

- Name at least two concrete instances — things in this system that will (or do) follow the pattern. The instances do not have to exist yet; they have to be nameable.

  **Example (pass):** "Instances: every route under `/api/subscriber/*`, every route under `/api/cart/*`, and every internal route under `/internal/*`." Three named instances make it real; later fidelity levels will detail each one.

- When a mechanism currently has only one instance but the team expects more, say so explicitly and name the expected next instances.

  **Example (pass):** "Currently only the Mavenir entity instantiates the System Entity Controller pattern; Zoho, Persona, Fygaro, and Voucher will follow at blueprint stage."

#### DO NOT

- Name a mechanism for which you cannot describe the pattern multiple components will share.

  **Example (fail):** *Caching* as a mechanism heading with prose that says "we may add caching for some endpoints if performance becomes an issue." There is no principle, no pattern, no instance — it is a deferred discussion mislabelled as a mechanism.

- Treat a single one-off integration as a mechanism. One-offs belong in the package description or in the entity that owns them.

  **Example (fail):** *Payment Webhook Handler* as a mechanism — but there is exactly one webhook endpoint, with one shape, that no other code will follow. It is a feature of the Payment package, not a mechanism.

- List a technology pick without the principle and pattern that surround it.

  **Example (fail):** *Logging.* **Technology:** Winston. That tells a reader what library is on disk but not the shape every log call must take, not what makes a log statement "in" or "out" of the mechanism, and not which code will follow the pattern.

**Source:** Practice-skill authoring convention (abd-architecture-outline); mirrors the specification skill's five-part shape — at outline fidelity the principle, pattern, technology, and instances are the minimum that lets blueprint and specification flesh the mechanism into a complete section.
