# Concepts

Behavior-driven development turns domain vocabulary into passing tests. Every BDD artifact is an indented hierarchy: **describe** names the subject (a domain concept); nested **with** / **that** (or 
present-tense events) narrow state; **it should** leaves observe what 
is true of that state; at development, **expect** asserts those 
observations on the public surface. Sketch that shape first 
(`sketch-template.md`).


**Shared Rules:** 
**`observable-behavior`** — prove what a stakeholder can verify without reading code (return value, state, public effect). Never internals.
**`domain-practice-alignment`** — describe names must match domain language / model exactly.

---

This skill operates at **multiple levels of fidelity**. Start from an agreed sketch and deepen toward green tests and production code. Each level **adds** artifacts and **extends** the previous — do not fill in details from a more detailed fidelity. Least detail → most detail below.

| Fidelity | Output |
|---|---|
| **behavior** | describe/it hierarchy with `BDD: SIGNATURE` markers in each `it` |
| **development** | Implemented tests + production code |

## behavior

**Default format:** Python

**Goal:** map observation to a real test before implementation. Lock the sketched hierarchy as framework `describe` / `it` nesting. Every `it` body is exactly one `BDD: SIGNATURE` marker — nothing else.

- Sketch nesting (subjects → `with`/`that`/events → `it should`) is agreed 
- **Confirm framework** — ask if not stated. Default: Mamba/Python; Jest/TypeScript or JUnit 5/Java when the project uses those.
- Convert every sketch hierarchy line to its framework equivalent (see Framework syntax).
- Process in batches of ~18 describe blocks when the hierarchy is large.

Fill the **behavior** (SIGNATURE) section of `formats/{format}/bdd-template.*`.

### Framework syntax

| Construct | Jest (TypeScript) | Mamba (Python) | JUnit 5 (Java) |
| --- | --- | --- | --- |
| Top-level concept | `describe('Concept', () => {` | `with description('Concept'):` | `@Nested class Concept` |
| Nested state/context | `describe('that has…', () => {` | `with context('that has…'):` | `@Nested class ThatHas…` |
| Behavior | `it('should …', () => {` | `with it('should …'):` | `@Test void should…()` |
| Marker | `// BDD: SIGNATURE` | `# BDD: SIGNATURE` | `// BDD: SIGNATURE` |

### Rules

- **`hierarchy-preservation`** — 1:1 from sketch nesting to code. Nothing added, removed, or flattened. Same depth, same `it` count.
- **`signature-markers`** — Every `it` body is exactly `// BDD: SIGNATURE` or `# BDD: SIGNATURE`.
- **`no-implementation`** — No assertions, mocks, production imports, helpers, or `beforeEach` / shared setup.
- **`framework-syntax`** — One confirmed framework throughout. Do not mix Jest and Mamba constructs.

**Pass:**
```typescript
it('should apply a percentage discount to eligible items', () => {
  // BDD: SIGNATURE
});
```

**Fail:** any assertion, mock, import of production code, or helper inside the body.

---

## development

**Default format:** Python

**Goal:** Replace `BDD: SIGNATURE` markers one at a time with it shgould /expect bodies, then minimum production code until green. Inherit the framework from the **behavior** artifactif already completed.

1. **Confirm framework** — inherit from the behavior file.
2. **Scan markers** — list all `it` blocks still containing `BDD: SIGNATURE`; report count.
3. **Identify shared setup** — extract to `beforeEach` / `with before.each:` or a factory when three or more siblings share arrangement.
4. Pick **one** marker. Fill Arrange-Act-Assert from the DEVELOPMENT TESTS section of `formats/{format}/bdd-template.*`.
5. Run the test — confirm RED for the right reason.
6. Write the **minimum** production code until GREEN (PRODUCTION CODE section of the same template).
7. Refactor only while green. Move to the next marker.
8. Repeat until zero markers remain, then run **validate**.

### Diagnose

If a test fails after **2 consecutive fix attempts** — stop. Read `diagnose.md` immediately. Do not attempt a third fix without a hypothesis.

### The RED-GREEN-REFACTOR cycle

**RED** — fail for the right reason before production code exists.  
**GREEN** — least production code that makes this assertion pass.  
**REFACTOR** — clean up while green. One test, one production change, one green — do not batch all bodies first.

### Arrange-Act-Assert

Label Arrange / Act / Assert; one observable outcome per `it` (`observable-behavior` above). Split unrelated expects. Shared construction → `beforeEach` / factory at three sibling dupes.

### Rules

- **`red-then-green`** — Fail for the right reason before production code changes.
- **`minimum-green`** / **`code-minimalism`** — Least production code that makes this assertion pass.
- **`refactor-only-when-green`** — Refactor only while green.
- **`one-signature-at-a-time`** — One marker → green → next. Do not batch all bodies first.
- **`one-assertion-per-test`** —  one outcome per `it`. tighly connects `expects`
- **`layer-isolation`** — Mock only at architecture boundaries; never the subject under test.
- **`no-remaining-signatures`** — Zero `BDD: SIGNATURE` markers when done.
- **`context-sharing`** — Shared construction in `beforeEach` / factory at three sibling dupes.
- **`oo-api-design`** — Ask-don't-tell: construct fully; own state on the object; operations on the closest domain concept.
- **`honors-documented-surface-contracts`** — Public API must match documented surface contracts; if a spec fights the contract, fix the spec.
- **`roundtrip-parity-is-required`** — Adapter parse/render seams assert `counts(parse(render(canonical))) == counts(canonical)`.
- **`code-source-of-truth-guard`** — Tests reject unsafe regeneration when generation can overwrite hand-edited code.
- **`impl-must-carry-bdd-manifest`** — Impl paired with `*_spec.py` carries `# @toolset-manifest … bdd.bdd:Bdd`.
- **`observable-behavior`** — Assert public outcomes only.

---

# Generate

1. Confirm fidelity (`behavior` → `development`) and format (defaults: both → python).
2. Read § Concepts — shared rules and the active fidelity (including its Rules).
3. Grill and sketch when useful (`@grill_with_context`, `sketch-template.md`): order subjects → states/events → `it should` → `b` call surface → `d` only at development.
4. Fill `formats/{format}/bdd-template.*` for the active fidelity.
5. Run **validate**.
