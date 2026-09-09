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
