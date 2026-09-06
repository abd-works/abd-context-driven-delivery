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

Code backends (TypeScript, and future language targets) extend the base rendering
contract with two additions:

1. **AST-oriented generation** — `CodeStoryNode` holds a `LanguageAst` by composition.
   Each concrete node type (`SubEpic`, `Story`, `AcceptanceCriteria`) owns its own
   generation method. The pattern mirrors `DrawIOStoryNode.updateSelf` calling into
   `DrawIOElement` — here the node calls into `LanguageAst` instead.

2. **Fixture extraction** — when regenerating an existing `*-stories.ts` file, a
   `TypeScriptFixtureExtractor` reads the file first and separates hand-written exports
   (route constants, example arrays, helper functions) from generated story const blocks.
   Only the generated blocks are replaced; fixtures are preserved verbatim.

Code rendering is **one-directional** — TypeScript files are not read back into the
story graph. There is no `Synchronizer.sync` round-trip; the `{fmt}Synchronizer` slot
is implemented as a no-op stub (or omitted for the first iteration).

The `SubEpic` is the file boundary: each sub-epic produces exactly one `*-stories.ts`
file at `tests/{epic-slug}/{sub-epic-slug}/{sub-epic-slug}-stories.ts`.

---

## Why this shape

**The problem.** Code generation cannot naively overwrite a target file — real `*-stories.ts` files contain hand-authored route constants, example arrays, and helper exports that developers rely on. Regenerating would nuke them. And unlike diagrams, source files are edited *away from* the canonical graph by developers who add hand-written code alongside generated blocks — there is no meaningful "parse back" story, so code sync is one-directional by design.

**The inversion.** Fixture extraction runs **before** `translateFrom` — `TypeScriptFixtureExtractor` reads the existing file first and cleaves it into a fixture zone (preserved verbatim) and a generated zone (replaced). Then `translateFrom` runs against the canonical tree and produces only the generated zone. The output is `fixtures + freshly generated content`. This inverts the usual generate-then-overwrite flow into read-first-then-splice.

**The disciplines.** *`SubEpic` is the file boundary* — one sub-epic maps to exactly one `*-stories.ts`, so there is a bijection between the graph and the file tree; no cross-file generation, no fan-out ambiguity. *AST-oriented via `LanguageAst`* — language details live in a Layer 2 mixin (`CodeStoryNode` + `LanguageAst`) so a new language backend adds a `{lang}Ast` and inherits the four-slot orchestration for free. *No reverse sync* — the `Synchronizer` slot is a deliberate no-op, not an oversight; two-way sync would require round-tripping developer edits and is not part of this mechanism.

---

## File Structure

```
formats/code/
+-- architecture-context.md           <- this file
+-- code_story_node.py                <- CodeStoryNode mixin (holds LanguageAst by composition)
+-- language_ast.py                   <- LanguageAst abstract base (parse, generate, nodeFor)
+-- typescript/
    +-- typescript_story_node.py      <- TypeScriptStoryNode mixin + TypeScriptSubEpic/Story/AC
    +-- typescript_element.py         <- TypeScript source file (path + generated content)
    +-- typescript_story_map.py       <- file tree generation orchestration
    +-- typescript_synchronizer.py    <- fixture extractor + merge (no reverse sync)
```

---

## Layer 2: CodeStoryNode

`CodeStoryNode` is the shared intermediate mixin for all code backends. It holds a
`LanguageAst` by composition and provides the generation entry point.

```
CodeStoryNode  << mixin — extends StoryNode >>
  ast: LanguageAst         ← held by composition; created in concrete constructor

  + updateSelf(source: StoryNode): void
      self.name = source.name
      self.sequential_order = source.sequential_order
      self.ast.update(self)         ← delegates serialization to LanguageAst

## LanguageAst  << abstract >>
  + update(node: StoryNode): void   ← called from CodeStoryNode.updateSelf
  + generate(): str                 ← emit final source text
  + nodeFor(name: str): AstNode     ← look up existing node by name (for fixture extraction)
```

---

## Layer 3: TypeScript Backend

```
TypeScriptStoryNode  << mixin — extends CodeStoryNode >>
  element: TypeScriptElement   ← source file path + content

  + updateSelf(source: StoryNode): void
      super.updateSelf(source)              ← CodeStoryNode writes to ast
      self.element.content = self.ast.generate()

TypeScriptSubEpic(SubEpic, TypeScriptStoryNode)    ← concrete; file boundary
  typeScriptPath() → Path
      tests/{epic-slug}/{sub-epic-slug}/{sub-epic-slug}-stories.ts
  generateTypeScriptFile() → str            ← orchestrates file emit
  createChildStory(source) → TypeScriptStory(source)

TypeScriptStory(Story, TypeScriptStoryNode)        ← concrete; const block boundary
  generateTypeScriptConst() → str           ← emits single const block
  createChildAC(source) → TypeScriptAC(source)

TypeScriptAC(AcceptanceCriteria, TypeScriptStoryNode)  ← concrete
  toStepDicts() → List[StepDict]            ← parses AC text to Gherkin step dicts
```

**AC text → Gherkin step dicts:**
```python
"Given the user is logged in\nWhen they view an invoice\nThen they see the total"
  → [{ "type": "given", "text": "the user is logged in" },
     { "type": "when",  "text": "they view an invoice" },
     { "type": "then",  "text": "they see the total" }]
```

---

## Generation Flow

```
TypeScriptStoryMap.render(story_map)
  for each Epic:
    for each SubEpic:
      dest = sub_epic.typeScriptPath()
      fixtures = TypeScriptFixtureExtractor.extractFrom(dest)    ← if file exists
      sub_epic.translateFrom(canonical_sub_epic)                 ← runs four-step algorithm
      content = sub_epic.generateTypeScriptFile()
      write(dest, fixtures.lines + content)
```

**What `translateFrom` does for `TypeScriptSubEpic`:**
- Step 2 (`updateSelf`) → writes slug, name into AST.
- Step 3 (`childCollections`) → reconciles `TypeScriptStory` children.
- Each `TypeScriptStory.updateSelf` writes its name and AC steps into the story const.
- At the end of the loop, `generateTypeScriptFile()` assembles the full file.

---

## Fixture Extraction

`TypeScriptFixtureExtractor` separates an existing `*-stories.ts` file into two zones:

| Zone | What it contains | Action |
| --- | --- | --- |
| **Fixture zone** | Imports, route constants (`export const INVOICE_ROUTE`), example arrays, helper exports | Preserved verbatim; emitted at top of new file |
| **Generated zone** | `export const SCREAMING_SNAKE_STORY = { … }` blocks matching story slug pattern | Replaced by freshly generated content |

The current implementation uses brace-counting (not a TypeScript AST). This is a known
gap (see Violations). The target is a `TypeScriptAst`-backed extractor using a
lightweight parser (`ts-morph` or `acorn`) for reliable nested-brace handling.

**Walkthrough — regenerating `review-past-invoices-stories.ts`:**

1. File already contains:
   ```typescript
   export const INVOICE_ROUTE = '/billing/invoices'
   export const VIEW_INVOICE_TOTAL = { name: 'View Invoice Total', steps: […] }
   ```
2. `extractFrom(dest)` → fixture lines = `[export const INVOICE_ROUTE …]`;
   generated lines = `[export const VIEW_INVOICE_TOTAL …]` (matches slug pattern).
3. `translateFrom` rebuilds `TypeScriptStory("View Invoice Total")` with updated steps.
4. `generateTypeScriptFile()` emits new story const.
5. Output = preserved `INVOICE_ROUTE` line + new `VIEW_INVOICE_TOTAL` block.

---

## Violations (Known Gaps)

| # | Location | Violation | Severity | Resolution |
| --- | --- | --- | --- | --- |
| V-08 | `generate-domain-stories.py`, `generate-stories.py` | Code scaffolding is standalone outside `story_graph_ops`; nodes do not own their own TypeScript generation methods | High | Introduce `CodeStoryNode` and `TypeScriptStoryNode` mixins; move generation into `SubEpic.generateTypeScriptFile()`, `Story.generateTypeScriptConst()`, `AC.toStepDicts()` |
| V-09 | `extract_fixture_lines()` | Fixture extraction uses brace-counting and regex, not a structural parser; brittle against nested braces and template literals | Medium | Replace with `TypeScriptFixtureExtractor` backed by a lightweight AST parser |

---

## Rules — What Code Backends Must Not Do

- **Never override `translateFrom`** — only `updateSelf` and `childCollections`.
- **`TypeScriptStoryNode.updateSelf` must call `super.updateSelf(source)` first** — so `CodeStoryNode` writes to the AST before the element is serialized.
- **Fixture extraction must run before `translateFrom`** — reading the existing file after writing would lose fixtures.
- **The `Synchronizer` slot does not implement reverse sync** — code backends are one-directional; stub or no-op is correct.

---

## Adding a New Code Backend

1. Create `formats/code/{lang}/` with the four slots (stub `{lang}Synchronizer` as no-op).
2. Create `{lang}Ast` implementing `LanguageAst.update`, `generate`, and `nodeFor`.
3. Create `{lang}StoryNode` mixin: holds `{lang}Element`; `updateSelf` calls `super` then writes element.
4. Create concrete node classes inheriting from both the domain type and `{lang}StoryNode`.
5. Implement `{lang}StoryMap.render` (calls `translateFrom`).
6. No changes to `CodeStoryNode`, `LanguageAst`, `core/`, or any existing backend.
