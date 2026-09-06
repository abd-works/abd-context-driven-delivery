### Rule: A per-folder context file conveys what its boundary is for

At blueprint fidelity, a per-folder `architecture-context.md` earns its place by making the **architectural role of its folder** visible to a reader who has never seen the codebase — the seam it owns, the mechanism it participates in, the constraint it imposes on whatever calls into it, the test tier it lives in, and what it depends on. The shape is fixed; the content is local. Passing means a developer who opens any per-folder file can answer the question "if I'm working in a sibling package and I need something from this one, what am I obliged to do and what may I not assume?" Failing means the file is a list of section headings with no prose beneath, or repeats the master document's one-liner without adding boundary content, or describes what the folder *contains* instead of what it imposes.

A per-folder file at blueprint fidelity is not a stub. Stubs are the absence of thinking; this file is the thinking. If the folder's role cannot be expressed at this depth at blueprint time, the package should not yet appear in `src/architecture-context.md` — the architectural decision is not ready.

#### DO

- Name the seam and the constraint first, in the same form the blueprint's Packages section uses. The per-folder file is the *expansion* of the blueprint entry, not a different artefact.

  **Example (pass):** A `helpers/error/architecture-context.md` whose first paragraph says: "Owns the error-handling seam. Exports `handleError(res, error)` and the `Err` discriminated union. Every entity controller must call `handleError` from its catch block; direct `res.status().json(...)` is prohibited outside this folder."

- Make the consumer list real. Who imports from this folder today? Who *will* import from it once the blueprint's constraint is enforced? A consumer list that includes "everything" or "all controllers" is unhelpful; a consumer list that names the packages and the call site adds architectural weight.

- Name the test tier and the stub status. Is this folder mocked at the unit-test seam? Is it real in the sandbox tier? The answer must come from the Testing Architecture section in `src/architecture-context.md`, not be invented locally.

#### DO NOT

- Leave section headings with no prose.

  **Example (fail):**
  ```
  ## Seam
  ## Mechanism
  ## Technology
  ## Consumers
  ## Test Tier
  ```
  Empty sections are a TODO list, not a context file. A reader cannot tell whether the architecture was thought through or skipped.

- Repeat the master document's one-liner without adding boundary detail.

  **Example (fail):** A per-folder file whose only content is "Owns the error-handling seam." The blueprint's Packages section already says this; the per-folder file's job is to expand it — exports, consumers, prohibition, test tier, dependencies.

- Describe the folder's internals as if it had no boundary.

  **Example (fail):** "This folder contains `error-translator.ts`, `error-mapper.ts`, and `domain-error.ts`." The internals belong at specification fidelity; the boundary belongs here.

- Invent content that contradicts `src/architecture-context.md`. If the per-folder file says the folder is mocked at the sandbox tier but the master says it is real, the master document wins and the discrepancy is a violation to surface, not a per-folder decision to make.

**Source:** A per-folder file at blueprint fidelity is the boundary's first description in its own folder — without that, the boundary lives only in the master document and nobody who opens the folder sees it.
