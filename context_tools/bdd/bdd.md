# Contexts

Behavior-driven development describes an application's behavior from the perspective of its stakeholders — as concrete examples in domain language. Sketch that usage story first (`templates/bdd-sketch.md`); automate it only once the examples read cleanly.

## Hierarchy shape (required)

```
describe {subject — domain thing, state, or observable condition}
  that {event or condition that sets the subject up}
    with {narrower condition}
      it should {observable outcome}
```

**Same behavior, different implementations** — extend the hierarchy with explicit routes:

```
describe {story name}
  shared_context {abstract subject — exact string for included_context}
    it should {shared outcome}
    it should {second shared outcome}
  with {Implementation}
    -> included_context('{abstract subject — same string}')
    it should {outcome only for this implementation}
  with {second Implementation}
    -> included_context('{abstract subject — same string}')
    it should {outcome only for second implementation}
```

Read top-down as a **usage / storytelling sequence**: what the user or system does first, then what is true, then what is observed. Nest by the **real events and conditions** that make the next observation possible — not by package, class role, or test fixture type.

| Line | Names | Never names |
| --- | --- | --- |
| **describe** | Subject under observation in plain English (thing, state, condition) | Manager / hub / runner / service / internal class; decorator symbol (`@log`); marker name |
| **that …** | Past or present event/condition on that subject (`that has been logged`, `that is invoked`) | `when …` |
| **with …** | Narrower standing condition (`with no session name given`, `with verbose off`) | `when …`; implementation knobs phrased as API flags |
| **shared_context …** | Shared `it should` outcomes written **once**; string reused by `included_context` | Copying the same `it should` under every implementation branch |
| **-> included_context('…')** | Route to the matching `shared_context` on this implementation branch | Omitting the route and assuming the spec will wire it |
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
ToolsetRunner                        ← manager / internal
a logged tool                        ← splits the same subject; use one action story
when no session name is given        ← never "when" for state — use "with …"
```

**Shared Rules:**

- **`observable-behavior`** — Prove what a stakeholder can verify without reading code (return value, state, public effect). Never internals.
- **`domain-practice-alignment`** — Describe names must match domain language / model exactly.
- **`usage-order-behaviors`** — Order describes, contexts, and examples as a **usage story** or operational sequence (what happens first → next). Do not order by implementation layer, package, or internal type.
- **`describe-is-subject-not-internal`** — A `describe` is a domain subject, state, or observable condition — never a manager, hub, runner, service, or other internal (`SessionLog`, `ToolsetRunner`, …).
- **`describe-is-plain-english`** — Full English phrases (e.g. "an action that is annotated with log", "an action that is not annotated"). Never symbol/mechanism names (`"@log marker"`) as the subject.
- **`state-not-when`** — Never name a nested state with `when`. Use `that …` for events/conditions on the subject and `with …` for standing conditions. Ask: what event or condition must already be true for this observation?
- **`nest-by-enabling-events`** — Each nested `that` / `with` must be a real precondition or event required for the nested `it should` — not a test-file grouping convenience.
- **`abstract-subject-then-concrete-backends`** — When the same behavior must hold for several implementations, write the shared `it should` outcomes **once** on the abstract subject (the domain thing before you name the implementation). Each concrete `with …` branch (a subtype, format, or adapter) **includes** that contract — it does not restate it. Add new `it should` lines under a concrete branch only for proofs that differ because of that implementation. See [Same behavior, different implementations](#same-behavior-different-implementations) below.
- **`full-surface-coverage`** — When generating or satisfying tests for a module that already exists, scan the production source for every public method, property, class, and constant. Each must have at least one `it should` covering its observable behavior. Any gap is a violation. Private and underscore-prefixed members are excluded unless they are part of a documented public contract.
- **`scan-fixture-pair`** — A mechanical mistake spec passes the fail file to `expect_scan_fails` and the pass file to `expect_scan_passes` (`context_tools.bdd.spec_helpers`). Do not invent a parallel eval spec harness.


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

Fill the **behavior** (SIGNATURE) section of `templates/bdd-templates.{ext}` (`.py` / `.java` / `.ts`).

### Framework syntax

| Construct | Jest (TypeScript) | Mamba (Python) | JUnit 5 (Java) |
| --- | --- | --- | --- |
| Top-level concept | `describe('Context', () => {` | `with description('Context'):` | `@Nested class Context` |
| Nested state/context | `describe('that has…', () => {` | `with context('that has…'):` | `@Nested class ThatHas…` |
| Shared contract (once) | shared `describe` / `it` group (project convention) | `with shared_context('…'):` | `@Nested` shared fixture class |
| Include shared contract | nested `describe` including shared group | `with included_context('…'): pass` | extend / compose shared fixture |
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

**Pass (shared behavior across implementations):**
```python
with shared_context('with an agent runtime that has accepted a request'):
    with it('should show the runtime as done'):
        # BDD: SIGNATURE
    with it('should yield the reply'):
        # BDD: SIGNATURE

with description('Finish request on agent runtime'):
    with context('with a SubAgent'):
        with included_context('with an agent runtime that has accepted a request'):
            pass
        with it('should leave the reply on doer.out'):
            # BDD: SIGNATURE
```

---
## Same behavior, different implementations

Write shared `it should` once on the abstract subject (`shared_context`). Each `with {Implementation}` branch names domain state and routes with `-> included_context('…')` — **same string**, no copy-paste. Extra `it should` lines belong only on the branch they differ by.

```
shared_context with an agent runtime that has accepted a request
  it should show the runtime as done
  it should yield the reply
with a SubAgent
  -> included_context('with an agent runtime that has accepted a request')
  it should leave the reply on the role out file
with a CliAgent
  -> included_context('with an agent runtime that has accepted a request')
  it should detect completion when the transcript stops growing
```

**Fail:** the shared pair repeated under every `with …` branch. Fixture: `examples/evals/backends-restate-shared-behavior/`.

## development

**Default format:** Python

**Goal:** Replace `BDD: SIGNATURE` markers one at a time with it shgould /expect bodies, then minimum production code until green. Inherit the framework from the **behavior** artifactif already completed.

1. **Confirm framework** — inherit from the behavior file.
2. **Scan markers** — list all `it` blocks still containing `BDD: SIGNATURE`; report count.
3. **Identify shared setup** — extract to `beforeEach` / `with before.each:` or a factory when three or more siblings share arrangement.
4. Pick **one** marker. Replace it with a minimal body from the DEVELOPMENT TESTS section of `templates/bdd-templates.{ext}` (`.py` / `.java` / `.ts`).
5. Run the test — confirm RED for the right reason.
6. Write the **minimum** production code until GREEN (PRODUCTION CODE section of the same template).
7. Refactor only while green. Move to the next marker.
8. Repeat until zero markers remain, then run **validate**.

### Coverage scan (existing code)

When generating or satisfying against a module that already exists, read the production source before touching the spec:

1. List every public method, property, class, and constant (exclude `_`-prefixed members unless publicly documented).
2. Compare against the existing spec to find members with no `it should` entry.
3. Add `it should` entries (at behavior fidelity) or full test bodies (at development fidelity) for every gap — do not skip any public member.
4. Only then proceed with RED-GREEN-REFACTOR for the new or updated tests.

### The RED-GREEN-REFACTOR cycle

**RED** — fail for the right reason before production code exists.  
**GREEN** — least production code that makes this assertion pass.  
**REFACTOR** — clean up while green. One test, one production change, one green — do not batch all bodies first.

### One outcome per `it`

One observable outcome per `it` (`observable-behavior` above). Split unrelated `expect` calls into separate examples. Shared construction → `beforeEach` / factory only when three or more sibling examples need the same setup — no Arrange / Act / Assert labels.

### Rules

- **`red-then-green`** — Fail for the right reason before production code changes.
- **`minimum-green`** / **`code-minimalism`** — Least production code that makes this assertion pass.
- **`refactor-only-when-green`** — Refactor only while green.
- **`one-signature-at-a-time`** — One marker → green → next. Do not batch all bodies first.
- **`one-assertion-per-test`** —  one outcome per `it`. tighly connects `expects`
- **`layer-isolation`** — Mock only at architecture boundaries; never the subject under test.
- **`no-remaining-signatures`** — Zero `BDD: SIGNATURE` markers when done.
- **`full-surface-coverage`** — Before generating or satisfying, scan the production source for all public members. Add `it should` entries for every uncovered public method, property, or class. Complete coverage is required; no public surface may be left untested.
- **`context-sharing`** — Shared construction in `beforeEach` / factory at three sibling dupes.
- **`shared-behavior-across-implementations`** — When a behavior file has an abstract subject and several concrete `with …` implementations, extract the shared `it should` bodies once (`shared_context` + `included_context` in Mamba). Each concrete branch names domain state in `with context('with …')` and includes the shared group. Do not duplicate the same assertions under every branch.
- **`oo-api-design`** — Ask-don't-tell: construct fully; own state on the object; operations on the closest domain concept.
- **`honors-documented-surface-contracts`** — Public API must match documented surface contracts; if a spec fights the contract, fix the spec.
- **`roundtrip-parity-is-required`** — Adapter parse/render seams assert `counts(parse(render(canonical))) == counts(canonical)`.
- **`code-source-of-truth-guard`** — Tests reject unsafe regeneration when generation can overwrite hand-edited code.
- **`impl-must-carry-bdd-manifest`** — Impl paired with `*_spec.py` carries `# @toolset-manifest … context_tools.bdd.bdd:Bdd`.
- **`observable-behavior`** — Assert public outcomes only.
- **`scan-fixture-pair`** — A mechanical mistake spec passes the fail file to `expect_scan_fails` and the pass file to `expect_scan_passes` (`context_tools.bdd.spec_helpers`). Do not invent a parallel eval spec harness.

---



# Scaffold

A scaffold produces thin subject index — domain things, states, or observable conditions (top-level `describe`s); subject + candidate `that`/`with` + TODOs. Not full `it should` suites.

Key rules: `state-not-when` — nest by the state or condition that enables an observation, never by a `when` trigger; `nest-by-enabling-events` — sub-groupings are conditions that unlock further behavior, not implementation steps.