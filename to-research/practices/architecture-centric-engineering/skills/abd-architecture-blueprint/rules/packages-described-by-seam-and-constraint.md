### Rule: A package is described by its seam and the constraint it imposes

A package at blueprint fidelity is a **boundary with a rule on its other side**. Its entry must name the seam it owns (the call surface that crosses the boundary) and the constraint that seam imposes on code outside the package — what other packages must do at the seam, and what they must not do anywhere else. Internal organisation is not the point; how the rest of the codebase is shaped by the package's existence is the point. Passing means a reader can tell, from the entry alone, what changes for a developer working in any *other* package because this one exists. Failing means the entry catalogues what the package contains (files, classes, functions) without saying what it forces consumers to do, or describes the package's internals as if the boundary did not exist.

#### DO

- Name the seam as the first sentence. Make the constraint the second sentence.

  **Example (pass):** "`helpers/error` — Owns the error-handling seam. Every entity controller calls `handleError(res, error)` from its catch block; direct `res.status().json(...)` calls in route handlers are prohibited."

- State the constraint in the form of an obligation *or* a prohibition on consumers — preferably both. A seam without a constraint is decoration; the constraint is what gives the package architectural weight.

  **Example (pass):** "`configs` — Owns the configuration seam. All environment access goes through the typed `runtimeEnv` object exported from this folder; no module outside `configs/` reads `process.env` directly."

- Defer internal organisation to the per-folder `architecture-context.md`. The blueprint entry stops at the seam.

#### DO NOT

- Catalogue files, classes, or functions instead of naming the seam.

  **Example (fail):** "`helpers/error` — contains `ErrorTranslator`, `ErrorMapper`, `DomainError`, `HttpError`, `ValidationError`." A list of internals tells the reader what is inside; it never tells them what the package forces them to do.

- Describe the package as a feature area rather than a boundary.

  **Example (fail):** "`auth` — handles authentication." That is a department label, not architecture. What does the seam look like? What must consumers do? What may they not do? Without the constraint there is no boundary, only a folder.

- Treat the seam and the constraint as separable. A seam stated without its consumer-facing rule is just a function name; a rule stated without the seam is a wish.

  **Example (fail):** "`helpers/error` — exposes a `handleError` function." (No constraint stated — anyone could ignore it.)
  **Example (fail):** "All errors must be normalised before responding." (No seam stated — no one knows where to do this.)

**Source:** A package's value at blueprint fidelity is the constraint it imposes — without the constraint, the boundary is fiction.
