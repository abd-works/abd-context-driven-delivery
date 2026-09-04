# bdd-development

Use bdd guidance at `development` fidelity only.

Use higher-level fidelity guidance only when required information is missing. Reference these commands with `@`; do not inline their content:
@bdd-behavior
@bdd-modules

# Contexts

## development

**Default format:** Python

**Goal:** Replace `BDD: SIGNATURE` markers one at a time with it shgould /expect bodies, then minimum production code until green. Inherit the framework from the **behavior** artifactif already completed.

1. **Confirm framework** — inherit from the behavior file.
2. **Scan markers** — list all `it` blocks still containing `BDD: SIGNATURE`; report count.
3. **Identify shared setup** — extract to `beforeEach` / `with before.each:` or a factory when three or more siblings share arrangement.
4. Pick **one** marker. Fill Arrange-Act-Assert from the DEVELOPMENT TESTS section of `templates/bdd-templates.{ext}` (`.py` / `.java` / `.ts`).
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
- **`full-surface-coverage`** — Before generating or satisfying, scan the production source for all public members. Add `it should` entries for every uncovered public method, property, or class. Complete coverage is required; no public surface may be left untested.
- **`context-sharing`** — Shared construction in `beforeEach` / factory at three sibling dupes.
- **`oo-api-design`** — Ask-don't-tell: construct fully; own state on the object; operations on the closest domain concept.
- **`honors-documented-surface-contracts`** — Public API must match documented surface contracts; if a spec fights the contract, fix the spec.
- **`roundtrip-parity-is-required`** — Adapter parse/render seams assert `counts(parse(render(canonical))) == counts(canonical)`.
- **`code-source-of-truth-guard`** — Tests reject unsafe regeneration when generation can overwrite hand-edited code.
- **`impl-must-carry-bdd-manifest`** — Impl paired with `*_spec.py` carries `# @toolset-manifest … context_tools.bdd.bdd:Bdd`.
- **`observable-behavior`** — Assert public outcomes only.
- **`scan-fixture-pair`** — A mechanical mistake spec passes the fail file to `expect_scan_fails` and the pass file to `expect_scan_passes` (`context_tools.bdd.spec_helpers`). Do not invent a parallel eval spec harness.

---

## evals/backends-restate-shared-behavior/fail.md

# HIERARCHY: story-graph-ops — Diagrams and Code sections rendered without an abstract subject

<!--
Violates: abstract-subject-then-concrete-backends.

Every concrete backend restates the same structural and reconciliation observations
that a single abstract subject (`a diagram Story Map`, `a code Story Map`) would carry
once. The behavior is real and state-oriented, but it is duplicated across backends.

Add a fifth backend (Whimsical, Excalidraw, Kotlin, Rust…) and every observation
below gets copy-pasted again — the specifications will silently drift.
-->

## Diagrams

a DrawIO Story Map
  that holds a rendered Story Map with 4 Epics and 3 SubEpics under the first Epic
    it should contain 4 Epic elements on the Epic row
    every Epic element
      it should sit at its Epic's row Y coordinate

    with a fifth Epic appended
      it should contain 5 Epic elements on the Epic row
      the first 4 Epic elements
        it should be byte-identical to before

    with the first Epic removed
      it should contain 3 Epic elements
      the SubEpic elements that lived under the removed Epic
        it should be gone

    with the first Epic renamed
      the Epic element for the first Epic
        it should carry the new name

a Miro Story Map
  that holds a rendered Story Map with 4 Epics and 3 SubEpics under the first Epic
    it should contain 4 Epic elements on the Epic row
    every Epic element
      it should sit at its Epic's row Y coordinate

    with a fifth Epic appended
      it should contain 5 Epic elements on the Epic row
      the first 4 Epic elements
        it should be unchanged

    with the first Epic removed
      it should contain 3 Epic elements
      the SubEpic elements that lived under the removed Epic
        it should be gone

    with the first Epic renamed
      the Epic element for the first Epic
        it should carry the new name

## Code

a TypeScript story-spec Story Map
  that holds a rendered Story Map with 4 Epics
    every Epic
      it should produce a folder under the tests root, named after the Epic slug

    with a fifth Epic appended
      the appended Epic
        it should produce a new folder under the tests root

    with the first Epic renamed
      the folder for the first Epic
        it should carry the new slug

a Python acceptance-test Story Map
  that holds a rendered Story Map with 4 Epics
    every Epic
      it should produce a folder under the tests root, named after the Epic slug

    with a fifth Epic appended
      the appended Epic
        it should produce a new folder under the tests root

    with the first Epic renamed
      the folder for the first Epic
        it should carry the new slug

a Java acceptance-test Story Map
  that holds a rendered Story Map with 4 Epics
    every Epic
      it should produce a folder under the tests root, named after the Epic slug

    with a fifth Epic appended
      the appended Epic
        it should produce a new folder under the tests root

    with the first Epic renamed
      the folder for the first Epic
        it should carry the new slug


## evals/backends-restate-shared-behavior/pass.md

# HIERARCHY: story-graph-ops — Diagrams and Code with abstract subjects

<!--
Passes: abstract-subject-then-concrete-backends.

Shared structural and reconciliation observations live once on the abstract
subject (`a diagram Story Map`, `a code Story Map`). Concrete backends are thin
and add only backend-specific proofs — no duplicated shared behavior.
-->

## Diagrams

a diagram Story Map
  that holds a rendered Story Map with 4 Epics and 3 SubEpics under the first Epic
    it should contain 4 Epic elements on the Epic row in sequential order
    it should contain 3 SubEpic elements on the SubEpic row, directly under the first Epic

    with a fifth Epic appended
      it should contain 5 Epic elements on the Epic row
      the first 4 Epic elements
        it should be unchanged in position and identity

    with the first Epic removed
      it should contain 3 Epic elements
      the SubEpic elements that lived under the removed Epic
        it should be gone

a DrawIO Story Map
  <!-- Every "a diagram Story Map" behavior applies. Only DrawIO-specific
       serialization proofs live here. -->
  that holds a rendered diagram Story Map with 4 Epics
    every Epic element
      it should be an mxCell whose style carries the Epic swatch
    the serialized diagram
      it should parse as valid draw.io XML

## Code

a code Story Map
  that holds a rendered Story Map with 4 Epics
    every Epic
      it should produce a folder under the tests root, named after the Epic slug

    with a fifth Epic appended
      the appended Epic
        it should produce a new folder under the tests root

    with the first Epic renamed
      the folder for the first Epic
        it should carry the new slug

a TypeScript story-spec Story Map
  <!-- Every "a code Story Map" behavior applies. Only TypeScript-specific
       spec-data proofs live here. -->
  that holds a rendered code Story Map with 4 Epics
    every leaf file
      it should be named `<sub-epic-slug>-stories.ts`
      it should parse as valid TypeScript and typecheck against the story-types module


## evals/leaves-not-state-oriented/fail.md

# HIERARCHY: story-graph-ops (excerpt — Story Model)

Story Model
  StoryMap
    should add an Epic to a StoryMap
    should remove an Epic from a StoryMap
    should reorder Epics in a StoryMap by sequential order
    should list every Story in a StoryMap recursively across every Epic and SubEpic
  Epic
    should rename an Epic
    should add a SubEpic under an Epic
    should remove a SubEpic and its subtree from an Epic
    should reorder SubEpics under an Epic
    should move a SubEpic to a different Epic
  SubEpic
    should rename a SubEpic
    should nest a SubEpic under another SubEpic
    should add a Story under a SubEpic
    should remove a Story from a SubEpic


## evals/leaves-not-state-oriented/pass.md

# HIERARCHY: story-graph-ops (excerpt — Story Model)

<!--
Passes: state-oriented-hierarchy, category-headings-not-subjects.

Every non-leaf describe is a subject noun phrase or a state elaboration opened
with `with` / `that`. Every leaf is `it should …` observing an outside-verifiable
result. Organizational scaffolding is a `##` heading, not a describe.
-->

## Story Model

a Story Map
  it should hold no Epics

  with 4 Epics in sequential order
    it should hold 4 Epics
    it should list the Epics in sequential order

    with a fifth Epic appended
      it should hold 5 Epics
      the last Epic in sequential order
        it should be the appended Epic

    with the first Epic removed
      it should hold 3 Epics
      it should discard the SubEpics that lived under the removed Epic

    with the first Epic renamed
      it should preserve the sequential order of the Epics
      the first Epic
        it should carry the new name

    with the first Epic holding 3 SubEpics
      the first Epic
        it should hold 3 SubEpics

      with the first SubEpic moved from the first Epic to the second Epic
        the first Epic
          it should hold 2 SubEpics
        the second Epic
          it should hold one additional SubEpic
        the moved SubEpic
          it should keep its Stories and AcceptanceCriteria


## evals/observations-are-mechanics/fail.md

# HIERARCHY: story-graph-ops (excerpt captured as a failure fixture)
<!-- Every leaf here observes an internal method call, super chain, or private helper — not a result the reader could verify from outside the implementation. -->

a StoryNode

  that has been translated from a source with an added child
    the target
      it should hold the new child
      it should have called its own createChildXxx factory to produce the new child
      it should have called translateFrom on the new child to fill its fields

  that is reconciling a child collection
    the reconciliation
      it should match self-children to source-children by name and sequential order via findMatch before creating any new child
      it should call translateFrom on every matched pair
      it should process child collection pairs in the order declared by childCollections

a DiagramStoryNode

  that has had updateSelf called
    it should have copied the domain fields from source first via super.updateSelf
    it should have set position and size from the placementRules for its type
    it should have applied the formatting from the formattingRules for its type

a CodeStoryNode

  that has had updateSelf called
    it should have copied the domain fields from source first via super.updateSelf
    it should have written the language-agnostic structure to the held LanguageAst
    the held LanguageAst
      it should never be replaced


## evals/observations-are-mechanics/pass.md

# HIERARCHY: story-graph-ops (excerpt — results, not mechanics)

<!--
Passes: observations-are-results-not-mechanics, subjects-are-domain-concepts,
business-readable-language, domain-practice-alignment.

Every leaf observes an outcome an outsider could verify. Subjects are domain
concepts. No super calls, factory names, private helpers, or call-order facts.
-->

## Story Model

a Story Map
  that holds 4 Epics and 3 SubEpics under the first Epic
    it should hold 4 Epics
    the first Epic
      it should hold 3 SubEpics

    with a fifth Epic appended
      it should hold 5 Epics
      the last Epic in sequential order
        it should be the appended Epic

## Documents

a Markdown document
  that holds a rendered Story Map with 4 Epics and 3 SubEpics under the first Epic
    it should contain 4 top-level headings in sequential order

    with the first Epic renamed in the source Story Map and re-rendered
      the first heading
        it should carry the new name

  that has been edited in place and synced back against a canonical Story Map
    the returned UpdateReport
      it should list every add, remove, rename, and reorder applied to the document
    the reconstructed Story Map
      it should reflect every edit made to the document

## Diagrams

a diagram Story Map
  that holds a rendered Story Map with 4 Epics
    it should contain 4 Epic elements on the Epic row in sequential order

    with the first Epic removed
      it should contain 3 Epic elements
      the SubEpic elements that lived under the removed Epic
        it should be gone


## evals/state-oriented-story-map/fail.md

# HIERARCHY: story-graph-ops (excerpt — Story Model)

<!--
Violates: state-oriented-hierarchy, category-headings-not-subjects.

Describes are bare class names; leaves restate operations as if the class were
the actor. No subject noun phrase, no state buildup, no observations of state.
`Story Model` is used as a describe rather than a `##` heading.
-->

Story Model
  StoryMap
    should add an Epic to a StoryMap
    should remove an Epic from a StoryMap
    should reorder Epics in a StoryMap by sequential order
    should list every Story in a StoryMap recursively across every Epic and SubEpic
  Epic
    should rename an Epic
    should add a SubEpic under an Epic
    should remove a SubEpic and its subtree from an Epic
    should reorder SubEpics under an Epic
    should move a SubEpic to a different Epic
  SubEpic
    should rename a SubEpic
    should nest a SubEpic under another SubEpic
    should add a Story under a SubEpic
    should remove a Story from a SubEpic


## evals/state-oriented-story-map/pass.md

# HIERARCHY: story-graph-ops (canonical excerpt)

<!--
This excerpt is the canonical passing shape. It demonstrates every rule in
this skill applied to a single domain:

- state-oriented-hierarchy: every non-leaf describe is a subject noun phrase
  or a state elaboration opened with `with` / `that`; every leaf is `it should …`.
- observations-are-results-not-mechanics: leaves observe outcomes an outsider
  could verify — no super calls, no factory names, no private helper names,
  no call-order facts.
- subjects-are-domain-concepts: every top-level describe is a domain concept
  a domain expert would recognise ("a Story Map", "a Markdown document",
  "a diagram Story Map", "a code Story Map", "a DrawIO Story Map",
  "a TypeScript story-spec Story Map"). No ast, node, synchronizer,
  positions, or service-class stereotype.
- category-headings-not-subjects: organizational scaffolding (Story Model,
  Documents, Diagrams, Code) is `##` markdown, not describes.
- abstract-subject-then-concrete-backends: for Diagrams and Code the shared
  behavior lives on an abstract subject (`a diagram Story Map`, `a code Story Map`);
  concrete backends are thin and add only backend-specific proofs.
-->

## Story Model

a Story Map
  it should hold no Epics

  with 4 Epics in sequential order
    it should hold 4 Epics
    it should list the Epics in sequential order

    with a fifth Epic appended
      it should hold 5 Epics
      the last Epic in sequential order
        it should be the appended Epic

    with the first Epic removed
      it should hold 3 Epics
      it should discard the SubEpics that lived under the removed Epic

    with the first Epic renamed
      it should preserve the sequential order of the Epics
      the first Epic
        it should carry the new name

    with the first Epic holding 3 SubEpics
      the first Epic
        it should hold 3 SubEpics

      with the first SubEpic moved from the first Epic to the second Epic
        the first Epic
          it should hold 2 SubEpics
        the second Epic
          it should hold one additional SubEpic
        the moved SubEpic
          it should keep its Stories and AcceptanceCriteria

## Documents

a Markdown document
  that holds a rendered Story Map with 4 Epics and 3 SubEpics under the first Epic
    it should contain 4 top-level headings in sequential order

    with the first Epic renamed in the source Story Map and re-rendered
      the first heading
        it should carry the new name

    with the first Epic removed in the source Story Map and re-rendered
      it should contain 3 top-level headings

  that has been edited in place and synced back against a canonical Story Map
    the returned UpdateReport
      it should list every add, remove, rename, and reorder applied to the document
    the reconstructed Story Map
      it should reflect every edit made to the document

## Diagrams

a diagram Story Map
  that holds a rendered Story Map with 4 Epics and 3 SubEpics under the first Epic
    it should contain 4 Epic elements on the Epic row in sequential order
    it should contain 3 SubEpic elements on the SubEpic row, directly under the first Epic

    with a fifth Epic appended
      it should contain 5 Epic elements on the Epic row
      the first 4 Epic elements
        it should be unchanged in position and identity

    with the first Epic removed
      it should contain 3 Epic elements
      the SubEpic elements that lived under the removed Epic
        it should be gone

a DrawIO Story Map
  <!-- Every "a diagram Story Map" behavior applies. Only DrawIO-specific
       serialization proofs live here. -->
  that holds a rendered diagram Story Map with 4 Epics
    every Epic element
      it should be an mxCell whose style carries the Epic swatch
    the serialized diagram
      it should parse as valid draw.io XML

## Code

a code Story Map
  that holds a rendered Story Map with 4 Epics and 3 SubEpics under the first Epic
    every Epic
      it should produce a folder under the tests root, named after the Epic slug

    with a fifth Epic appended
      the appended Epic
        it should produce a new folder under the tests root
      the folders for the first four Epics
        it should be byte-identical to before

    with the first Epic renamed
      the folder for the first Epic
        it should carry the new slug
        its contents
          it should be byte-identical to before

    with the first Epic holding 3 leaf SubEpics
      every leaf SubEpic of the first Epic
        it should produce a sub-folder under the first Epic's folder, named after the SubEpic slug
        it should produce exactly one leaf file inside its own sub-folder, named after the SubEpic slug

      with the first SubEpic of the first Epic holding 2 Stories
        the leaf file for the first SubEpic
          it should contain 2 Story blocks
        every Story
          it should produce one Story block inside its SubEpic's leaf file, named after the Story

        with the first Story of the first SubEpic holding 3 AcceptanceCriteria
          the Story block for the first Story
            it should expose 3 Scenarios (one per AcceptanceCriteria) in the AcceptanceCriteria's declared order
          every AcceptanceCriteria
            it should produce one Scenario inside its Story block, holding the AcceptanceCriteria's Gherkin steps in order

a TypeScript story-spec Story Map
  <!-- Every "a code Story Map" behavior applies. Only TypeScript-specific
       spec-data proofs live here. -->
  that holds a rendered code Story Map with 4 Epics
    every leaf file
      it should be named `<sub-epic-slug>-stories.ts`
      it should parse as valid TypeScript and typecheck against the story-types module
    every Story block
      it should be an exported const named after the Story in UPPER_SNAKE_CASE, initialised with `as const`
    every Scenario property inside a Story block
      it should be a single-keyed object whose value carries `name` and `steps` fields


## evals/subjects-are-code-stereotypes/fail.md

# HIERARCHY: story-graph-ops (excerpt captured as a failure fixture)
<!-- Every top-level describe here is a code-level class name, not a domain concept. LanguageAst / TypeScriptAst / CodeStoryNode are compiler-implementation stereotypes; RowPositions is a layout helper; MarkdownSynchronizer / TypeScriptSynchronizer are service classes; DiagramStoryNode is an abstract class exposed as a subject instead of the domain concept it represents (a diagram Story Map). The state-oriented and observations-are-results rules can be clean while this rule is still violated. -->

a LanguageAst

  that has been asked to parse a raw source string
    it should populate its internal AST from the source

  that has been asked to generate source code
    it should produce a raw source string from the internal AST

a TypeScriptAst

  that is generating from a StoryNode
    it should produce a TypeScript interface for the node
    it should produce a describe block for the node

a CodeStoryNode

  that has had updateSelf called from a source
    it should carry the same domain fields as the source
    the held LanguageAst
      it should reflect the language-agnostic structure of the node

a RowPositions

  that has been constructed for a tree with a maximum SubEpic depth of 2
    the SubEpic row for depth 0
      it should sit directly below the Epic row
    the actor row
      it should sit directly below the deepest SubEpic row

a DiagramStoryNode

  a SubEpic
    with an Epic parent
      it should accept the parent
    with a Story parent
      it should reject the parent

a MarkdownSynchronizer
  that has synced a canonical Story Map into an existing Markdown document
    the returned UpdateReport
      it should list every add, remove, rename, reorder, and move applied to the document

a TypeScriptSynchronizer
  that has regenerated the folder from a canonical Story Map
    the returned UpdateReport
      it should list every add, remove, rename, reorder, and move applied to the folder


## evals/subjects-are-code-stereotypes/pass.md

# HIERARCHY: story-graph-ops (excerpt — domain-concept subjects)

<!--
Passes: subjects-are-domain-concepts, domain-practice-alignment.

Every top-level describe is a domain concept a domain expert would recognise.
No LanguageAst, CodeStoryNode, RowPositions, Synchronizer, or other
compiler-/service-class stereotypes.
-->

## Story Model

a Story Map
  it should hold no Epics
  with 4 Epics in sequential order
    it should hold 4 Epics

## Documents

a Markdown document
  that holds a rendered Story Map with 4 Epics
    it should contain 4 top-level headings in sequential order

## Diagrams

a diagram Story Map
  that holds a rendered Story Map with 4 Epics
    it should contain 4 Epic elements on the Epic row

a DrawIO Story Map
  that holds a rendered diagram Story Map with 4 Epics
    every Epic element
      it should be an mxCell whose style carries the Epic swatch

## Code

a code Story Map
  that holds a rendered Story Map with 4 Epics
    every Epic
      it should produce a folder under the tests root, named after the Epic slug

a TypeScript story-spec Story Map
  that holds a rendered code Story Map with 4 Epics
    every leaf file
      it should parse as valid TypeScript and typecheck against the story-types module


## evals/top-level-describe-is-category-label/fail.md

# HIERARCHY: story-graph-ops — section labels used as top-level describes

<!--
Violates: category-headings-not-subjects.

`Story Model`, `Documents`, `Diagrams`, `Code` are organizational category labels,
not domain subjects. Read any one of them in isolation — none names an observable
thing whose state can be narrowed and observed. They belong as `##` markdown
headings, not as top-level describes.

Everything nested underneath is otherwise well-formed state-oriented BDD, so the
other rules cannot catch this — the shape is broken at the top level, before the
first real subject describe.
-->

Story Model

  a Story Map
    it should hold no Epics
    with 4 Epics in sequential order
      it should hold 4 Epics
      with a fifth Epic appended
        it should hold 5 Epics

Documents

  a Markdown document
    that holds a rendered Story Map with 4 Epics
      it should contain 4 top-level headings

  a JSON document
    that holds a rendered Story Map with 4 Epics
      it should contain 4 Epic entries in declared order

Diagrams

  a diagram Story Map
    that holds a rendered Story Map with 4 Epics
      it should contain 4 Epic elements on the Epic row
      with a fifth Epic appended
        it should contain 5 Epic elements on the Epic row

Code

  a code Story Map
    that holds a rendered Story Map with 4 Epics
      every Epic
        it should produce a folder under the tests root, named after the Epic slug


## evals/top-level-describe-is-category-label/pass.md

# HIERARCHY: story-graph-ops — categories as markdown headings

<!--
Passes: category-headings-not-subjects, state-oriented-hierarchy,
domain-practice-alignment.

`Story Model`, `Documents`, `Diagrams`, `Code` are `##` markdown headings.
Every top-level describe is a domain-concept subject noun phrase.
-->

## Story Model

a Story Map
  it should hold no Epics
  with 4 Epics in sequential order
    it should hold 4 Epics
    with a fifth Epic appended
      it should hold 5 Epics

## Documents

a Markdown document
  that holds a rendered Story Map with 4 Epics
    it should contain 4 top-level headings

a JSON document
  that holds a rendered Story Map with 4 Epics
    it should contain 4 Epic entries in declared order

## Diagrams

a diagram Story Map
  that holds a rendered Story Map with 4 Epics
    it should contain 4 Epic elements on the Epic row
    with a fifth Epic appended
      it should contain 5 Epic elements on the Epic row

## Code

a code Story Map
  that holds a rendered Story Map with 4 Epics
    every Epic
      it should produce a folder under the tests root, named after the Epic slug


## examples.md

# Examples — BDD fidelities

## Behavior hierarchy input (prerequisite)

Approved plain-English hierarchy (`character-behavior.md`) used as input to **behavior** fidelity:

```
Character
  that has been created
    should have initial stats assigned
    should have zero starting wounds
  that is in combat
    should track current wounds
    should apply damage from attacks
  Attack
    that has targeted an enemy
      should calculate hit chance using character stats
      should consume one action from the active turn
    that has missed
      should deal no damage
      should still consume one action
  that has been defeated
    should be removed from the initiative order
```

---

## Behavior fidelity — signatures

### Jest/TypeScript output (`character.test.ts`)

```typescript
describe('Character', () => {
  describe('that has been created', () => {
    it('should have initial stats assigned', () => {
      // BDD: SIGNATURE
    });
    it('should have zero starting wounds', () => {
      // BDD: SIGNATURE
    });
  });

  describe('that is in combat', () => {
    it('should track current wounds', () => {
      // BDD: SIGNATURE
    });
    it('should apply damage from attacks', () => {
      // BDD: SIGNATURE
    });
  });

  describe('Attack', () => {
    describe('that has targeted an enemy', () => {
      it('should calculate hit chance using character stats', () => {
        // BDD: SIGNATURE
      });
      it('should consume one action from the active turn', () => {
        // BDD: SIGNATURE
      });
    });

    describe('that has missed', () => {
      it('should deal no damage', () => {
        // BDD: SIGNATURE
      });
      it('should still consume one action', () => {
        // BDD: SIGNATURE
      });
    });
  });

  describe('that has been defeated', () => {
    it('should be removed from the initiative order', () => {
      // BDD: SIGNATURE
    });
  });
});
```

### Mamba/Python output (`character_spec.py`)

```python
from mamba import description, context, it

with description('Character'):
    with context('that has been created'):
        with it('should have initial stats assigned'):
            # BDD: SIGNATURE
        with it('should have zero starting wounds'):
            # BDD: SIGNATURE

    with context('that is in combat'):
        with it('should track current wounds'):
            # BDD: SIGNATURE
        with it('should apply damage from attacks'):
            # BDD: SIGNATURE

    with description('Attack'):
        with context('that has targeted an enemy'):
            with it('should calculate hit chance using character stats'):
                # BDD: SIGNATURE
            with it('should consume one action from the active turn'):
                # BDD: SIGNATURE

        with context('that has missed'):
            with it('should deal no damage'):
                # BDD: SIGNATURE
            with it('should still consume one action'):
                # BDD: SIGNATURE

    with context('that has been defeated'):
        with it('should be removed from the initiative order'):
            # BDD: SIGNATURE
```

### What to notice

- Behavior hierarchy has 9 `should` lines → signature has 9 `it` blocks. Count matches exactly.
- 4 nesting levels in scaffold → 4 levels in code.
- Every body contains `// BDD: SIGNATURE` (Jest) or `# BDD: SIGNATURE` (Mamba) and nothing else.
- No imports, no assertions, no mocks, no `beforeEach`.
- `it('should …')` matches the behavior hierarchy text verbatim — no paraphrasing.

### Batch processing for large behavior hierarchies

When a behavior hierarchy has more than ~18 describe blocks, process in batches:

1. First batch: top-level concept and its first 2-3 state blocks (~18 describes).
2. Subsequent batches: remaining state blocks and sub-context_tools.
3. Confirm after each batch that the hierarchy count matches the behavior hierarchy for that slice.

---

## Development fidelity — tests + code

### Phase 1: Signature → Test implementation

**Input (signature)**

```typescript
describe('Character', () => {
  describe('that has been created', () => {
    it('should have initial stats assigned', () => {
      // BDD: SIGNATURE
    });
    it('should have zero starting wounds', () => {
      // BDD: SIGNATURE
    });
  });

  describe('that is in combat', () => {
    it('should track current wounds', () => {
      // BDD: SIGNATURE
    });
    it('should apply damage from attacks', () => {
      // BDD: SIGNATURE
    });
  });
});
```

**Output (test implementation — Jest/TypeScript)**

```typescript
import { Character } from '../Character';

function defaultStats() {
  return { strength: 10, agility: 8, endurance: 6 };
}

describe('Character', () => {
  describe('that has been created', () => {
    it('should have initial stats assigned', () => {
      // Arrange
      const stats = defaultStats();
      // Act
      const character = new Character({ name: 'Test', stats });
      // Assert
      expect(character.stats.strength).toBe(10);
      expect(character.stats.agility).toBe(8);
    });

    it('should have zero starting wounds', () => {
      // Arrange / Act
      const character = new Character({ name: 'Test', stats: defaultStats() });
      // Assert
      expect(character.wounds).toBe(0);
    });
  });

  describe('that is in combat', () => {
    let character: Character;

    beforeEach(() => {
      character = new Character({ name: 'Test', stats: defaultStats() });
    });

    it('should track current wounds', () => {
      // Act
      character.applyDamage(3);
      // Assert
      expect(character.wounds).toBe(3);
    });

    it('should apply damage from attacks', () => {
      // Arrange
      character.applyDamage(2);
      // Act
      character.applyDamage(4);
      // Assert
      expect(character.wounds).toBe(6);
    });
  });
});
```

### Phase 2: Failing tests → Minimal production code

Tests above are RED — `Character` does not exist.

**Output (minimal production code — TypeScript)**

```typescript
// Character.ts

interface Stats {
  strength: number;
  agility: number;
  endurance: number;
}

interface CharacterProps {
  name: string;
  stats: Stats;
}

export class Character {
  readonly name: string;
  readonly stats: Stats;
  wounds = 0;

  constructor({ name, stats }: CharacterProps) {
    this.name = name;
    this.stats = stats;
  }

  applyDamage(amount: number): void {
    this.wounds += amount;
  }
}
```

**What to notice:**
- Only properties tests assert on: `stats`, `wounds`. No `createdAt`, `id`, etc.
- Only methods tests call: `applyDamage`. No `heal()`, `die()`, etc.
- `wounds` starts at `0` because the test asserts `expect(character.wounds).toBe(0)`.
- Class used (not function) because `wounds` is mutable state that accumulates across calls.

### Mamba/Python equivalent

**Test implementation**

```python
from mamba import description, context, it, before
from expects import equal, expect
from character import Character

def default_stats():
    return {'strength': 10, 'agility': 8, 'endurance': 6}

with description('Character'):
    with context('that has been created'):
        with it('should have initial stats assigned'):
            # Arrange / Act
            character = Character(name='Test', stats=default_stats())
            # Assert
            expect(character.stats['strength']).to(equal(10))
            expect(character.stats['agility']).to(equal(8))

        with it('should have zero starting wounds'):
            # Arrange / Act
            character = Character(name='Test', stats=default_stats())
            # Assert
            expect(character.wounds).to(equal(0))

    with context('that is in combat'):
        with before.each:
            self.character = Character(name='Test', stats=default_stats())

        with it('should track current wounds'):
            self.character.apply_damage(3)
            expect(self.character.wounds).to(equal(3))

        with it('should apply damage from attacks'):
            self.character.apply_damage(2)
            self.character.apply_damage(4)
            expect(self.character.wounds).to(equal(6))
```

**Minimal production code (Python)**

```python
# character.py

class Character:
    def __init__(self, name: str, stats: dict):
        self.name = name
        self.stats = stats
        self.wounds = 0

    def apply_damage(self, amount: int) -> None:
        self.wounds += amount
```

### Layer boundary mocking example (service layer)

When testing a service that depends on a repository:

```typescript
import { VoucherService } from '../VoucherService';
import { VoucherRepository } from '../VoucherRepository';

describe('VoucherService', () => {
  describe('that is creating a voucher', () => {
    let service: VoucherService;
    let mockRepo: jest.Mocked<Pick<VoucherRepository, 'save'>>;

    beforeEach(() => {
      mockRepo = { save: jest.fn().mockResolvedValue(undefined) };
      service = new VoucherService(mockRepo as VoucherRepository);
    });

    it('should persist the voucher when input is valid', async () => {
      // Arrange
      const input = { code: 'ABC-001', campaignId: 'camp-1' };
      // Act
      await service.create(input);
      // Assert
      expect(mockRepo.save).toHaveBeenCalledWith(
        expect.objectContaining({ code: 'ABC-001' })
      );
    });
  });
});
```

**Mock is at the boundary** (repository) — the service is fully tested; the repository mock is not the thing under test.

"""
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""
# =============================================================================
# BDD Development Template - Mamba/Python Test Implementation
# =============================================================================
# Instructions (for skill maintainers - delete this block when generating):
#
#   1. Replace {DomainEntity} with the class or module under test.
#   2. Import only the entity under test.
#   3. Add a factory function for shared test-data objects.
#   4. Use `with before.each:` for shared object setup when 3+ siblings need it.
#   5. Each `with it():` body uses # Arrange / # Act / # Assert comments.
#   6. One assertion per behavior.
#   7. Replace `# BDD: SIGNATURE` markers - do not leave any in the final file.
#   8. Delete this instruction block before committing the file.
#   9. Keep the edit/check manifest header above - do not strip it.
# =============================================================================
from mamba import description, context, it, before
from expects import equal, be_none, be_true, expect
from {domain_module} import {DomainEntity}


def default_{related_data}() -> dict:
    """Minimal valid test data - populate only fields tests assert on."""
    return {
        # field: value
    }


with description('{DomainEntity}'):
    with context('that has been created'):
        with it('should have {initial property} assigned'):
            # Arrange / Act
            entity = {DomainEntity}(**default_{related_data}())
            # Assert
            expect(entity.{property}).to(equal({expected_value}))

    with context('that is {active state}'):
        with before.each:
            self.entity = {DomainEntity}(**default_{related_data}())

        with it('should {behavior description}'):
            # Act
            self.entity.{action}({input})
            # Assert
            expect(self.entity.{property}).to(equal({expected_value}))

        with it('should {second behavior}'):
            # Arrange
            {local_setup} = {value}
            # Act
            self.entity.{action}({local_setup})
            # Assert
            expect(self.entity.{property}).to(equal({expected_value}))


# Scan fixture pair — mechanical mistake specs use these helpers, not an eval harness.
from context_tools.bdd.spec_helpers import expect_scan_fails, expect_scan_passes

with description('a scan fixture pair'):
    with context('a file that violates the rule'):
        with it('should fail scan'):
            expect_scan_fails({scan}, '{FailFixturePath}', rule='{Rule}')

    with context('a file that satisfies the rule'):
        with it('should pass scan'):
            expect_scan_passes({scan}, '{PassFixturePath}', rule='{Rule}')