**Default format:** markdown

**Goal:** Name the BDD subject tree before behavior signatures — delegates module structure to Clean Engineering at the same depth.

### Guidance

Name the BDD subject tree before behavior signatures. Delegate module structure to Clean Engineering at the same depth. Rough subject index for a partition pass: domain things, states, or observable conditions (top-level `describe`s); subject + candidate `that`/`with` + TODOs. Not full `it should` suites.

### Scaffold

**When scaffolding only** (`/partition` or a names-only first cut — not full generate at this fidelity): follow this subsection. Do not use ## behavior / ## development below, ## Sketching, or ## Templates. **Stop reading this skill when scaffolding.**

Rough subject index for a **partition** pass or first cut — domain things, states, or observable conditions (top-level `describe`s); subject + candidate `that`/`with` + TODOs. Not full `it should` suites.

Key rules: `state-not-when` — nest by the state or condition that enables an observation, never by a `when` trigger; `nest-by-enabling-events` — sub-groupings are conditions that unlock further behavior, not implementation steps; `context-setup-expresses-state` — setup under a label must establish that label's state, not unrelated host boot.

**Default format:** Python

**Goal:** map observation to a real test before implementation. Lock the sketched hierarchy as framework `describe` / `it` nesting. Every `it` body is exactly one `BDD: SIGNATURE` marker — nothing else.

### Guidance

- Sketch nesting (subjects → `with`/`that`/events → `it should`) is agreed
- **Confirm framework** — ask if not stated. Default: Mamba/Python; Jest/TypeScript or JUnit 5/Java when the project uses those.
- Convert every sketch hierarchy line to its framework equivalent (see Framework syntax).
- Process in batches of ~18 describe blocks when the hierarchy is large.

Fill the **behavior** (SIGNATURE) section of `templates/bdd-templates.{ext}` (`.py` / `.java` / `.ts`).

### Rules

- **`no-implementation`** — No assertions, mocks, production imports, helpers, or `beforeEach` / shared setup.
- **`framework-syntax`** — Refer to [`practices/language-tools.md`](/practices/language-tools.md) for the target language's syntax. One confirmed framework throughout. Do not mix Jest and Mamba constructs.

**Pass:**
```typescript
it('should apply a percentage discount to eligible items', () => {
  // BDD: SIGNATURE
});
```

**Fail:** any assertion, mock, import of production code, or helper inside the body.

---

### Guidance

**Procedure:** Follow the **Test shape ladder** in `@clean_engineering` `## code` § Procedure — real conditions first, then stub TDD, then e2e swap on request.

**Tooling & Idioms:** Refer to [`practices/language-tools.md`](/practices/language-tools.md) for language-specific tool recommendations and idiomatic patterns for tests.

1. **Confirm framework** — inherit from the behavior file.
2. **Scan markers** — list all `it` blocks still containing `BDD: SIGNATURE`; report count.
3. **Identify shared setup** — extract to `beforeEach` / `with before.each:` or a factory when three or more siblings share arrangement.
4. Pick **one** marker. Fill Arrange-Act-Assert from the DEVELOPMENT TESTS section of `templates/bdd-templates.{ext}` (`.py` / `.java` / `.ts`).
5. Run the test — confirm RED for the right reason.
6. Write the **minimum** production code until GREEN (PRODUCTION CODE section of the same template).
7. Refactor only while green. Move to the next marker.
8. Repeat until zero markers remain, then run **validate**.

### Rules

- **hierarchy-preservation** — 1:1 from sketch nesting to code. Nothing added, removed, or flattened. Same depth, same `it` count. Changing the tree during implementation drops behaviors that were agreed on, or adds ones nobody specified.
- **red-then-green** — Fix code by writing the test first, then watching it fail, then making production code changes.
- **minimum-green-code-minimalism-least-production-code-that-makes-this-assertion-pass-refactor-only-while-green** — **`minimum-green`** / **`code-minimalism`** — Least production code that makes this assertion pass. Refactor only while green.
- **one-signature-at-a-time** — Implement and test one `BDD: SIGNATURE` at a time — get it passing before moving to the next. Do not fill in every test body first and try to make them all pass together.
- **one-assertion-per-test** — One outcome per `it` — two outcomes in one test and a failure does not tell you which behavior broke.
- **layer-isolation** — Mock only at architecture boundaries; never the subject under test. Mocking the subject tests the mock, not your code.
- **context-sharing** — Shared construction in `beforeEach` / factory at three sibling dupes. Repeated setup in every test hides what actually differs between them.
- **context-setup-expresses-state** — Same rule as behavior (above). At development fidelity, `before.each` is Arrange: it must express the parent context's named state, not smuggle host boot under a domain classification branch.
- **oo-api-design** — Ask-don't-tell: construct fully; own state on the object; operations on the closest domain concept. Tests that assemble state through getters or pass setup bags couple to how you built it, not what it does.
- **honors-documented-surface-contracts** — Public API must match documented surface contracts; if a spec fights the contract, fix the spec.
