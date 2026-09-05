### Rule: A mechanism describes a code shape, not a feature

At blueprint fidelity the job of a mechanism entry is to make the **code shape that every participating package must adopt** visible to a developer who has never seen the codebase. Not what the system *does* with the mechanism — what the *code* looks like when the mechanism is applied. Passing means a developer could read the entry, open any package that participates, and recognise the shape immediately: same seam, same call site, same constraint on what surrounding code may and may not do. Failing means the entry describes a capability ("the system validates input"), a technology choice on its own ("uses Joi"), or a feature ("we log every request") without saying what that *imposes on the code that touches the mechanism*.

A code shape names three things together: the **seam** (the exact call surface the mechanism exposes), the **obligation** on consumers (what they must do at that seam), and the **prohibition** on consumers (what they must not do anywhere else). Technology is mentioned inline because it disambiguates the seam — not because it is the point.

#### DO

- Describe the seam, the obligation, and the prohibition in 1–2 paragraphs.

  **Example (pass):** "Error Handling — all downstream errors flow through `handleError(res, error)`, which maps them to the `Err` discriminated union and writes a normalised HTTP response. Every entity controller must call `handleError` from its catch block. Direct `res.status().json(...)` calls in route handlers are prohibited; the two named exceptions are recorded in ADR-006 and ADR-007."

- Make the prohibition explicit — say what the consumer must *not* do, not just what it must do. The prohibition is what makes the shape enforceable in review.

  **Example (pass):** "Configuration — no module outside `configs/` reads `process.env` directly; all environment access goes through `runtimeEnv`." The prohibition is what stops the shape from quietly eroding.

- Use technology as a disambiguator for the seam, not as the description itself.

  **Example (pass):** "Validation — Joi schemas validate every inbound request before the controller runs." Joi is named because it tells you what kind of schema; the description still names the seam and the obligation.

#### DO NOT

- Describe the mechanism as a capability the system has.

  **Example (fail):** "Logging — the system emits structured logs to CloudWatch." That tells you *what happens*, not what every package must do. A reader cannot tell from this whether they need to inject a logger, call a global, or annotate a method.

- Lead with technology and stop.

  **Example (fail):** "Authentication — JWT with Cognito." A technology choice is not a code shape. What does a route handler have to do? What can it not do? Without that, the entry is a label.

- Describe the mechanism's *effect* in production without describing the *code* that produces the effect.

  **Example (fail):** "Authentication — every protected endpoint requires a valid token." True, but vacuous as architecture. What does the code look like? Is there a middleware? A decorator? An explicit guard call in each handler? The shape is missing.

**Source:** Mechanisms at blueprint fidelity are templates for code — if the description does not let a developer see the template, it is not a mechanism description.
