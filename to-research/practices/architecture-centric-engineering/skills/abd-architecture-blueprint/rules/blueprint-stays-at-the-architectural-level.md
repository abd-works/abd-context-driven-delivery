### Rule: The blueprint stays at the architectural level

Blueprint fidelity is the level where every entry answers the question **"what shape does this impose on the code?"** — never the question "what does this code look like, line by line?" The blueprint earns its existence by being above the source and below the outline: it adds the constraint each mechanism and package imposes, but it stops short of the canonical pattern, the file structure, the test fixture, the class diagram with twenty types. Passing means a reader who has read the outline can read the blueprint and learn something new about the *constraints* the system places on its own code, without being drawn into implementation. Failing means a mechanism section runs to multiple pages with code; or a package entry lists files; or a sequence diagram with six lanes appears; or the blueprint duplicates a per-folder file's content because the author could not resist showing the detail.

The same content has a home — it goes into the per-folder `architecture-context.md` at specification fidelity. The blueprint does not lose the information; it stops carrying it.

#### DO

- Describe each mechanism's code shape in 1–2 prose paragraphs. The shape is named through seam, obligation, and prohibition; the implementation that satisfies the shape is not described.

  **Example (pass):** Error Handling is described in two paragraphs naming `handleError`, the `Err` discriminated union, and the prohibition on direct `res.status().json(...)` calls. The actual implementation of `handleError` does not appear; the reader who wants it follows the link to `helpers/error/architecture-context.md`.

- When a one-line contract signature genuinely sharpens the description, include it. One line, not five.

  **Example (pass):** "Every entity controller calls `handleError(res, error)` from its catch block." The signature is the seam; the body is not the blueprint's job.

- Forward the reader to the per-folder file when a question naturally pulls towards detail. The forward-link is the blueprint's way of staying at its level without losing the trail.

#### DO NOT

- Inline a method body, class definition, or any implementation longer than a single signature line.

  **Example (fail):** A mechanism section followed by 30 lines of TypeScript showing the implementation of the seam. The implementation belongs in the per-folder file; the blueprint's value disappears when it duplicates it.

- Ship a sequence diagram with more than three participants in `src/architecture-context.md`.

  **Example (fail):** A six-lane sequence diagram of the full JWT verification flow. Three participants is the threshold; beyond that the diagram is a walkthrough, and walkthroughs are specification work.

- Catalogue files, classes, or methods under a package entry.

  **Example (fail):** A package entry that lists `OrderService`, `OrderRepository`, `OrderEventPublisher`, `OrderValidator`, `OrderMapper`. The list tells the reader what is inside; the blueprint's job is to tell them what the boundary forces them to do.

**Source:** The blueprint exists between the outline and the specification; what makes it valuable is the constraint, not the content of the implementation.
