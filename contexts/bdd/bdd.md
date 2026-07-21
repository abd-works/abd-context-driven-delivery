# Contexts

Behavior-driven development turns domain vocabulary into passing tests. Every BDD artifact is an indented hierarchy. Sketch that shape first (`sketch-template.md`).

## Hierarchy shape (required)

```
describe {subject — domain thing, state, or observable condition}
  that {event or condition that sets the subject up}
    with {narrower condition}
      it should {observable outcome}
```

Read top-down as a **usage / storytelling sequence**: what the user or system does first, then what is true, then what is observed. Nest by the **real events and conditions** that make the next observation possible — not by package, class role, or test fixture type.

| Line | Names | Never names |
| --- | --- | --- |
| **describe** | Subject under observation in plain English (thing, state, condition) | Manager / hub / runner / service / internal class; decorator symbol (`@log`); marker name |
| **that …** | Past or present event/condition on that subject (`that has been logged`, `that is invoked`) | `when …` |
| **with …** | Narrower standing condition (`with no session name given`, `with verbose off`) | `when …`; implementation knobs phrased as API flags |
| **it should …** | One stakeholder-visible outcome | Internals, private fields, call counts on mocks of the subject |

**Pass (storytelling / usage order):**
```
an action that is annotated with log
  that is invoked
    it should record a run event on the session trail
  that has been logged
    with no session name given
      it should use the default session
    with a given session name
      it should keep events under that session
    with verbose off
      it should write a summary line and keep the last payload
      with full logging requested
        it should flush the last payload
    with verbose on
      it should write payload files for later events

an action that is not annotated
  that is invoked
    it should leave the session trail empty
```

**Fail:**
```
@log marker                          ← mechanism / symbol, not a subject
SessionLogHub                        ← manager / internal
a logged tool                        ← splits the same subject; use one action story
when no session name is given        ← never "when" for state — use "with …"
```

**Shared Rules:**

- **`observable-behavior`** — Prove what a stakeholder can verify without reading code (return value, state, public effect). Never internals.
- **`domain-practice-alignment`** — Describe names must match domain language / model exactly.
- **`usage-order-behaviors`** — Order describes, contexts, and examples as a **usage story** or operational sequence (what happens first → next). Do not order by implementation layer, package, or internal type.
- **`describe-is-subject-not-internal`** — A `describe` is a domain subject, state, or observable condition — never a manager, hub, runner, service, or other internal (`SessionLogHub`, `ToolsetRunner`, …).
- **`describe-is-plain-english`** — Full English phrases (e.g. "an action that is annotated with log", "an action that is not annotated"). Never symbol/mechanism names (`"@log marker"`) as the subject.
- **`state-not-when`** — Never name a nested state with `when`. Use `that …` for events/conditions on the subject and `with …` for standing conditions. Ask: what event or condition must already be true for this observation?
- **`nest-by-enabling-events`** — Each nested `that` / `with` must be a real precondition or event required for the nested `it should` — not a test-file grouping convenience.

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
| Top-level concept | `describe('Context', () => {` | `with description('Context'):` | `@Nested class Context` |
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
- **`impl-must-carry-bdd-manifest`** — Impl paired with `*_spec.py` carries `# @toolset-manifest … contexts.bdd.bdd:Bdd`.
- **`observable-behavior`** — Assert public outcomes only.

---

# Generate

1. Confirm fidelity (`behavior` → `development`) and format (defaults: both → python).
2. Read § Contexts — shared rules and the active fidelity (including its Rules).
3. Grill and sketch when useful (`@grill_with_context`, `sketch-template.md`): follow **Hierarchy shape** — usage-order subjects → `that`/`with` enabling events → `it should` → public call surface → novel internals only at development. Declare fidelity once at the top of the sketch; **do not** annotate lines with `# b` / `# d`. No manager/hub/`when`/mechanism describes.
4. Fill `formats/{format}/bdd-template.*` for the active fidelity.
5. Run **validate**.
