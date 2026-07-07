# Artifact Layout — Expanded

The story map hierarchy is expressed as folders on disk. Each lowest-level sub-epic becomes a file; each story inside it becomes a class or section; each scenario becomes a method or subsection. Natural for code (`.py`, `.tsx`, `.java`) and for large docs.

## Folder hierarchy

The folder tree mirrors the story map exactly:

```
stories/
  <epic>/
    story-context.md              ← optional: describes this epic if not fully expanded below
    <sub_epic>/
      ...
        <lowest_sub_epic>/
          <lowest_sub_epic>.<fmt> ← FILE  (named after the lowest-level sub-epic)
```

Non-leaf folders (epics and non-terminal sub-epics) can carry a `story-context.md` describing the node and its children when its children are not yet expanded. Once fully expanded, the folder structure carries the meaning and `story-context.md` becomes optional.

## Output locations

| Artifact | Location |
|---|---|
| Story Map | Implicit in the folder structure; `story-context.md` per non-leaf folder as needed |
| Story Scenarios | `stories/<epic>/.../<lowest_sub_epic>/<lowest_sub_epic>-stories.<fmt>` |
| Story Tests | `tests/<epic>/.../<lowest_sub_epic>/<lowest_sub_epic>-<layer>.<fmt>` |

**Story Scenarios** (`-stories.<fmt>`) are the structured scenario data — the typed interface to the tests (e.g. a TypeScript const file). They declare what the stories do; they contain no test runner code.

**Story Tests** are real test implementations, one file per layer under test. Each file imports from the `-stories.<fmt>` file for the same sub-epic:

- `<lowest_sub_epic>-web.<fmt>` — UI / browser layer tests
- `<lowest_sub_epic>-api.<fmt>` — API / service layer tests
- `<lowest_sub_epic>-e2e.<fmt>` — end-to-end tests

Not every sub-epic will have all three — include only the layers that exist and are meaningful to test independently.

## Who writes which file

Expanded layout is the code case, so the code-path-vs-AI split matters here more than in any other layout. The short version:

| File | Producer | Notes |
|---|---|---|
| `story-context.md` (any level) | AI / human | Prose that describes the node; code path never writes here |
| `<lowest_sub_epic>-stories.<fmt>` | Code path for first render + large re-render; AI for small in-place edits | Must remain round-trippable — the code path must be able to parse it back |
| `<lowest_sub_epic>-<layer>.<fmt>` (tier files) | Code path scaffolds ONCE (empty TODO bodies), AI/human owns all bodies from then on | Write-once; the code path refuses to overwrite existing files |
| `story-types.<fmt>` / `story-runner.<fmt>` (shared) | Code path only, verbatim from `stories/templates/` | AI never edits these |

See `behavior/code-scaffolding-vs-ai-editing.md` for the full decision table and the `stories/cli/` invocations per situation.

## File naming inside a test file

- **File** is named after the **lowest-level sub-epic** plus a layer suffix (`-web`, `-api`, `-e2e`) — never the story
- **Class** is named after the **story**: `Test<ExactStoryName>`
- **Method** is named after the **scenario**: `test_<scenario_outcome_snake_case>`
- Additions go into the existing class; new stories under the same lowest sub-epic get a new class in the same file

Naming the file after the story is the most common mistake — the file always maps to the lowest sub-epic.
