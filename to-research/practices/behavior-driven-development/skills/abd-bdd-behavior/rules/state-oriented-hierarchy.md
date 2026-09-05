---
rule: state-oriented-hierarchy
severity: error
---
# State-Oriented Hierarchy

The behavior hierarchy is state-oriented, not operation-oriented. Every non-leaf describe is one of two things — a **subject noun phrase** or a **state elaboration** opened with `with` or `that`. Every leaf is `it should …` — an observation of what is true of the current subject in the state that the enclosing describes have built up.

You never write actions, events, keywords like `when` / `if` / `given`, or method names as describes. You never restate the operation as a leaf (`should add an Epic to a StoryMap`). You never write `the X should …` in a leaf — if `it` would be ambiguous, that is a signal to add a nested describe that names the subject, then observe under it.

## How to read each level

| Line looks like | Role |
|---|---|
| `a Story Map` | Subject — an instance of the thing under discussion |
| `with 4 Epics in sequential order` | State elaboration — narrows the subject to a specific configuration |
| `that has been translated from a source with an added child` | State elaboration in past-participle form — the state was reached via some transformation, but the describe still names the resulting state, not the action |
| `with the first Epic renamed` | State elaboration — the state after a change, expressed as a state, not an event |
| `the first Epic` | Nested subject — switches focus to a sub-element of the current state so the next leaf can use `it` |
| `it should hold 5 Epics` | Observation — a fact that is true in the surrounding state |

## The two core rules

### 1. State form only — never event, action, or keyword form

Every non-leaf describe starts with one of these subject-noun-phrase openers:

- `a`, `an`, `the` — single subject instance (`a Story Map`, `the first Epic`)
- `every`, `each` — universal quantifier over a set of sub-elements (`every Epic element`, `each rendered heading`)
- `its` — possessive that refocuses on a sub-element of the standing subject (`its contents`, `its Epic row`)
- `with` — state elaboration in participle form (`with 4 Epics in sequential order`, `with a fifth Epic appended`)
- `that` — state elaboration in clause form (`that has been translated from a source with an added child`)

If you find yourself writing `when …`, `if …`, `given …`, `<subject> is <verb>ed`, or a bare verb phrase, rewrite it as a state. Bare CamelCase class names (`StoryMap`, `Epic`) are not subject noun phrases either — prefix with an article, or promote to a `##` markdown category heading if the label is organizational rather than a subject.

| Wrong (event / action) | Right (state) |
|---|---|
| `when an Epic is appended to the Story Map` | `with a fifth Epic appended` |
| `an Epic is appended to the Story Map` | `with a fifth Epic appended` |
| `if the source has an added child` | `that has been translated from a source with an added child` |
| `given 4 Epics` | `with 4 Epics in sequential order` |
| `adding a SubEpic to the first Epic` | `with a SubEpic appended to the first Epic` |

The reason: BDD at this fidelity describes what is TRUE of a system in a state, not what the system does. Present-tense narrative events are still events — they name a change rather than a state. The past-participle state form (`with X <ed>`) names the resulting state, which is what the observations below actually observe.

### 2. Every leaf is `it should …` — restructure if `it` would be ambiguous

Leaves never name the subject. If the subject of the observation is the current innermost subject, write `it should …`. If the observation is about a sub-element of the current state, add a nested describe naming that sub-element, then write `it should …` under it.

Wrong:

```
with the first Epic renamed
  the first Epic should carry the new name
  the sequential order of the Epics should not change
```

Right:

```
with the first Epic renamed
  it should preserve the sequential order of the Epics
  the first Epic
    it should carry the new name
```

Here `it should preserve the sequential order …` refers to the Story Map (the standing subject). The observation about the first Epic gets its own nested describe so the following `it` unambiguously refers to the first Epic.

The reason: `it` forces you to make the subject unambiguous through the hierarchy. `the X should …` lets you paper over a broken hierarchy by naming the subject inline, which destroys the state-carrying structure of the describes.

## Direct sentence test

Concatenate the describes and the leaf into one sentence, ignoring the word `it`. It must read as a clear declarative sentence about the standing subject.

- `a Story Map / with 4 Epics in sequential order / with a fifth Epic appended / it should hold 5 Epics` → **A Story Map, with 4 Epics in sequential order, with a fifth Epic appended, should hold 5 Epics.** ✓
- `a Story Map / with 4 Epics in sequential order / with a fifth Epic appended / the last Epic in sequential order / it should be the appended Epic` → **… the last Epic in sequential order should be the appended Epic.** ✓
- `StoryMap / should add an Epic to a StoryMap` → **StoryMap should add an Epic to a StoryMap.** ✗ nonsense
- `with the first Epic renamed / the first Epic should carry the new name` → OK-ish but no `it`; the sub-subject `the first Epic` is not opened as a describe. Rewrite so `it` carries.

## DO

```
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
      it should renumber the remaining Epics
    with the first Epic renamed
      it should preserve the sequential order of the Epics
      the first Epic
        it should carry the new name
    with the first Epic holding 3 SubEpics
      the first Epic
        it should hold 3 SubEpics
      with a SubEpic appended to the first Epic
        the first Epic
          it should hold 4 SubEpics
```

## DO NOT

Class names as describes, operations as leaves, subjects restated in leaves:

```
StoryMap
  should add an Epic to a StoryMap
  should remove an Epic from a StoryMap
  should reorder Epics in a StoryMap
Epic
  should rename an Epic
  should add a SubEpic under an Epic
```

Event / action form in describes:

```
a Story Map
  with 4 Epics
    an Epic is appended to the Story Map
      it should hold 5 Epics
    when the first Epic is removed
      it should hold 3 Epics
```

Subject restated in leaves instead of opening a nested subject describe:

```
with the first Epic renamed
  the first Epic should carry the new name
  the sequential order of the Epics should not change
```

## Reuse comes from state, not from operations

When many implementations share the same operation (e.g., add / remove / rename / reorder across many backends), the shared **state contract** stays the same while the **observed artifacts** differ per backend. This is exactly what the state-oriented shape enables:

```
a Markdown document
  that holds a rendered Story Map with 4 Epics and 3 SubEpics under the first Epic
    it should contain 4 top-level headings
    with the first Epic renamed in the source Story Map and re-rendered
      the first heading
        it should carry the new name

a DrawIO diagram
  that holds a rendered Story Map with 4 Epics and 3 SubEpics under the first Epic
    it should contain 4 Epic mxCells on the Epic row
    with the first Epic renamed in the diagram
      the reconstructed Story Map
        it should carry the new Epic name
```

Same shape, same story, different observations per backend. The operation-oriented style destroys this reuse.

## Examples

- Example (wrong): `StoryMap > should add an Epic to a StoryMap` — describe is a class name, leaf is the operation restated as if the class were the actor
- Example (correct): `a Story Map > with 4 Epics in sequential order > with a fifth Epic appended > it should hold 5 Epics` — describe builds state, elaboration is stated as state (not event), leaf uses `it`
- Example (wrong): `with the first Epic renamed > the first Epic should carry the new name` — subject restated in the leaf instead of opening a nested subject describe
- Example (correct): `with the first Epic renamed > the first Epic > it should carry the new name` — sub-subject is opened as a nested describe, leaf uses `it`
- Example (wrong): `an Epic is appended to the Story Map > it should hold 5 Epics` — event form in the describe
- Example (correct): `with a fifth Epic appended > it should hold 5 Epics` — same meaning expressed as state
