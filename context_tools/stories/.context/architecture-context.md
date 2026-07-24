---
generating-skill: abd-architecture-specification
type: package-context
fidelity: specification
---

# Package: formats/code/

> **Base contract:** The `translateFrom` algorithm, four-slot pattern, abstract class
> specs, and rules shared by every backend are defined in the central
> [architecture-specification.md § Multi-Format Story Rendering](../architecture-context.md#multi-format-story-rendering).
> Read that section first. This file covers only what code backends add on top.

---

## Overview

Code backends render a `StoryMap` as a **source-code tree**. Unlike diagram or JSON
backends, code produces two **kinds** of files per story with fundamentally
different regeneration semantics:

| File kind | Filename shape | Content | Regeneration policy |
| --- | --- | --- | --- |
| **Spec file** | `<story-slug>-stories.<ext>` | Pure story-map data as language literals: `Story` constant with `story`, `actor`, `domainTerms`, `evidence`, plus one scenario per key with phase-grouped `given` + `interactions` | **Bidirectional round-trip.** Adapter renders freely on every run. Parsing the file reconstructs the StoryMap byte-for-byte. |
| **Tier file** | `<story-slug>-<tier>.test.<ext>` (TS/TSX/JS), `test_<story_slug>_<tier>.py` (Python), `<StorySlug><Tier>Test.java` (Java) | ONE file per (story, tier) containing BOTH the `TierImpl` class AND the `runScenario(...)` wiring calls. Imports the spec constant from the sibling spec file. | **Write-once.** Adapter creates the skeleton the first time it doesn't exist. Once present, the adapter never overwrites — the human/AI mutates it in place to preserve hand-authored bodies. |

This split is the mechanism that lets code generation stay useful without eating
developer work. The **spec** is the domain graph translated to code; the **tier
files** are engineering artifacts that reference the spec but grow independently.

### Code path vs AI path — different jobs

Two very different producers write into a code tier tree, and it's worth naming
them clearly because they have opposite guarantees:

- **The code path (scaffolder + spec renderer).** Deterministic, one-shot,
  bootstrap-only. Invoked from `context_tools/stories/cli/main.py` (`render-tree`,
  `scaffold-tiers`, `translate`). Given a `StoryMap`, it can render the spec
  file byte-for-byte reproducibly, and if a tier file does not yet exist it
  emits a skeleton with every `given`/`when`/`then` key present but stubbed
  (`// TODO`, `raise NotImplementedError`, `throw new Error('not implemented')`
  — the exact form varies by backend). That skeleton exists purely so the AI
  or human has a well-shaped surface to fill in.
- **The AI / human path.** This is where the work happens the majority of the
  time. Filling in stubs with real assertions, driving the UI with real user
  events, connecting to a real (or realistically stubbed) HTTP boundary,
  writing pure-domain invariant tests. The eval framework under
  `context_tools/stories/evals/05-engineering/` measures this path, not the scaffolder — a
  passing engineering run is one where the tier file has **implemented**
  bodies, not the scaffold shape.

The scanner `tier-bodies-implemented` guards this line: it flags any step body
that still carries a `TODO`, is comment-only, or throws a not-implemented
placeholder. That's how the engineering fidelity gate refuses to accept a run
that just re-emits the scaffolder's output.

The `Story` is the **folder** boundary: each story gets one folder containing
one spec file and one tier file per declared tier (e.g. `server`, `client`,
`e2e`, `domain`).

**One tier = one file.** The tier class and its `runScenario(...)` wiring live
in the same file. The `.test.<ext>` (or `test_` prefix in Python, or `Test`
suffix in Java) is what test runners auto-discover, and everything else that
belongs to that tier — class definition, dispatch tables, cleanup — lives
alongside the wiring. A previous version of this doc split them into
`<slug>-<tier>.<ext>` (class) + `<slug>-<tier>.test.<ext>` (wiring); that split
carried no benefit and has been retired.

---

## Why this shape

**The problem — code cannot be one uniform file.** A real test file contains
`given_account_has_balance(step)`, `when_treasurer_submits(step, account)`,
`then_transfer_settles_same_day(step, result)` helpers with actual assertions
against real modules. If code generation ran end-to-end it would either (a) wipe
those helpers on every run, or (b) require the adapter to understand which lines
are "user code" — a task the adapter is not equipped to do safely.

**The inversion — split the file, split the responsibility.** Facts the graph
knows (story name, actor, Given/When/Then step text, examples table) live in
`-stories.<ext>`. Everything the graph does not know (given/when/then helper
bodies, framework wiring, imports of production modules, assertions) lives in
`-<layer>.<ext>` or the single-file Python test. The adapter fully owns spec
files. It never owns test files; it can scaffold them once, then hands them off.

**The disciplines.** *`-stories` files are pure literals* — no helper functions,
no imports beyond types, no comments beyond block dividers. This keeps them
byte-reversible: `render(parse(x)) == x`. *Test files import from the spec
file next to them* — never inline the same data twice; the constant is the
source of truth. *The adapter refuses to overwrite existing test files* —
regeneration is a no-op when a test file exists; the AI is responsible for
adding new test methods when the spec grows.

---

## File Layout (per story)

```
tests/
+-- story-test.<ext>                         <- GWT helpers (story / scenario / given / when / then)
+-- <epic-slug>/
    +-- <epic-slug>-helper.<ext>             <- ExampleFactory accessors
    +-- <sub-epic-slug>/
        +-- <story-slug>/
            +-- <story_snake>_story.<ext>         <- explore/spec (fake + public interface)
            +-- <story_snake>_spec.<ext>          <- isolated objects (write-once)
            +-- <story_snake>_spec.production.<ext> <- other tiers (write-once)
```

**Language variation — story / isolated-spec / tier-spec:**

| Language | Story (explore/spec) | Isolated | Other tiers |
| --- | --- | --- | --- |
| JavaScript | `<story_snake>_story.js` | `<story_snake>_spec.js` | `<story_snake>_spec.{tier}.js` |
| Python | `<story_snake>_story.py` | `<story_snake>_spec.py` | `<story_snake>_spec.{tier}.py` |
| TypeScript | `<story_snake>_story.ts` | `<story_snake>_spec.ts` | `<story_snake>_spec.{tier}.ts` |
| Java | `<StorySlug>Story.java` | `<StorySlug>Spec.java` | `<StorySlug>Spec<Tier>.java` |

Explore/spec story files are **runnable** Given / When / Then against factory
**fakes**, asserting the **public interface** of `I{Type}`. Concrete values live
in `{Type}ExampleFactory` — not inventable `examples: [{ … }]` tables in the
story file. Tier specs call the shared story function with `isolated` or
`production` mode.

The `context_tools/stories/examples/{ts,py}/process-payments/` trees are the canonical
reference of what a fully-expanded code example looks like: root document-mode
`story-context.md`, one sub-epic folder per sub-epic, and exactly one
`<slug>-stories.<ext>` per sub-epic. No test files live in the story examples —
tests are a different concern with their own examples elsewhere.

**Python-only naming exception — snake-case epic helper:**

Every other file across every backend is kebab-case
(`<sub-epic-slug>-stories.ts`, `<sub-epic-slug>-stories.py`, etc.). The
**epic-level shared helper** for Python (`<epic_slug>_helper.py`) is the single
exception because it must be a valid Python module identifier, and Python
identifiers cannot contain hyphens. Folder names stay kebab
(`process-payments/`); only this one file inside the epic folder is snake
(`process_payments_helper.py`). Leaf test files import from it via a small
`sys.path` shim — the name in the `import` statement is the snake form.

| What | Convention | Example |
| --- | --- | --- |
| Epic folder | kebab | `process-payments/` |
| Sub-epic folder | kebab | `submit-wire-payment/` |
| Sub-epic spec file | kebab | `submit-wire-payment-stories.py` |
| Sub-epic test file | kebab | `submit-wire-payment-tests.py` |
| **Epic helper file** | **snake** | **`process_payments_helper.py`** |
| Java equivalent | PascalCase (no exception needed) | `ProcessPaymentsHelper.java` |

Java is unaffected because its file-per-class rule already forces PascalCase
(`ProcessPaymentsHelper.java`), which never contains hyphens in the first
place. Python is the only backend where the kebab-everywhere rule collides
with the language's identifier grammar, hence the single exception.

### Example factories (Clean Engineering link)

When scenarios need domain objects from CE, helpers **import `{Type}ExampleFactory`**
and call `load*({ mode })`. Story files import helpers and assert the public
`I{Type}` seam. Chain at explore/spec: steps → helper → factory → fake `I{Type}`.
At engineering, tier specs pass `isolated` (`{Type}` + injected mocks) or
`production` (`{Type}` + real collaborators). See `stories.md` § Example factories.

JSON is emitted as `stories.json` — one file per project, pure data, round-trip
by design. See `../document/json/` for details.

---

## File Structure (source tree of this package)

```
formats/code/
+-- architecture-context.md           <- this file
+-- code_story_map.py                 <- CodeStoryMap abstract base (render/parse/sync)
+-- typescript/
|   +-- typescript_story_map.py       <- TS spec-file render + parse
+-- python/
|   +-- python_story_map.py           <- Python test-file render (write-once)
+-- java/
    +-- java_story_map.py             <- Java spec-file + test-file render
```

---

## Read Path (what scanners use today)

Every scanner receives a pre-parsed `Workspace` from `workspace/loader.py`. For
the code path, the story-map loader delegates to the appropriate `<lang>StoryMap`
adapter's `parse()` method, which walks the tests folder and reconstructs
the `StoryMap` domain object from the `-stories.<ext>` files. Test files are
not read by these adapters; `workspace/tests_loader.py` handles those separately
into `TestFile` / `TestCase` objects for the tests-specific scanners.

```
tests/                                     workspace.story_map: StoryMap
+-- epic/                                     StoryMap
|   +-- sub-epic/                               \-- Epic
|       +-- sub-epic-stories.ts     ─►               \-- SubEpic
|       +-- sub-epic-api.ts     (ignored here)             \-- Story
|       +-- sub-epic-web.ts     (ignored here)                  \-- AC
```

The API contract on `CodeStoryMap`:

- `render(canonical: StoryMap, previous: Dict[str, str] = None) -> Dict[str, str]`
  — produces `{path: content}` for every file in the target tree.
- `parse(external: Dict[str, str]) -> StoryMap` — reconstructs the canonical
  graph from an existing tree.
- `sync(external, canonical) -> UpdateReport` — parse + `canonical.translate_from(parsed)`.

---

## Write Path (rendering) — spec vs test discipline

The adapter's `render()` produces every file, but the caller enforces a two-lane
policy on the output:

1. **Spec files (`-stories.<ext>`)** — write unconditionally. These are
   byte-reversible from the domain graph; no developer state to preserve.

2. **Test files (`-<layer>.<ext>` or Python `-tests.py`)** — write only if the
   file does not already exist. If it does exist, the adapter emits an
   **update advisory** — a structured record of what changed in the graph that
   the AI must reflect in the file. Advisories include:
   - New stories → new test class / describe block templates
   - New scenarios under an existing story → new `it(...)` / `def test_...`
     placeholders
   - Deleted context_tools/stories/scenarios → marker comments the AI can remove after
     verifying the tests are truly dead
   The adapter never modifies existing test-file lines.

Under this discipline the current `HAND-WRITTEN START` / `HAND-WRITTEN END`
marker comments inside a single file (the migrated story-graph-ops model) are
**obsolete**: hand-written code lives in a physically separate file, so there
is no need to fence it inside the generated file.

> **Migration status.** The migrated adapter code (`code_story_map.py`,
> `typescript_story_map.py`, etc.) currently supports render+parse of spec
> files and still carries the legacy `_preserve_hand_written` mechanism for
> single-file backwards compatibility. The write-once policy for test files
> is enforced by the caller, not the adapter, and lands as part of the
> `context_tools/stories/eval.py` unified runner (Phase D).

---

## Layer 2: CodeStoryMap (shared abstract base)

`CodeStoryMap` is the abstract Layer-2 base for all code backends. It owns:

- Folder-tree assembly (`<tests-root>/<epic>/<sub-epic>/`)
- Slug computation (`to_kebab`, `to_snake`, `to_upper_snake`, `to_pascal`, `to_camel`)
- The `render` / `parse` / `sync` uniform callable surface
- Duplicate-name resolution (`--<sequential_order>` suffix when siblings collide)

Each concrete backend overrides two hooks:

- `_render_leaf_file(sub_epic, epic) -> str` — emit the language-specific
  spec-file body for one leaf sub-epic.
- `_hydrate_leaf_sub_epic_from_content(sub_epic, file_name, content) -> None`
  — reverse: read a spec file's text and populate `sub_epic.stories` and
  their `acceptance_criteria`.

Backends that need a per-epic helper file (Python, Java) additionally override
`_render_epic_helper(epic)` and `_epic_helper_path(epic_root, epic)`.

---

## Layer 3: TypeScript / TSX Backend

The TypeScript backend renders one `-stories.ts` spec file per leaf sub-epic.
Its `_render_leaf_file` emits:

```typescript
import type { Step, AcceptanceCriterion, Background } from "../../story-types";

export const SUBMIT_SAME_DAY_TRANSFER = {
  story: `Submit same-day transfer`,
  actor: `Treasurer`,
  domain_terms: [],
  evidence: [],
  acceptance_criteria: [
    [{ when: `Submit transfer before cutoff time settles same day` }],
  ],
  submitTransferBeforeCutoffTimeSettlesSameDay: {
    name: `AC 1`,
    steps: [{ when: `Submit transfer before cutoff time settles same day` }] as const,
  },
} as const;
```

Its `_hydrate_leaf_sub_epic_from_content` uses non-greedy regex to extract
each `export const ... = { ... } as const;` block and reconstruct the
`Story` + `AcceptanceCriteria` records.

Test files (`-api.ts`, `-web.ts`, `-web.tsx`) are rendered from separate
templates under `context_tools/stories/templates/ts/`, `context_tools/stories/templates/tsx/`. See those
templates for their exact shape.

---

## Layer 3: Python Backend

Python has the same spec / test split as TypeScript.

**Spec file** — `<sub-epic-slug>-stories.py` — pure data literals only. Each
story is a module-level `Final` dict keyed by SCREAMING_SNAKE (matching the TS
`as const` convention translated to Python). Tuples-of-dicts express `steps`
and `examples` for the same reason TS uses `as const` arrays: to signal
immutability and enable round-tripping through the adapter. The adapter
regenerates this file freely on every run.

**Test file** — `<sub-epic-slug>-tests.py` — write-once. Contains `pytest`
fixtures and one `Test<StoryName>` class per story. Test methods import story
literals from the sibling `-stories.py` file and drive them through hand-authored
given/when/then helpers. Once the file exists the adapter never overwrites it.

Per-epic `<epic-slug>_helper.py` files carry shared given/when/then helpers.
This file's name is the sole snake_case exception to the kebab-case rule (see
Language variation table above for why).

---

## Layer 3: Java Backend

Java splits into `<sub-epic-slug>-stories.java` (spec) and
`<sub-epic-slug>-web.java` (single test file). The spec file follows the same
regeneratable-literal pattern as TypeScript. The test file follows the same
write-once discipline.

Per-epic `<epic-slug>Helper.java` files carry shared given/when/then helpers.

---

## Rules — What Code Backends Must Not Do

- **Never override `translateFrom`** — only `updateSelf`, `childCollections`, and `createChildXxx`.
- **Spec files (`-stories.<ext>`) contain no imports of production code** — imports are limited to type-only imports of the shared `story-types` module. Anything else belongs in a test file.
- **Test files (`-<layer>.<ext>`) always import the spec constants** — the story name, actor, and step text live in exactly one place (the spec file). Never duplicate them in the test file.
- **Test files are write-once** — the render pipeline must never overwrite an existing test file, only scaffold when absent or emit an update advisory when the graph moves.
- **No `HAND-WRITTEN START / END` fences inside spec files** — those are a legacy fixture-preservation mechanism superseded by the physical spec/test split.

---

## Adding a New Code Backend

1. Decide split shape: **spec + test files** (ts/tsx/js/java pattern) or **single test file** (Python pattern).
2. Create `formats/code/{lang}/` with `{lang}_story_map.py` extending `CodeStoryMap`.
3. Override `_render_leaf_file(sub_epic, epic)` to emit the language-specific spec-file body.
4. Override `_hydrate_leaf_sub_epic_from_content(...)` to reverse-parse the spec back into `Story` and `AcceptanceCriteria` records.
5. If the language needs per-epic helper files (Python, Java), override `_render_epic_helper(epic)` and `_epic_helper_path(epic_root, epic)`.
6. Add matching templates under `context_tools/stories/templates/{lang}/`:
   - `{sub-epic-verb-noun}-stories.<ext>` (spec file body)
   - `{sub-epic-verb-noun}-<layer>.<ext>` (test file skeleton) — one per relevant layer.
7. No changes to `CodeStoryMap`, `context_tools/stories/`, or any existing backend.
