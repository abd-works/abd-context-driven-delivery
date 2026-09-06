### Rule: A mechanism's pattern is coherent across instances

A mechanism is a templated pattern other features extend. Its coherence lives at the *pattern* level, not the responsibility level: a framework-style mechanism can legitimately handle several related concerns (a request lifecycle that validates, routes, and translates errors; an identity setup that authenticates, authorises, and refreshes tokens) as long as every instance follows the same canonical shape. What makes a mechanism real is that the canonical pattern *predicts* a new instance — same file skeleton, same extension points, same wiring contract. Passing means existing instances visibly share the canonical shape, and a new engineer could produce another instance that looks like the rest by following the recipe alone. Failing means instances diverge so much that the "canonical pattern" is fictional, OR two genuinely separate patterns have been stapled together under one folder name.

**When to split a mechanism in two:**

- Instance groups follow visibly different skeletons (different files, different wiring, different extension steps).
- The Rules section contains rules that apply to some instances but not others; rules that branch on instance type indicate two patterns.

**When NOT to split:**

- A mechanism handles multiple concerns (logging + correlation + metrics) but every instance does all of them the same way — that is one mechanism with a multi-concern recipe, not multiple mechanisms. Responsibility count is irrelevant; shape consistency is what matters.

#### DO

- Make the canonical pattern actually canonical: existing instances visibly follow the same shape.

  **Example (pass):** Partner Integrations — every partner folder has `handler.ts`, `mapper.ts`, `types.ts`; every handler registers in `/src/composition.ts`; every test mirrors `/tests/integrations/{Partner}.spec.ts`. Ten existing instances confirm the pattern; the eleventh is predictable.

- Allow multiple responsibilities in one mechanism if instances treat them uniformly.

  **Example (pass):** Request Lifecycle validates input, routes to a handler, and translates errors. Every route uses the same lifecycle wrapper. Three responsibilities, one consistent pattern, one wiring point — one mechanism.

- Make divergence visible in an "Across the Codebase" table when minor variation exists, so the canonical pattern stays canonical and the exceptions are labelled exceptions.

  **Example (pass):** The Across-the-Codebase table shows nine partners follow the standard recipe and one partner (Mavenir) has an extra `events.ts` file because it emits events the others don't. The standard pattern is intact; the deviation is documented as a deviation.

#### DO NOT

- Document a "mechanism" whose instances diverge significantly.

  **Example (fail):** `src/services/` is called a mechanism. Logger has a singleton entry point; Axios is a factory class; Cognito is a stateful client; Twilio is a thin SDK wrapper. Four different shapes, no shared extension recipe, no common wiring. These are four packages, not one mechanism.

- Bundle two genuinely separate patterns into one mechanism.

  **Example (fail):** A "Storage" mechanism containing both `db/` (a repository pattern with a canonical CRUD shape) and `cache/` (a key-value adapter pattern with a different shape). Two patterns, two extension recipes — split into two mechanism folders or reclassify one as a package.

- Write a Rules section that contradicts itself across instances.

  **Example (fail):** Rules say "every handler registers in `composition.ts`" but half the instances are auto-discovered from the filesystem. The rule isn't a rule; the pattern isn't consistent; the mechanism is two patterns wearing one name.

- Treat "common responsibility" as the test for mechanism-ness when shape is what matters.

  **Example (fail):** Four folders are documented under one mechanism called "Things that talk to external systems" because they share a responsibility. But the four follow four different shapes with four different wiring points. Shared responsibility, no shared pattern — these are four packages.

**Source:** A mechanism's value is in being a template — if existing instances don't share a shape, there is no template, only a collection.
