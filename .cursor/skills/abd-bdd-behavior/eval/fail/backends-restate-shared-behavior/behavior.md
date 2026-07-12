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
