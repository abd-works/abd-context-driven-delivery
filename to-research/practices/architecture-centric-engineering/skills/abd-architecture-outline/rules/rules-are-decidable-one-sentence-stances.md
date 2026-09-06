### Rule: Rules are decidable one-sentence stances

Every entry in the Rules section is **one sentence** and **decidable against a real code change or design proposal**. It names a constraint the system imposes on itself — not an aspiration or a value statement. A reviewer should be able to look at a pull request and say "this violates rule 3" or "this is fine under rule 3." Passing means every rule names what it constrains (a layer, a folder, a code path, a naming convention) and can be applied with a clear yes-or-no answer. Failing means a rule is a paragraph, a slogan, a preference, or so abstract that no piece of code could ever be measured against it.

#### DO

- Write each rule as one declarative sentence naming the constraint and the thing it constrains.

  **Example (pass):** "All downstream API calls cross a named entity controller — no route handler calls an external SDK directly; the controller class is the only permitted seam."

- Name a verifiable surface: a layer, a folder, a code path, a file-naming convention, or a build-time check.

  **Example (pass):** "Config is read once at startup — no `process.env` access outside the environment module; every other module receives configuration through injection." Verifiable by grepping `process.env` across non-environment files.

- Write 5–8 rules. If a candidate rule cannot be applied to a concrete pull request, defer it to the blueprint where the code shape exists to test it against.

  **Example (pass):** Eight rules, each one sentence. A ninth candidate ("prefer immutability where cost is low") cannot be decided without seeing the actual data structures — deferred to blueprint.

#### DO NOT

- Express a rule as a value statement or aspiration that cannot be applied to a code change.

  **Example (fail):** "We value clean, maintainable code." Undecidable — a reviewer cannot pass or fail a PR against this.

- Write a rule as a multi-sentence or multi-paragraph entry.

  **Example (fail):** A rule entry is three paragraphs explaining context, options considered, and consequences. That is an ADR, not a rule.

- Embed implementation detail inside a rule — implementation lives in per-folder `architecture-context.md` files at specification fidelity.

  **Example (fail):** "Use `handleError(res, error)` from `lib/errors/handleError.ts` and never call `res.status().json()` directly in a controller — configure the error translator at `src/lib/errors/index.ts`." The verifiable constraint is the first clause; the rest is specification-level detail.

**Source:** Practice-skill authoring convention (abd-architecture-outline); rules are the outline's constraint layer — they must survive as yes/no tests against future code changes, not as retrospective documentation.
