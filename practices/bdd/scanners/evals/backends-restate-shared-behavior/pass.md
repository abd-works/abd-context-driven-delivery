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
