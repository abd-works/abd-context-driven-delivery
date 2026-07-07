---
fidelity: [exploration, specification, engineering]
artifact: [behavior]
section: body
---

# Behavior — Documentation Mode

Documentation mode applies to **expanded layout only** — the layout where the story map
is expressed as folders on disk. It can be applied **during generation** (second pass
immediately after expanding the tree) or **after the fact** (on an existing expanded
tree). Either way, the output is one `story-context.md` at the root of the folder
concerned — or wherever the user says.

---

## When to apply

- User says `--document`, `document this`, or `add documentation` during or after generation
- User points at an existing expanded folder and asks for story-level documentation
- No `story-context.md` exists at the target location yet

---

## What goes in story-context.md

The content scales to what actually exists. Do not document what is not there.
Do not add what the structure does not say.

**To determine what sections to include, read the current fidelity from the folder
first — see `behavior/discovering-current-fidelity.md`.**

| Current fidelity of the folder | What to include in story-context.md |
|---|---|
| Shaping | Story map (folder names only) |
| Discovery | Story map + story names from files |
| Exploration / Specification | Story map + story scenarios |
| Engineering | Story map + story scenarios (tests are code — not documented) |

Thin slices are included whenever they exist, regardless of fidelity level.
Add each section only when there is content to put in it.

---

## Story map

Derive the map from the folder hierarchy and file names. Preserve names verbatim — do not
rename, normalise, or paraphrase.

```
(E) <Epic Verb–Noun>            ← top-level folder name
    (E) <Sub-Epic Verb–Noun>    ← sub-folder name
        (S) Agent --> <Story Verb–Noun>   ← file name or story name from file
```

If a folder has no files yet, the story map entry is sufficient. Mark unspecified stories
as `(stub)`.

---

## Story scenarios

Include this section only when story files contain scenarios (main-flow, inline, outline,
or stub entries with content).

List each story's scenarios verbatim from the file — scenario name, actor, steps. Do not
summarise or rewrite.

---

## Thin slices

Include this section only when thin-slice definitions exist (in a thin-slice file, a
domain-context, or wherever the user has defined them).

Derive slices in dependency order — the sub-epic with no upstream dependencies first.

---

## Output location

| User points at | story-context.md goes at |
|---|---|
| Root of an expanded tree | Root of that tree |
| A specific sub-folder | That sub-folder |
| User names a location explicitly | That location |

One `story-context.md` per invocation. Do not create sub-folder context files unless
the user explicitly asks.

---

## Rules

- Verbatim extraction — never paraphrase story names, scenario names, or step text
- Scale to what exists — only include sections with real content
- Tests are code — do not document test files in story-context.md
- Preserve the hierarchy — do not flatten sub-epics or stories into a single list
- Stubs are valid — a story with no scenarios gets `(stub)`, not an invented scenario
- No invented content — if it is not in the folder, it is not in story-context.md
