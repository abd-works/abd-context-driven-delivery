# Rule: `templates/tests/` mirrors the test-helpers context file

The folder structure, tier names, file naming pattern, and helper layout inside `templates/tests/` MUST match the test-helpers package-tier `architecture-context.md` exactly. The test-helpers context file (typically at `tests/<helpers>/architecture-context.md`) is the source of truth for testing-architecture decisions in the new project-distributed spec model. The template skill's job is to render those decisions as parameterized scaffold files, not to author a parallel testing architecture. Failing this means `templates/tests/` declares one testing pattern, the rest of the project follows another, and `abd-architecture-code`'s `scaffold-test-layout-before-scenarios.md` rule cannot reconcile the two.

## DO

- Read the test-helpers context file before writing any test scaffold.

  **Example (pass):** Test-helpers context file's folder structure section defines `tests/domain/{epicSlug}/{subEpicSlug}.test.ts`, `tests/server/{epicSlug}/{subEpicSlug}.server.test.ts`, `tests/client/{epicSlug}/{subEpicSlug}.client.test.tsx`, `tests/e2e/{epicSlug}.e2e.test.ts`. `templates/tests/` has exactly those four files at exactly those paths.

- Mirror helper file naming.

  **Example (pass):** Test-helpers context file's spec-alignment table maps "domain tier" to `tests/domain/_helpers/{subEpicSlug}-helpers.ts`. `templates/tests/_helpers/{subEpicSlug}-helpers.ts` exists in the template package with the canonical helper shape (Given/When/Then DSL, fixture factory, stub registry — whatever the helpers context file documents).

- Use the placeholder vocabulary from the helpers context file for slugs.

  **Example (pass):** Helpers context file uses `{epicSlug}` and `{subEpicSlug}`. `templates/tests/` uses both. They are declared in `parameters.json` alongside the code-level placeholders from `template/`.

- Lift the canonical test body shape from the helpers context file verbatim.

  **Example (pass):** Helpers context file documents the domain-tier shape as `describe(<sub-epic>) → it(<scenario>) → arrange (use helpers) → act → assert via DSL`. `templates/tests/domain/{epicSlug}/{subEpicSlug}.test.ts` shows that exact shape with placeholder values; readers know where each part goes.

## DO NOT

- Invent a test tier the helpers context file does not name.

  **Example (fail):** Helpers context file names three tiers: domain, server, client. Template adds a fourth — `tests/integration/...` — because "integration tests are usually needed". The project does not have an integration test runner; `example/`'s integration test cannot be executed. The tier was a fabrication.

- Use a folder structure that contradicts the helpers context file.

  **Example (fail):** Helpers context file maps sub-epic-per-file: `tests/server/<epic>/<sub-epic>.server.test.ts`. Template uses scenario-per-file: `tests/server/<epic>/<sub-epic>-<scenario>.server.test.ts`. `abd-architecture-code` is now forced to pick one — it picks the helpers context file (per its own rules), so the template's structure is silently overridden.

- Author a helper shape that differs from the helpers context file's canonical pattern.

  **Example (fail):** Helpers context file documents a Given/When/Then DSL. Template's helper uses raw `beforeEach`/`afterEach` setup blocks. Two patterns now compete; new contributors copy whichever they see first.

- Skip the helpers context file because the source mechanism's `architecture-context.md` says nothing about tests.

  **Example (fail):** Source spec is a mechanism with no test-architecture content. The skill skips authoring `templates/tests/` rather than reading the test-helpers context file. `templates/tests/` is empty; the code skill has no test scaffold to instantiate. The fix is to read the helpers context file always — it is the source of truth for tests regardless of which mechanism the template is for.

- Use a placeholder for tier names.

  **Example (fail):** Template uses `{tier}.test.ts` because "any tier works". The four tiers in the helpers context file have different shapes, different helpers, and different runners; collapsing them under `{tier}` makes the template too abstract to be useful.

**Source:** Practice-skill authoring convention (abd-architecture-template). The test-helpers context file is the architecture-specification skill's testing-architecture output; this rule keeps the template faithful to it.
